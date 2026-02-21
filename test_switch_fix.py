#!/usr/bin/env python3
"""
测试新的开关保存逻辑：每个开关只更新自己，不影响其他开关
"""
import requests
import json

BASE_URL = "http://localhost:9002"
ACCOUNT_ID = "account_main"

def get_settings():
    """获取当前设置"""
    response = requests.get(f"{BASE_URL}/api/okx-trading/tpsl-settings/{ACCOUNT_ID}")
    data = response.json()
    if data['success']:
        return data['settings']
    return None

def print_settings(settings, title="当前设置"):
    """打印设置"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"止盈开关: {settings['takeProfitEnabled']}")
    print(f"止损开关: {settings['stopLossEnabled']}")
    print(f"RSI多单止盈: {settings['rsiTakeProfitEnabled']}")
    print(f"RSI空单止盈: {settings['rsiShortTakeProfitEnabled']}")
    print(f"市场情绪止盈: {settings['sentimentTakeProfitEnabled']}")
    print(f"{'='*60}\n")

def test_single_switch():
    """测试单个开关切换"""
    
    # 1. 重置所有开关为 false
    print("步骤1: 重置所有开关为 false")
    reset_data = {
        "takeProfitEnabled": False,
        "takeProfitThreshold": 50,
        "stopLossEnabled": False,
        "stopLossThreshold": -30,
        "rsiTakeProfitEnabled": False,
        "rsiTakeProfitThreshold": 1900,
        "rsiShortTakeProfitEnabled": False,
        "rsiShortTakeProfitThreshold": 810,
        "sentimentTakeProfitEnabled": False,
        "maxPositionValueUsdt": 5.0
    }
    response = requests.post(f"{BASE_URL}/api/okx-trading/tpsl-settings/{ACCOUNT_ID}",
                            json=reset_data)
    print(f"重置结果: {response.json()['success']}")
    
    settings = get_settings()
    print_settings(settings, "重置后的设置")
    
    # 2. 测试：只打开止盈开关（模拟用户点击）
    print("\n步骤2: 模拟用户点击 takeProfitSwitch，只打开止盈开关")
    print("（新逻辑：先从服务器加载当前配置，然后只更新 takeProfitEnabled 字段）")
    
    # 模拟 saveSingleSwitchSetting('takeProfitEnabled', true)
    # 先获取当前配置
    current = get_settings()
    # 只更新 takeProfitEnabled
    current['takeProfitEnabled'] = True
    # 保存
    response = requests.post(f"{BASE_URL}/api/okx-trading/tpsl-settings/{ACCOUNT_ID}",
                            json=current)
    print(f"保存结果: {response.json()['success']}")
    
    settings = get_settings()
    print_settings(settings, "只打开止盈开关后的设置")
    
    # 验证：其他开关应该保持 false
    assert settings['takeProfitEnabled'] == True, "❌ 止盈开关应该为 True"
    assert settings['stopLossEnabled'] == False, "❌ 止损开关应该保持 False"
    assert settings['rsiTakeProfitEnabled'] == False, "❌ RSI多单止盈应该保持 False"
    assert settings['rsiShortTakeProfitEnabled'] == False, "❌ RSI空单止盈应该保持 False"
    assert settings['sentimentTakeProfitEnabled'] == False, "❌ 市场情绪止盈应该保持 False"
    
    print("✅ 验证通过：只有止盈开关为 True，其他开关保持 False\n")
    
    # 3. 测试：再打开 RSI 多单止盈开关
    print("\n步骤3: 模拟用户点击 rsiTakeProfitSwitch，打开 RSI 多单止盈")
    current = get_settings()
    current['rsiTakeProfitEnabled'] = True
    response = requests.post(f"{BASE_URL}/api/okx-trading/tpsl-settings/{ACCOUNT_ID}",
                            json=current)
    print(f"保存结果: {response.json()['success']}")
    
    settings = get_settings()
    print_settings(settings, "打开RSI多单止盈后的设置")
    
    # 验证：之前打开的开关应该保持 True
    assert settings['takeProfitEnabled'] == True, "❌ 止盈开关应该保持 True"
    assert settings['rsiTakeProfitEnabled'] == True, "❌ RSI多单止盈应该为 True"
    assert settings['stopLossEnabled'] == False, "❌ 止损开关应该保持 False"
    assert settings['rsiShortTakeProfitEnabled'] == False, "❌ RSI空单止盈应该保持 False"
    assert settings['sentimentTakeProfitEnabled'] == False, "❌ 市场情绪止盈应该保持 False"
    
    print("✅ 验证通过：止盈和RSI多单止盈都为 True，其他开关保持 False\n")
    
    # 4. 测试：关闭止盈开关
    print("\n步骤4: 模拟用户再次点击 takeProfitSwitch，关闭止盈开关")
    current = get_settings()
    current['takeProfitEnabled'] = False
    response = requests.post(f"{BASE_URL}/api/okx-trading/tpsl-settings/{ACCOUNT_ID}",
                            json=current)
    print(f"保存结果: {response.json()['success']}")
    
    settings = get_settings()
    print_settings(settings, "关闭止盈开关后的设置")
    
    # 验证：RSI 多单止盈应该保持 True
    assert settings['takeProfitEnabled'] == False, "❌ 止盈开关应该为 False"
    assert settings['rsiTakeProfitEnabled'] == True, "❌ RSI多单止盈应该保持 True"
    
    print("✅ 验证通过：关闭止盈后，RSI多单止盈保持 True\n")
    
    print("\n" + "="*60)
    print("🎉 所有测试通过！开关切换逻辑正确！")
    print("="*60)

if __name__ == "__main__":
    test_single_switch()
