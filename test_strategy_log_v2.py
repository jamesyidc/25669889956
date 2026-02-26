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
        "action_type": "config_change",  # 修正字段名
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
    result = response.json()
    print(f"成功: {result.get('success')}")
    if result.get('hash'):
        print(f"哈希: {result['hash'][:32]}...")
    print()
    
    # 模拟RSI策略开启
    rsi_log = {
        "action_type": "config_change",
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
    result = response.json()
    print(f"成功: {result.get('success')}")
    if result.get('hash'):
        print(f"哈希: {result['hash'][:32]}...")
    print()
    
    # 模拟见顶信号策略关闭
    top_signal_log = {
        "action_type": "config_change",
        "strategy_type": "top_signal_top8_short",
        "account": ACCOUNT_ID,
        "config_changes": {
            "enabled": False
        },
        "reason": "用户关闭见顶信号涨幅前8做空策略"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/okx-trading/strategy-log",
        json=top_signal_log
    )
    
    print(f"见顶信号策略日志: {response.status_code}")
    result = response.json()
    print(f"成功: {result.get('success')}")
    if result.get('hash'):
        print(f"哈希: {result['hash'][:32]}...")
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
        print("最新3条日志的哈希值:")
        for i, line in enumerate(lines[-3:], 1):
            log = json.loads(line)
            print(f"[{i}] 时间: {log['timestamp']}")
            print(f"    策略: {log.get('strategy_type', 'N/A')}")
            print(f"    动作: {log.get('action_type', 'N/A')}")
            
            if '_hash' in log:
                print(f"    哈希: {log['_hash'][:32]}...")
                print(f"    算法: {log.get('_hash_algorithm', 'N/A')}")
            else:
                print(f"    ⚠️  无哈希值（旧数据）")
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
        print("最新3条日志:")
        for i, log in enumerate(data['logs'][:3], 1):
            print(f"[{i}] 时间: {log['timestamp']}")
            print(f"    动作: {log.get('action_type', log.get('action', 'N/A'))}")
            print(f"    策略: {log['strategy_type']}")
            
            if log.get('action_type') == 'config_change':
                print(f"    配置变更: {json.dumps(log.get('config_changes', {}), ensure_ascii=False)}")
            
            if '_hash' in log:
                print(f"    哈希: {log['_hash'][:32]}...")
            else:
                print(f"    ⚠️  无哈希值")
            print()

def test_verify_logs():
    """测试日志验证"""
    print("=" * 60)
    print("测试4: 日志完整性验证")
    print("=" * 60)
    
    today = datetime.now().strftime("%Y%m%d")
    
    response = requests.post(
        f"{BASE_URL}/api/okx-trading/verify-strategy-logs",
        json={
            "account": ACCOUNT_ID,
            "date": today
        }
    )
    
    result = response.json()
    print(f"验证结果: {response.status_code}")
    print(f"完整性: {'✅ 通过' if result.get('valid') else '❌ 失败'}")
    print(f"总日志数: {result.get('total_logs', 0)}")
    print(f"已验证: {result.get('verified_logs', 0)}")
    print(f"无哈希: {result.get('logs_without_hash', 0)}")
    
    if result.get('tampered_logs'):
        print(f"⚠️  篡改日志数: {len(result['tampered_logs'])}")
        for log in result['tampered_logs'][:3]:
            print(f"  - {log['timestamp']}: {log.get('reason', 'Unknown')}")

if __name__ == "__main__":
    test_config_change_log()
    test_tamper_protection()
    test_log_query()
    test_verify_logs()
    
    print("=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
