#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
见底信号自动做多监控器
监控市场情绪见底信号，当满足条件时自动开多单

策略1: 见底信号 + RSI<800 + 涨幅前8 → 做多
策略2: 见底信号 + RSI<800 + 涨幅后8 → 做多

每份账户可用余额的1.5%，开8份，每份限额5U（可配置）
10倍杠杆

JSONL执行许可机制：
- 每个账户每个策略有独立的execution.jsonl文件
- 开关开启时，写入allowed=true到文件头
- 执行后，写入allowed=false，并记录执行详情
- 防止重复触发
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录
BASE_DIR = Path('/home/user/webapp')
sys.path.insert(0, str(BASE_DIR))

# 数据目录
DATA_DIR = BASE_DIR / 'data' / 'okx_auto_strategy'
CONFIG_DIR = BASE_DIR / 'data' / 'okx_bottom_signal_long'

# API基础URL
API_BASE = 'http://localhost:9002'

# 配置
CHECK_INTERVAL = 60  # 检查间隔（秒）= 1分钟
COOLDOWN_TIME = 3600  # 冷却时间（秒）= 1小时，防止重复触发

# Telegram配置
TELEGRAM_BOT_TOKEN = "8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0"
TELEGRAM_CHAT_ID = "-1003227444260"

# 策略配置（默认值，会从API读取用户配置）
STRATEGY_CONFIG = {
    'top8_long': {
        'name': '见底信号+前8做多',
        'enabled_key': 'bottom_signal_top8_long_enabled',
        'coin_selection': 'top8',  # 涨幅前8
        'default_rsi_threshold': 800,
        'balance_percent': 0.015,  # 1.5%
        'num_coins': 8,
        'default_max_per_coin': 5.0,  # 每份默认最大5U
        'leverage': 10  # 10倍杠杆
    },
    'bottom8_long': {
        'name': '见底信号+后8做多',
        'enabled_key': 'bottom_signal_bottom8_long_enabled',
        'coin_selection': 'bottom8',  # 涨幅后8
        'default_rsi_threshold': 800,
        'balance_percent': 0.015,  # 1.5%
        'num_coins': 8,
        'default_max_per_coin': 5.0,  # 每份默认最大5U
        'leverage': 10  # 10倍杠杆
    }
}

# 存储上次触发时间（防止重复）
last_trigger_times = {
    'top8_long': {},
    'bottom8_long': {}
}


def log(message):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)


def get_execution_file_path(account_id, strategy_key):
    """获取执行许可文件路径（按日期保存）"""
    # 获取当前日期
    date_str = datetime.now().strftime('%Y%m%d')
    # top8_long -> bottom_signal_top8_long_execution_20260221.jsonl
    # bottom8_long -> bottom_signal_bottom8_long_execution_20260221.jsonl
    filename = f"{account_id}_bottom_signal_{strategy_key}_execution_{date_str}.jsonl"
    return DATA_DIR / filename


def get_latest_execution_file(account_id, strategy_key):
    """获取最新的执行文件（用于读取allowed状态）"""
    # 查找最近3天的文件
    for days_ago in range(3):
        date = datetime.now() - timedelta(days=days_ago)
        date_str = date.strftime('%Y%m%d')
        filename = f"{account_id}_bottom_signal_{strategy_key}_execution_{date_str}.jsonl"
        file_path = DATA_DIR / filename
        if file_path.exists():
            return file_path
    return None


def check_allowed_execution(account_id, strategy_key):
    """检查是否允许执行（从今日JSONL文件头读取，如不存在则查找最近文件）"""
    # 先检查今天的文件
    execution_file = get_execution_file_path(account_id, strategy_key)
    
    if not execution_file.exists():
        # 今天的文件不存在，查找最近的文件
        latest_file = get_latest_execution_file(account_id, strategy_key)
        if latest_file:
            # 从最近的文件读取状态
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line:
                        record = json.loads(first_line)
                        allowed = record.get('allowed', False)
                        log(f"📖 [{account_id}] 从历史文件读取allowed={allowed}: {strategy_key}")
                        return allowed
            except Exception as e:
                log(f"❌ [{account_id}] 读取历史文件失败: {e}")
        
        # 没有历史文件，创建新文件并允许执行
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(execution_file, 'w', encoding='utf-8') as f:
                record = {
                    'allowed': True,
                    'timestamp': datetime.now().isoformat(),
                    'reason': '初始化，允许执行'
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            log(f"✅ [{account_id}] 创建今日执行许可文件: {strategy_key}")
            return True
        except Exception as e:
            log(f"❌ [{account_id}] 创建执行许可文件失败: {e}")
            return False
    
    # 今天的文件存在，读取
    try:
        with open(execution_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line:
                record = json.loads(first_line)
                allowed = record.get('allowed', False)
                return allowed
    except Exception as e:
        log(f"❌ [{account_id}] 读取执行许可失败: {e}")
    
    return False


def set_allowed_execution(account_id, strategy_key, allowed, reason='', rsi_value=None, coins=None, result=None):
    """设置执行许可（更新JSONL文件头）"""
    execution_file = get_execution_file_path(account_id, strategy_key)
    
    try:
        # 读取现有记录（除了第一行）
        existing_records = []
        if execution_file.exists():
            with open(execution_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    existing_records = lines[1:]  # 跳过第一行
        
        # 写入新的文件头
        with open(execution_file, 'w', encoding='utf-8') as f:
            header = {
                'allowed': allowed,
                'timestamp': datetime.now().isoformat(),
                'reason': reason
            }
            
            if rsi_value is not None:
                header['rsi_value'] = rsi_value
            
            if coins:
                header['coins'] = coins
            
            if result:
                header['result'] = result
            
            f.write(json.dumps(header, ensure_ascii=False) + '\n')
            
            # 写回其他记录
            for line in existing_records:
                f.write(line)
        
        log(f"✅ [{account_id}] 执行许可已更新: {strategy_key} = {allowed}")
        return True
    except Exception as e:
        log(f"❌ [{account_id}] 更新执行许可失败: {e}")
        return False


def record_execution(account_id, strategy_key, coins, total_amount, amount_per_coin, success_count, failed_count, success_coins, failed_coins):
    """记录执行详情（追加到JSONL文件）"""
    execution_file = get_execution_file_path(account_id, strategy_key)
    
    try:
        with open(execution_file, 'a', encoding='utf-8') as f:
            record = {
                'timestamp': datetime.now().isoformat(),
                'account_id': account_id,
                'strategy_key': strategy_key,
                'coins': coins,
                'total_amount': total_amount,
                'amount_per_coin': amount_per_coin,
                'success_count': success_count,
                'failed_count': failed_count,
                'success_coins': success_coins,
                'failed_coins': failed_coins
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        log(f"✅ [{account_id}] 执行记录已保存: {strategy_key}")
        return True
    except Exception as e:
        log(f"❌ [{account_id}] 保存执行记录失败: {e}")
        return False


def send_telegram(message):
    """发送Telegram通知"""
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        response = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=10)
        return response.status_code == 200
    except Exception as e:
        log(f"❌ Telegram通知失败: {str(e)}")
        return False


def get_accounts():
    """获取所有账户列表"""
    try:
        response = requests.get(f"{API_BASE}/api/okx-accounts/list-with-credentials", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            return result.get('accounts', [])
        return []
    except Exception as e:
        log(f"❌ 获取账户列表异常: {str(e)}")
        return []


def get_tpsl_settings(account_id):
    """获取账户的策略设置"""
    try:
        response = requests.get(f"{API_BASE}/api/okx-trading/tpsl-settings/{account_id}", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            return result.get('settings', {})
        return {}
    except Exception as e:
        log(f"❌ 获取账户 {account_id} 设置异常: {str(e)}")
        return {}


def get_strategy_config(account_id, strategy_key):
    """获取策略配置（从API）"""
    try:
        # top8_long or bottom8_long
        endpoint = f"/api/okx-trading/bottom-signal-long-{strategy_key.replace('_long', '')}/{account_id}"
        response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success') and result.get('config'):
            config = result['config']
            return {
                'enabled': config.get('enabled', False),
                'rsi_threshold': config.get('rsi_threshold', 800),
                'max_per_coin': config.get('max_order_size', 5.0),
                'position_size_percent': config.get('position_size_percent', 1.5),
                'leverage': config.get('leverage', 10)
            }
        return None
    except Exception as e:
        log(f"❌ 获取账户 {account_id} 策略配置异常: {str(e)}")
        return None


def check_market_sentiment():
    """检查市场情绪是否出现见底信号"""
    try:
        response = requests.get(f"{API_BASE}/api/market-sentiment/latest", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success') and result.get('data'):
            data = result['data']
            if isinstance(data, list) and len(data) > 0:
                sentiment = data[0].get('sentiment', '')
            else:
                sentiment = data.get('sentiment', '')
            
            # 检查是否为见底信号或底部背离
            is_bottom = '见底信号' in sentiment or '底部背离' in sentiment
            return is_bottom, sentiment
        return False, None
    except Exception as e:
        log(f"❌ 检查市场情绪异常: {str(e)}")
        return False, None


def get_rsi_sum():
    """获取RSI总和"""
    try:
        # 这里应该调用实际的RSI API
        # 暂时返回模拟值
        # TODO: 实现真实的RSI API调用
        response = requests.get(f"{API_BASE}/api/rsi/latest", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            return result.get('rsi_sum', 0)
        return 0
    except Exception as e:
        log(f"⚠️ 获取RSI总和异常（使用默认值0）: {str(e)}")
        return 0


def get_coin_changes():
    """获取币种涨跌幅数据"""
    try:
        response = requests.get(f"{API_BASE}/api/coin-change-tracker/latest", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success') and result.get('data'):
            return result['data']
        return []
    except Exception as e:
        log(f"❌ 获取币种涨跌幅异常: {str(e)}")
        return []


def select_coins(coin_changes, strategy_key, num_coins=8):
    """选择币种（前8或后8）"""
    if not coin_changes:
        return []
    
    # 按24小时涨跌幅排序
    sorted_coins = sorted(coin_changes, key=lambda x: x.get('change_24h', 0), reverse=True)
    
    if 'top8' in strategy_key:
        # 涨幅前8
        selected = sorted_coins[:num_coins]
    else:
        # 涨幅后8
        selected = sorted_coins[-num_coins:]
    
    return [coin.get('symbol', '') for coin in selected]


def execute_long_order(account, symbol, amount_usdt, leverage=10):
    """执行开多单"""
    try:
        # 调用开仓API
        response = requests.post(f"{API_BASE}/api/okx-trading/place-order", json={
            'account_id': account['id'],
            'symbol': symbol,
            'side': 'buy',  # 做多
            'posSide': 'long',
            'amount_usdt': amount_usdt,
            'leverage': leverage,
            'orderType': 'market'
        }, timeout=30)
        
        response.raise_for_status()
        result = response.json()
        
        return result.get('success', False), result
    except Exception as e:
        log(f"❌ [{account['id']}] 开仓失败 {symbol}: {str(e)}")
        return False, {'error': str(e)}


def execute_strategy(account, strategy_key, config, sentiment, rsi_sum):
    """执行策略"""
    account_id = account['id']
    account_name = account.get('name', account_id)
    strategy_name = STRATEGY_CONFIG[strategy_key]['name']
    
    log(f"🎯 [{account_name}] 开始执行策略: {strategy_name}")
    
    # 1. 检查执行许可
    if not check_allowed_execution(account_id, strategy_key):
        log(f"🔒 [{account_name}] 执行许可为false，跳过执行")
        return False
    
    # 2. 获取币种涨跌幅数据
    coin_changes = get_coin_changes()
    if not coin_changes:
        log(f"❌ [{account_name}] 无法获取币种涨跌幅数据")
        return False
    
    # 3. 选择币种
    num_coins = STRATEGY_CONFIG[strategy_key]['num_coins']
    selected_coins = select_coins(coin_changes, strategy_key, num_coins)
    
    if not selected_coins:
        log(f"❌ [{account_name}] 无法选择币种")
        return False
    
    log(f"📊 [{account_name}] 选中币种: {', '.join(selected_coins)}")
    
    # 4. 计算每个币种的开仓金额
    try:
        available_balance = float(account.get('balance', 0))
    except:
        available_balance = 0
    
    if available_balance <= 0:
        log(f"❌ [{account_name}] 可用余额不足")
        return False
    
    # 总投入 = 可用余额 * position_size_percent%
    position_size_percent = config.get('position_size_percent', 1.5) / 100
    total_amount = available_balance * position_size_percent
    
    # 每个币种的金额
    amount_per_coin = total_amount / num_coins
    
    # 限制单币最大金额
    max_per_coin = config.get('max_per_coin', 5.0)
    if amount_per_coin > max_per_coin:
        amount_per_coin = max_per_coin
        total_amount = amount_per_coin * num_coins
    
    log(f"💰 [{account_name}] 总投入: {total_amount:.2f} USDT, 每币: {amount_per_coin:.2f} USDT")
    
    # 5. 执行开仓
    leverage = config.get('leverage', 10)
    success_count = 0
    failed_count = 0
    success_coins = []
    failed_coins = []
    
    for symbol in selected_coins:
        success, result = execute_long_order(account, symbol, amount_per_coin, leverage)
        if success:
            success_count += 1
            success_coins.append(symbol)
            log(f"✅ [{account_name}] 开仓成功: {symbol} {amount_per_coin:.2f}U {leverage}x")
        else:
            failed_count += 1
            failed_coins.append(symbol)
            log(f"❌ [{account_name}] 开仓失败: {symbol}")
    
    # 6. 更新执行许可（设为false）
    set_allowed_execution(
        account_id, 
        strategy_key, 
        allowed=False,
        reason=f'策略已执行 - 成功{success_count}个，失败{failed_count}个',
        rsi_value=rsi_sum,
        coins=selected_coins,
        result={'success': success_count, 'failed': failed_count}
    )
    
    # 7. 记录执行详情
    record_execution(
        account_id,
        strategy_key,
        selected_coins,
        total_amount,
        amount_per_coin,
        success_count,
        failed_count,
        success_coins,
        failed_coins
    )
    
    # 8. 发送Telegram通知
    telegram_msg = f"""
🚀 <b>见底信号做多策略执行</b>

👤 账户: {account_name}
📈 策略: {strategy_name}
📊 市场情绪: {sentiment}
📉 RSI总和: {rsi_sum}

💰 总投入: {total_amount:.2f} USDT
🔢 币种数: {num_coins}个
💵 每币: {amount_per_coin:.2f} USDT
📊 杠杆: {leverage}x

✅ 成功: {success_count}个
{', '.join(success_coins) if success_coins else '无'}

❌ 失败: {failed_count}个
{', '.join(failed_coins) if failed_coins else '无'}

⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()
    
    send_telegram(telegram_msg)
    
    log(f"✅ [{account_name}] 策略执行完成: 成功{success_count}个，失败{failed_count}个")
    return True


def monitor_loop():
    """主监控循环"""
    log("=" * 60)
    log("🚀 见底信号做多监控器启动")
    log(f"📊 检查间隔: {CHECK_INTERVAL}秒")
    log(f"⏰ 冷却时间: {COOLDOWN_TIME}秒")
    log("=" * 60)
    
    while True:
        try:
            log("🔍 开始检查...")
            
            # 1. 检查市场情绪
            is_bottom_signal, sentiment = check_market_sentiment()
            if not is_bottom_signal:
                log(f"⏸️ 未出现见底信号，当前: {sentiment}")
                time.sleep(CHECK_INTERVAL)
                continue
            
            log(f"✅ 检测到见底信号: {sentiment}")
            
            # 2. 获取RSI总和
            rsi_sum = get_rsi_sum()
            log(f"📈 当前RSI总和: {rsi_sum}")
            
            # 3. 获取所有账户
            accounts = get_accounts()
            if not accounts:
                log("⚠️ 没有可用账户")
                time.sleep(CHECK_INTERVAL)
                continue
            
            log(f"👥 找到 {len(accounts)} 个账户")
            
            # 4. 遍历每个账户，检查每个策略
            for account in accounts:
                account_id = account['id']
                account_name = account.get('name', account_id)
                
                # 检查两个策略
                for strategy_key in ['top8_long', 'bottom8_long']:
                    try:
                        # 获取策略配置
                        config = get_strategy_config(account_id, strategy_key)
                        
                        if not config:
                            continue
                        
                        # 检查策略是否启用
                        if not config.get('enabled', False):
                            continue
                        
                        # 检查RSI阈值
                        rsi_threshold = config.get('rsi_threshold', 800)
                        if rsi_sum >= rsi_threshold:
                            log(f"⏸️ [{account_name}] RSI {rsi_sum} >= {rsi_threshold}，不满足条件")
                            continue
                        
                        log(f"🎯 [{account_name}] 满足条件，准备执行 {STRATEGY_CONFIG[strategy_key]['name']}")
                        
                        # 执行策略
                        execute_strategy(account, strategy_key, config, sentiment, rsi_sum)
                        
                    except Exception as e:
                        log(f"❌ [{account_name}] 策略 {strategy_key} 执行异常: {str(e)}")
            
            log(f"✅ 本轮检查完成，等待 {CHECK_INTERVAL} 秒...")
            
        except KeyboardInterrupt:
            log("👋 收到中断信号，退出...")
            break
        except Exception as e:
            log(f"❌ 监控循环异常: {str(e)}")
        
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    try:
        monitor_loop()
    except KeyboardInterrupt:
        log("👋 程序退出")
    except Exception as e:
        log(f"❌ 程序异常退出: {str(e)}")
        sys.exit(1)
