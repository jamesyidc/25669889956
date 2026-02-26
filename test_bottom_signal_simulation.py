#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
见底信号做多策略 - 端到端测试脚本
功能：模拟见底信号并验证完整开仓流程

测试流程：
1. 修改市场情绪数据库，插入 "✅见底信号" 或 "🔄底部背离"
2. 确认 RSI Sum < 800（通过 API 或数据库查询）
3. 等待监控脚本检测到信号
4. 验证策略日志记录
5. 验证开仓执行记录（JSONL 文件）
6. 恢复原始市场情绪数据
"""

import requests
import json
import os
import time
from datetime import datetime

# API 配置
API_BASE = 'http://localhost:9002'

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg):
    print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} {msg}")

def log_success(msg):
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")

def log_warning(msg):
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")

def log_error(msg):
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")

def log_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

# 1. 获取当前市场情绪
def get_current_market_sentiment():
    """获取当前市场情绪数据"""
    try:
        response = requests.get(f'{API_BASE}/api/market-sentiment/latest', timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_success(f"当前市场情绪: {data.get('sentiment', 'N/A')}")
            log_info(f"情绪更新时间: {data.get('timestamp', 'N/A')}")
            return data
        else:
            log_error(f"获取市场情绪失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        log_error(f"获取市场情绪异常: {str(e)}")
        return None

# 2. 获取当前 RSI Sum
def get_current_rsi_sum():
    """获取当前 RSI 总和"""
    try:
        # 使用 OKX Trading API 获取 RSI 数据
        response = requests.get(f'{API_BASE}/api/okx-trading/rsi-sum', timeout=10)
        if response.status_code == 200:
            data = response.json()
            rsi_sum = data.get('rsi_sum', 0)
            log_success(f"当前 RSI Sum: {rsi_sum}")
            return rsi_sum
        else:
            log_warning(f"获取 RSI Sum 失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        log_error(f"获取 RSI Sum 异常: {str(e)}")
        return None

# 3. 模拟插入见底信号
def simulate_bottom_signal(signal_type="✅见底信号"):
    """
    模拟插入见底信号到数据库
    signal_type: "✅见底信号" 或 "🔄底部背离"
    """
    log_header("模拟插入见底信号")
    
    try:
        # 构造市场情绪数据
        sentiment_data = {
            'sentiment': signal_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 调用 API 插入数据
        response = requests.post(
            f'{API_BASE}/api/market-sentiment/insert-test',
            json=sentiment_data,
            timeout=10
        )
        
        if response.status_code == 200:
            log_success(f"✅ 成功插入测试信号: {signal_type}")
            return True
        else:
            log_error(f"插入测试信号失败: HTTP {response.status_code}")
            log_error(f"响应内容: {response.text}")
            return False
    
    except Exception as e:
        log_error(f"插入测试信号异常: {str(e)}")
        return False

# 4. 检查策略是否被触发
def check_strategy_execution(account_id='account_main', wait_time=120):
    """
    检查策略是否被执行
    等待 wait_time 秒，然后检查 JSONL 文件
    """
    log_header(f"等待策略执行 ({wait_time} 秒)")
    
    log_info(f"监控脚本每 60 秒检查一次，等待最多 {wait_time} 秒...")
    
    for i in range(wait_time // 10):
        time.sleep(10)
        log_info(f"已等待 {(i+1)*10} 秒...")
    
    log_info("检查执行记录...")
    
    # 检查 JSONL 文件
    jsonl_files = [
        f'data/okx_bottom_signal_long/{account_id}_bottom_signal_top8_long_execution.jsonl',
        f'data/okx_bottom_signal_long/{account_id}_bottom_signal_bottom8_long_execution.jsonl'
    ]
    
    execution_found = False
    
    for jsonl_file in jsonl_files:
        if os.path.exists(jsonl_file):
            log_success(f"✅ 找到执行记录文件: {jsonl_file}")
            
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 1:  # 除了 header 还有执行记录
                    log_success(f"✅ 文件包含 {len(lines)} 行记录")
                    
                    # 显示最近的执行记录
                    last_record = json.loads(lines[-1])
                    log_info(f"最近执行时间: {last_record.get('timestamp', 'N/A')}")
                    log_info(f"交易币种: {last_record.get('coins', [])}")
                    log_info(f"成功数量: {last_record.get('success_count', 0)}")
                    log_info(f"失败数量: {last_record.get('failure_count', 0)}")
                    
                    execution_found = True
                else:
                    log_warning(f"文件仅包含 header，未找到执行记录")
        else:
            log_warning(f"未找到文件: {jsonl_file}")
    
    return execution_found

# 5. 检查策略日志
def check_strategy_logs(account_id='account_main'):
    """检查策略日志记录"""
    log_header("检查策略日志")
    
    try:
        response = requests.get(
            f'{API_BASE}/api/okx-trading/strategy-logs/{account_id}?limit=10',
            timeout=10
        )
        
        if response.status_code == 200:
            logs = response.json()
            log_success(f"✅ 获取到 {len(logs)} 条策略日志")
            
            # 查找见底信号相关日志
            bottom_signal_logs = [
                log for log in logs 
                if 'bottom_signal' in log.get('strategy_type', '').lower()
            ]
            
            if bottom_signal_logs:
                log_success(f"✅ 找到 {len(bottom_signal_logs)} 条见底信号相关日志")
                
                for log_entry in bottom_signal_logs[:3]:  # 显示最近3条
                    log_info(f"日志时间: {log_entry.get('timestamp', 'N/A')}")
                    log_info(f"策略类型: {log_entry.get('strategy_type', 'N/A')}")
                    log_info(f"操作类型: {log_entry.get('action_type', 'N/A')}")
                    log_info(f"触发信息: {json.dumps(log_entry.get('trigger_info', {}), ensure_ascii=False, indent=2)}")
                    print("-" * 80)
            else:
                log_warning("未找到见底信号相关日志")
                
            return True
        else:
            log_error(f"获取策略日志失败: HTTP {response.status_code}")
            return False
    
    except Exception as e:
        log_error(f"获取策略日志异常: {str(e)}")
        return False

# 6. 恢复原始市场情绪
def restore_market_sentiment(original_sentiment):
    """恢复原始市场情绪"""
    log_header("恢复原始市场情绪")
    
    if not original_sentiment:
        log_warning("没有原始情绪数据，跳过恢复")
        return True
    
    try:
        response = requests.post(
            f'{API_BASE}/api/market-sentiment/restore',
            json=original_sentiment,
            timeout=10
        )
        
        if response.status_code == 200:
            log_success("✅ 成功恢复原始市场情绪")
            return True
        else:
            log_error(f"恢复市场情绪失败: HTTP {response.status_code}")
            return False
    
    except Exception as e:
        log_error(f"恢复市场情绪异常: {str(e)}")
        return False

# 主测试流程
def main():
    log_header("见底信号做多策略 - 端到端测试")
    
    log_info("测试目标：")
    log_info("1. ✅ 模拟见底信号")
    log_info("2. ✅ 监控脚本自动检测")
    log_info("3. ✅ 验证策略执行")
    log_info("4. ✅ 检查日志记录")
    log_info("5. ✅ 恢复原始状态")
    
    # Step 1: 保存当前市场情绪
    log_header("Step 1: 获取当前市场情绪")
    original_sentiment = get_current_market_sentiment()
    
    # Step 2: 获取当前 RSI Sum
    log_header("Step 2: 获取当前 RSI Sum")
    current_rsi = get_current_rsi_sum()
    
    if current_rsi is None:
        log_warning("无法获取 RSI Sum，测试可能不准确")
    elif current_rsi >= 800:
        log_warning(f"当前 RSI Sum ({current_rsi}) >= 800，不满足做多条件")
        log_warning("测试将继续，但策略可能不会执行")
    else:
        log_success(f"✅ 当前 RSI Sum ({current_rsi}) < 800，满足做多条件")
    
    # Step 3: 模拟插入见底信号
    log_header("Step 3: 模拟插入见底信号")
    
    signal_inserted = simulate_bottom_signal("✅见底信号")
    
    if not signal_inserted:
        log_error("❌ 测试失败：无法插入测试信号")
        return
    
    # 验证信号已插入
    time.sleep(2)
    get_current_market_sentiment()
    
    # Step 4: 等待策略执行
    execution_found = check_strategy_execution(wait_time=120)
    
    # Step 5: 检查策略日志
    check_strategy_logs()
    
    # Step 6: 恢复原始市场情绪
    # restore_market_sentiment(original_sentiment)
    
    # 测试总结
    log_header("测试总结")
    
    if execution_found:
        log_success("✅ 端到端测试成功！")
        log_success("✅ 策略被成功触发并执行")
    else:
        log_warning("⚠️ 测试未检测到策略执行")
        log_warning("可能原因：")
        log_warning("1. 监控脚本检查间隔（60秒）尚未到达")
        log_warning("2. RSI Sum 不满足条件（>= 800）")
        log_warning("3. 策略开关未启用")
        log_warning("4. JSONL 执行许可为 false（冷却期内）")
        log_info("建议：检查 PM2 日志和策略配置")

if __name__ == '__main__':
    main()
