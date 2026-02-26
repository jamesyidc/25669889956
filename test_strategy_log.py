import requests
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:9002"
ACCOUNT_ID = "account_poit_main"

def test_config_change_log():
    """测试配置变更日志记录"""
    print("=" * 60)
    print("测试1: 配置变更日志记录")
    print("=" * 60)
    
    # 模拟止盈止损配置变更
    tpsl_log = {
        "action": "config_change",
        "strategy_type": "tpsl_settings",
        "account": ACCOUNT_ID,
        "config_changes": {
            "take_profit_enabled": True,
            "take_profit_threshold": 50.0,
            "stop_loss_enabled": True,
            "stop_loss_threshold": -30.0,
            "max_position_value": 5.0
        },
        "reason": "用户修改止盈止损配置"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/okx-trading/strategy-log",
        json=tpsl_log
    )
    
    print(f"止盈止损配置日志: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    
    # 模拟RSI策略开启
    rsi_log = {
        "action": "config_change",
        "strategy_type": "rsi_long_tp",
        "account": ACCOUNT_ID,
        "config_changes": {
            "enabled": True,
            "threshold": 1900
        },
        "reason": "用户开启RSI多单止盈策略"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/okx-trading/strategy-log",
        json=rsi_log
    )
    
    print(f"RSI策略配置日志: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_tamper_protection():
    """测试防篡改保护"""
    print("=" * 60)
    print("测试2: 防篡改保护")
    print("=" * 60)
    
    # 读取日志文件
    today = datetime.now().strftime("%Y%m%d")
    log_file = f"data/okx_strategy_logs/strategy_log_{ACCOUNT_ID}_{today}.jsonl"
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print(f"日志文件: {log_file}")
        print(f"总记录数: {len(lines)}")
        print()
        
        # 检查最后3条日志的哈希值
        print("最近3条日志的哈希值:")
        for line in lines[-3:]:
            log = json.loads(line)
            print(f"时间: {log['timestamp']}")
            print(f"策略: {log.get('strategy_type', 'N/A')}")
            print(f"哈希: {log.get('hash', 'N/A')[:16]}...")
            print()
            
    except FileNotFoundError:
        print(f"❌ 日志文件未找到: {log_file}")
    except Exception as e:
        print(f"❌ 读取日志失败: {e}")

def test_log_query():
    """测试日志查询"""
    print("=" * 60)
    print("测试3: 日志查询")
    print("=" * 60)
    
    response = requests.get(
        f"{BASE_URL}/api/okx-trading/strategy-logs",
        params={
            "account": ACCOUNT_ID,
            "limit": 10
        }
    )
    
    data = response.json()
    print(f"查询结果: {response.status_code}")
    print(f"日志数量: {data['count']}")
    print()
    
    if data['logs']:
        print("最新日志:")
        for log in data['logs'][:3]:
            print(f"  时间: {log['timestamp']}")
            print(f"  动作: {log['action']}")
            print(f"  策略: {log['strategy_type']}")
            if log['action'] == 'config_change':
                print(f"  配置变更: {json.dumps(log.get('config_changes', {}), ensure_ascii=False)}")
            print(f"  哈希: {log.get('hash', 'N/A')[:16]}...")
            print()

if __name__ == "__main__":
    test_config_change_log()
    test_tamper_protection()
    test_log_query()
    
    print("=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
