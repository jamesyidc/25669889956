#!/usr/bin/env python3
"""
Coin Change Tracker Collector - 币种涨跌变化追踪采集器
实时采集27个币种的价格变化并写入JSONL
"""
import sys
sys.path.insert(0, '/home/user/webapp/source_code')

import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pytz

# 配置
DATA_DIR = Path('/home/user/webapp/data/coin_change_tracker')
BASELINE_DIR = DATA_DIR
DATA_DIR.mkdir(parents=True, exist_ok=True)

BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# 27个追踪的币种
SYMBOLS = [
    'BTC', 'ETH', 'BNB', 'XRP', 'DOGE', 
    'SOL', 'DOT', 'MATIC', 'LTC', 'LINK',
    'HBAR', 'TAO', 'CFX', 'TRX', 'TON',
    'NEAR', 'LDO', 'CRO', 'ETC', 'XLM',
    'BCH', 'UNI', 'SUI', 'FIL', 'STX',
    'CRV', 'AAVE', 'APT'
]


def get_daily_open_prices():
    """从OKX获取今日开盘价（日线开盘价）"""
    try:
        open_prices = {}
        for symbol in SYMBOLS:
            try:
                # 优先使用永续合约，如果失败则使用现货
                # 永续合约后缀：-USDT-SWAP
                url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}-USDT-SWAP&bar=1D&limit=1"
                response = requests.get(url, timeout=5)
                data = response.json()
                
                # 如果永续合约失败，尝试现货
                if data.get('code') != '0' or not data.get('data'):
                    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}-USDT&bar=1D&limit=1"
                    response = requests.get(url, timeout=5)
                    data = response.json()
                
                if data.get('code') == '0' and data.get('data'):
                    # 日线数据格式: [时间戳, 开盘价, 最高价, 最低价, 收盘价, ...]
                    candle = data['data'][0]
                    open_price = float(candle[1])  # 开盘价
                    open_prices[symbol] = open_price
                    print(f"[开盘价] {symbol}: {open_price}")
                else:
                    print(f"[警告] {symbol} 开盘价获取失败")
                    
                time.sleep(0.1)  # 避免请求过快
                
            except Exception as e:
                print(f"[错误] {symbol} 获取开盘价失败: {e}")
                continue
                
        return open_prices
        
    except Exception as e:
        print(f"[错误] 获取开盘价失败: {e}")
        return {}


def get_current_prices():
    """从OKX获取当前价格"""
    try:
        prices = {}
        for symbol in SYMBOLS:
            try:
                # 优先使用永续合约，如果失败则使用现货
                url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}-USDT-SWAP"
                response = requests.get(url, timeout=5)
                data = response.json()
                
                # 如果永续合约失败，尝试现货
                if data.get('code') != '0' or not data.get('data'):
                    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}-USDT"
                    response = requests.get(url, timeout=5)
                    data = response.json()
                
                if data.get('code') == '0' and data.get('data'):
                    price = float(data['data'][0]['last'])
                    prices[symbol] = price
                    print(f"[价格] {symbol}: {price}")
                else:
                    print(f"[警告] {symbol} 价格获取失败")
                    
                time.sleep(0.1)  # 避免请求过快
                
            except Exception as e:
                print(f"[错误] {symbol} 获取价格失败: {e}")
                continue
                
        return prices
        
    except Exception as e:
        print(f"[错误] 获取价格失败: {e}")
        return {}


def load_baseline():
    """加载基准价格"""
    today = datetime.now(BEIJING_TZ).strftime('%Y%m%d')
    baseline_file = BASELINE_DIR / f"baseline_{today}.json"
    
    if baseline_file.exists():
        try:
            with open(baseline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[错误] 加载基准价格失败: {e}")
    
    return {}


def save_baseline(prices):
    """保存基准价格"""
    today = datetime.now(BEIJING_TZ).strftime('%Y%m%d')
    baseline_file = BASELINE_DIR / f"baseline_{today}.json"
    
    try:
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(prices, f, indent=2, ensure_ascii=False)
        print(f"[保存] 基准价格已保存到 {baseline_file}")
    except Exception as e:
        print(f"[错误] 保存基准价格失败: {e}")


def calculate_changes(current_prices, baseline_prices):
    """计算涨跌幅"""
    changes = {}
    
    for symbol in SYMBOLS:
        if symbol in current_prices and symbol in baseline_prices:
            current = current_prices[symbol]
            baseline = baseline_prices[symbol]
            
            if baseline > 0:
                change_pct = ((current - baseline) / baseline) * 100
                changes[symbol] = {
                    'current_price': current,
                    'baseline_price': baseline,
                    'change_pct': round(change_pct, 2)
                }
    
    return changes


def save_to_jsonl(data):
    """保存数据到JSONL"""
    today = datetime.now(BEIJING_TZ).strftime('%Y%m%d')
    jsonl_file = DATA_DIR / f"coin_change_{today}.jsonl"
    
    try:
        with open(jsonl_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        print(f"[保存] 数据已写入 {jsonl_file}")
    except Exception as e:
        print(f"[错误] 保存JSONL失败: {e}")


def main():
    """主循环"""
    print("=" * 60)
    print("币种涨跌变化追踪采集器启动")
    print("=" * 60)
    
    # 加载或初始化基准价格
    baseline_prices = load_baseline()
    last_baseline_date = None
    
    # 如果没有基准价格，或者是新的一天，获取今日开盘价
    today = datetime.now(BEIJING_TZ).strftime('%Y%m%d')
    
    if not baseline_prices:
        print("[初始化] 获取今日开盘价作为基准...")
        baseline_prices = get_daily_open_prices()
        if baseline_prices:
            save_baseline(baseline_prices)
            last_baseline_date = today
    else:
        last_baseline_date = today
    
    while True:
        try:
            now = datetime.now(BEIJING_TZ)
            current_date = now.strftime('%Y%m%d')
            
            # 检查是否是新的一天，如果是则重置基准价格
            if current_date != last_baseline_date:
                print(f"\n[新的一天] {current_date} - 重置基准价格...")
                baseline_prices = get_daily_open_prices()
                if baseline_prices:
                    save_baseline(baseline_prices)
                    last_baseline_date = current_date
            
            print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] 开始采集...")
            
            # 获取当前价格
            current_prices = get_current_prices()
            
            if current_prices:
                # 计算涨跌幅
                changes = calculate_changes(current_prices, baseline_prices)
                
                # 计算总和
                total_change = sum(item['change_pct'] for item in changes.values())
                
                # 计算上涨占比
                up_coins = sum(1 for item in changes.values() if item['change_pct'] > 0)
                total_coins = len(changes)
                up_ratio = (up_coins / total_coins * 100) if total_coins > 0 else 0
                
                # 构建数据记录
                record = {
                    'timestamp': int(time.time() * 1000),
                    'beijing_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'cumulative_pct': round(total_change, 2),  # 使用cumulative_pct字段名
                    'total_change': round(total_change, 2),     # 保留兼容性
                    'up_ratio': round(up_ratio, 1),            # 上涨占比 (%)
                    'up_coins': up_coins,                      # 上涨币种数
                    'down_coins': total_coins - up_coins,      # 下跌币种数
                    'changes': changes,
                    'count': len(changes)
                }
                
                # 保存到JSONL
                save_to_jsonl(record)
                
                print(f"[统计] 总涨跌幅: {total_change:.2f}%, 币种数: {len(changes)}, 上涨占比: {up_ratio:.1f}% ({up_coins}↑/{total_coins - up_coins}↓)")
            
            # 每1分钟采集一次
            print(f"[等待] 下次采集时间: {(now + timedelta(minutes=1)).strftime('%H:%M:%S')}")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n[退出] 采集器已停止")
            break
        except Exception as e:
            print(f"[错误] 采集失败: {e}")
            time.sleep(60)


if __name__ == '__main__':
    main()
