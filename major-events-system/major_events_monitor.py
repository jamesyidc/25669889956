#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重大事件监控器
监控市场异常信号并记录重大事件
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pytz

class MajorEventsMonitor:
    """重大事件监控器"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.events_file = Path(__file__).parent / "data" / "major_events.jsonl"
        self.tz = pytz.timezone('Asia/Shanghai')
        
        # 确保数据目录存在
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 预警阈值
        self.thresholds = {
            'top_signal_2h': {
                'warning': 100,  # 警戒
                'danger': 120    # 危险
            },
            'coins_change_sum': {
                'warning': 80,   # 警戒：涨跌幅总和 ±80%
                'danger': 100    # 危险：涨跌幅总和 ±100%
            },
            'liquidation_1h': {
                'warning': 2000,  # 警戒：2000万美元
                'danger': 3000    # 危险：3000万美元
            }
        }
    
    def get_current_data(self):
        """获取当前三大指标数据"""
        data = {
            'top_signal_2h': 0,
            'coins_change_sum': 0.0,
            'liquidation_1h': 0.0
        }
        
        try:
            # 1. 获取2h逃顶信号
            try:
                response = requests.get(f'{self.base_url}/api/escape-signal-stats?limit=1', timeout=3)
                if response.ok:
                    escape_data = response.json()
                    if escape_data.get('success') and escape_data.get('data'):
                        latest = escape_data['data'][0]
                        data['top_signal_2h'] = latest.get('escape_2h', 0)
            except Exception as e:
                print(f"获取2h逃顶信号失败: {e}")
            
            # 2. 获取27币涨跌幅总和
            try:
                response = requests.get(f'{self.base_url}/api/coin-change-tracker/latest', timeout=3)
                if response.ok:
                    coins_data = response.json()
                    if coins_data.get('success') and coins_data.get('data'):
                        data['coins_change_sum'] = coins_data['data'].get('total_change', 0.0)
            except Exception as e:
                print(f"获取27币涨跌幅失败: {e}")
            
            # 3. 获取1h爆仓金额
            try:
                response = requests.get(f'{self.base_url}/api/liquidation-stats/latest', timeout=3)
                if response.ok:
                    liq_data = response.json()
                    if liq_data.get('success') and liq_data.get('data'):
                        data['liquidation_1h'] = liq_data['data'].get('hour_1_amount', 0.0)
            except Exception as e:
                print(f"获取爆仓数据失败: {e}")
        
        except Exception as e:
            print(f"获取数据失败: {e}")
        
        return data
    
    def check_alert_level(self, indicator, value):
        """检查指标的预警级别"""
        if indicator not in self.thresholds:
            return 'normal'
        
        thresholds = self.thresholds[indicator]
        
        # 对于涨跌幅，使用绝对值判断
        if indicator == 'coins_change_sum':
            value = abs(value)
        
        if value >= thresholds['danger']:
            return 'danger'
        elif value >= thresholds['warning']:
            return 'warning'
        else:
            return 'normal'
    
    def monitor_cycle(self):
        """执行一次监控周期"""
        # 获取当前数据
        data = self.get_current_data()
        timestamp = datetime.now(self.tz)
        
        # 检查每个指标的预警级别
        events = []
        
        for indicator, value in data.items():
            level = self.check_alert_level(indicator, value)
            
            if level != 'normal':
                event = {
                    'timestamp': timestamp.isoformat(),
                    'indicator': indicator,
                    'value': value,
                    'level': level,
                    'description': self._get_event_description(indicator, value, level)
                }
                events.append(event)
                
                # 记录事件
                self._save_event(event)
        
        return events
    
    def _get_event_description(self, indicator, value, level):
        """生成事件描述"""
        indicator_names = {
            'top_signal_2h': '2小时逃顶信号',
            'coins_change_sum': '27币涨跌幅总和',
            'liquidation_1h': '1小时爆仓金额'
        }
        
        level_names = {
            'warning': '⚠️ 警戒',
            'danger': '🚨 危险'
        }
        
        name = indicator_names.get(indicator, indicator)
        level_name = level_names.get(level, level)
        
        if indicator == 'liquidation_1h':
            return f"{level_name} {name}: ${value:,.0f}"
        elif indicator == 'coins_change_sum':
            return f"{level_name} {name}: {value:+.2f}%"
        else:
            return f"{level_name} {name}: {int(value)}"
    
    def _save_event(self, event):
        """保存事件到JSONL文件"""
        try:
            with open(self.events_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"保存事件失败: {e}")
    
    def get_recent_events(self, hours=24):
        """获取最近N小时的事件"""
        if not self.events_file.exists():
            return []
        
        cutoff_time = datetime.now(self.tz) - timedelta(hours=hours)
        events = []
        
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        event_time = datetime.fromisoformat(event['timestamp'])
                        
                        # 确保时区信息
                        if event_time.tzinfo is None:
                            event_time = self.tz.localize(event_time)
                        
                        if event_time >= cutoff_time:
                            events.append(event)
        except Exception as e:
            print(f"读取事件失败: {e}")
        
        # 按时间倒序排序
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return events
    
    def get_current_event_states(self):
        """获取当前事件状态"""
        data = self.get_current_data()
        
        states = {}
        for indicator, value in data.items():
            level = self.check_alert_level(indicator, value)
            states[indicator] = {
                'value': value,
                'level': level,
                'is_alert': level != 'normal'
            }
        
        return states
    
    def get_24h_event_count(self):
        """获取24小时内的事件数量"""
        events = self.get_recent_events(hours=24)
        return len(events)


if __name__ == '__main__':
    # 测试
    monitor = MajorEventsMonitor()
    
    print("=== 当前数据 ===")
    data = monitor.get_current_data()
    for key, value in data.items():
        print(f"{key}: {value}")
    
    print("\n=== 执行监控 ===")
    events = monitor.monitor_cycle()
    if events:
        print(f"触发了 {len(events)} 个预警事件:")
        for event in events:
            print(f"  - {event['description']}")
    else:
        print("所有指标正常")
    
    print(f"\n=== 最近24小时事件 ===")
    recent_events = monitor.get_recent_events(hours=24)
    print(f"共 {len(recent_events)} 个事件")
