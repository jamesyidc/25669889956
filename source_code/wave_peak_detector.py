#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
波峰检测和假突破判断模块（状态机版）
按照 B确认 → A确认 → C确认 的严格顺序检测波峰
C点可以作为下一个波峰的B点复用
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from enum import Enum

class DetectionState(Enum):
    """波峰检测状态"""
    LOOKING_FOR_B = 1  # 寻找B点
    CONFIRMING_B = 2   # 确认B点（等待15分钟）
    LOOKING_FOR_A = 3  # 寻找A点
    CONFIRMING_A = 4   # 确认A点（等待15分钟）
    LOOKING_FOR_C = 5  # 寻找C点

class WavePeakDetector:
    """波峰检测器（状态机版）"""
    
    def __init__(self, min_amplitude: float = 35.0, window_minutes: int = 15):
        """
        初始化波峰检测器
        
        Args:
            min_amplitude: 最小振幅（B到A的涨跌幅差值），默认35%
            window_minutes: 确认窗口（分钟），点位需要在此窗口内保持极值才算确认，默认15分钟
        """
        self.min_amplitude = min_amplitude
        self.window_minutes = window_minutes
        self.data_dir = '/home/user/webapp/data/coin_change_tracker'
    
    def load_data(self, file_path: str) -> List[Dict]:
        """
        加载数据文件
        
        Args:
            file_path: 数据文件路径
            
        Returns:
            数据列表
        """
        if not os.path.exists(file_path):
            print(f"❌ 数据文件不存在: {file_path}")
            return []
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    
                    # 兼容旧格式：如果没有beijing_time字段，从timestamp字段生成
                    if 'beijing_time' not in record and 'timestamp' in record:
                        # timestamp格式：2026-02-01T09:12:25.698836+08:00
                        # 提取日期和时间部分
                        timestamp_str = record['timestamp']
                        # 去掉时区信息
                        if '+' in timestamp_str:
                            timestamp_str = timestamp_str.split('+')[0]
                        # 转换为beijing_time格式：2026-02-01 09:12:25
                        record['beijing_time'] = timestamp_str.replace('T', ' ').split('.')[0]
                    
                    data.append(record)
        
        return data
    
    def detect_wave_peaks(self, data: List[Dict]) -> tuple[List[Dict], Dict]:
        """
        检测波峰（B-A-C结构）- 状态机版本
        
        状态转换流程：
        1. LOOKING_FOR_B: 找到局部最低点 → CONFIRMING_B
        2. CONFIRMING_B: 等待15分钟确认
           - 期间出现更低点 → 回到 LOOKING_FOR_B
           - 15分钟后仍是最低 → B点确认 → LOOKING_FOR_A
        3. LOOKING_FOR_A: 找到局部最高点且振幅≥35% → CONFIRMING_A
        4. CONFIRMING_A: 等待15分钟确认
           - 期间出现更高点 → 回到 LOOKING_FOR_A
           - 15分钟后仍是最高 → A点确认 → LOOKING_FOR_C
        5. LOOKING_FOR_C: 找到回落>50%后反弹的点 → 记录波峰
           - C点成为下一个波峰的B点候选
        
        Args:
            data: 数据列表
            
        Returns:
            (波峰列表, 当前状态信息)
            - 波峰列表：已完成的波峰（有B、A、C三个点）
            - 当前状态：包含进行中的波峰信息（可能只有B，或只有B-A）
        """
        if len(data) < self.window_minutes * 3:
            return []
        
        wave_peaks = []
        state = DetectionState.LOOKING_FOR_B
        
        # 当前候选点
        b_candidate = None
        b_confirm_start_index = None
        
        a_candidate = None
        a_confirm_start_index = None
        
        # 从C点继承的B点（如果有）
        inherited_b = None
        
        i = 0
        while i < len(data):
            current_value = data[i]['total_change']
            
            # ==================== 状态1: 寻找B点 ====================
            if state == DetectionState.LOOKING_FOR_B:
                # 如果有从上一个波峰的C点继承的B点，直接使用
                if inherited_b is not None:
                    b_candidate = inherited_b
                    b_confirm_start_index = i
                    state = DetectionState.CONFIRMING_B
                    inherited_b = None  # 清除继承
                    print(f"📍 使用继承的B点: {b_candidate['beijing_time']} = {b_candidate['value']:.2f}%")
                # 否则寻找新的局部最低点
                elif i > 0 and current_value < data[i-1]['total_change']:
                    # 发现下降趋势，可能是B点候选
                    b_candidate = {
                        'index': i,
                        'timestamp': data[i]['timestamp'],
                        'beijing_time': data[i]['beijing_time'],
                        'value': current_value
                    }
                    b_confirm_start_index = i
                    state = DetectionState.CONFIRMING_B
                    print(f"🔍 发现B点候选: {b_candidate['beijing_time']} = {b_candidate['value']:.2f}%")
                
                i += 1
            
            # ==================== 状态2: 确认B点 ====================
            elif state == DetectionState.CONFIRMING_B:
                # 检查是否出现了更低点
                if current_value < b_candidate['value']:
                    print(f"⚠️  B点被推翻，发现更低点: {data[i]['beijing_time']} = {current_value:.2f}%")
                    # 重新设置B点候选
                    b_candidate = {
                        'index': i,
                        'timestamp': data[i]['timestamp'],
                        'beijing_time': data[i]['beijing_time'],
                        'value': current_value
                    }
                    b_confirm_start_index = i
                    print(f"🔍 新的B点候选: {b_candidate['beijing_time']} = {b_candidate['value']:.2f}%")
                
                # 检查是否已经过了确认窗口
                if i - b_confirm_start_index >= self.window_minutes:
                    # B点确认成功
                    print(f"✅ B点确认: {b_candidate['beijing_time']} = {b_candidate['value']:.2f}%")
                    a_candidate = None  # 重置A点候选
                    state = DetectionState.LOOKING_FOR_A
                
                i += 1
            
            # ==================== 状态3: 寻找A点 ====================
            elif state == DetectionState.LOOKING_FOR_A:
                # 确保A点在B点之后
                if i <= b_candidate['index']:
                    i += 1
                    continue
                
                # ⚠️ 检查是否出现了比B点更低的点，如果是，则放弃当前B点，重新寻找
                if current_value < b_candidate['value']:
                    print(f"⚠️  在寻找A点期间，发现比B点更低的点: {data[i]['beijing_time']} = {current_value:.2f}%")
                    print(f"   放弃当前B点，重新开始寻找B点")
                    state = DetectionState.LOOKING_FOR_B
                    b_candidate = None
                    a_candidate = None
                    # 不增加i，让下一轮循环处理这个新的低点
                    continue
                
                # 检查振幅是否满足要求
                amplitude = current_value - b_candidate['value']
                
                # 如果还没有A候选，或者当前值更高且振幅满足要求
                if a_candidate is None:
                    if amplitude >= self.min_amplitude:
                        a_candidate = {
                            'index': i,
                            'timestamp': data[i]['timestamp'],
                            'beijing_time': data[i]['beijing_time'],
                            'value': current_value
                        }
                        a_confirm_start_index = i
                        state = DetectionState.CONFIRMING_A
                        print(f"🔍 发现A点候选: {a_candidate['beijing_time']} = {a_candidate['value']:.2f}%, 振幅={amplitude:.2f}%")
                elif current_value > a_candidate['value'] and amplitude >= self.min_amplitude:
                    # 更新A候选
                    a_candidate = {
                        'index': i,
                        'timestamp': data[i]['timestamp'],
                        'beijing_time': data[i]['beijing_time'],
                        'value': current_value
                    }
                    a_confirm_start_index = i
                    print(f"🔄 更新A点候选: {a_candidate['beijing_time']} = {a_candidate['value']:.2f}%, 振幅={amplitude:.2f}%")
                
                i += 1
            
            # ==================== 状态4: 确认A点 ====================
            elif state == DetectionState.CONFIRMING_A:
                # ⚠️ 检查是否出现了比B点更低的点
                if current_value < b_candidate['value']:
                    print(f"⚠️  在确认A点期间，发现比B点更低的点: {data[i]['beijing_time']} = {current_value:.2f}%")
                    print(f"   放弃当前B点和A点，重新开始")
                    state = DetectionState.LOOKING_FOR_B
                    b_candidate = None
                    a_candidate = None
                    continue
                
                # 检查是否出现了更高点
                if current_value > a_candidate['value']:
                    # 检查新的高点振幅是否仍然满足
                    new_amplitude = current_value - b_candidate['value']
                    if new_amplitude >= self.min_amplitude:
                        print(f"⚠️  A点被推翻，发现更高点: {data[i]['beijing_time']} = {current_value:.2f}%")
                        a_candidate = {
                            'index': i,
                            'timestamp': data[i]['timestamp'],
                            'beijing_time': data[i]['beijing_time'],
                            'value': current_value
                        }
                        a_confirm_start_index = i
                        print(f"🔍 新的A点候选: {a_candidate['beijing_time']} = {a_candidate['value']:.2f}%, 振幅={new_amplitude:.2f}%")
                
                # 检查是否已经过了确认窗口
                if i - a_confirm_start_index >= self.window_minutes:
                    # A点确认成功
                    amplitude = a_candidate['value'] - b_candidate['value']
                    print(f"✅ A点确认: {a_candidate['beijing_time']} = {a_candidate['value']:.2f}%, 振幅={amplitude:.2f}%")
                    state = DetectionState.LOOKING_FOR_C
                
                i += 1
            
            # ==================== 状态5: 寻找C点 ====================
            elif state == DetectionState.LOOKING_FOR_C:
                # 确保C点在A点之后
                if i <= a_candidate['index']:
                    i += 1
                    continue
                
                # 计算目标回落值（振幅的一半）
                amplitude = a_candidate['value'] - b_candidate['value']
                half_amplitude = amplitude / 2
                target_decline = a_candidate['value'] - half_amplitude
                
                # 检查是否已经回落超过一半
                if current_value <= target_decline:
                    # 检查是否止跌反弹
                    if i + 1 < len(data) and data[i + 1]['total_change'] > current_value:
                        # 找到C点，记录完整波峰
                        c_point = {
                            'index': i,
                            'timestamp': data[i]['timestamp'],
                            'beijing_time': data[i]['beijing_time'],
                            'value': current_value
                        }
                        
                        decline = a_candidate['value'] - c_point['value']
                        decline_ratio = (decline / amplitude) * 100
                        
                        wave_peak = {
                            'b_point': b_candidate,
                            'a_point': a_candidate,
                            'c_point': c_point,
                            'amplitude': amplitude,
                            'decline': decline,
                            'decline_ratio': decline_ratio
                        }
                        wave_peaks.append(wave_peak)
                        
                        print(f"✅ 完整波峰记录: B({b_candidate['value']:.2f}%) → A({a_candidate['value']:.2f}%) → C({c_point['value']:.2f}%)")
                        print(f"   振幅={amplitude:.2f}%, 回调={decline:.2f}% ({decline_ratio:.1f}%)")
                        
                        # C点作为下一个波峰的B点候选
                        inherited_b = c_point
                        print(f"♻️  C点将作为下一个波峰的B点候选")
                        
                        # 重置状态，开始寻找下一个波峰
                        state = DetectionState.LOOKING_FOR_B
                        b_candidate = None
                        a_candidate = None
                
                i += 1
        
        # 构建当前状态信息
        current_state = {
            'state': state.value if state else 'COMPLETED',
            'b_candidate': b_candidate if b_candidate else None,
            'a_candidate': a_candidate if a_candidate else None,
            'has_incomplete_peak': (b_candidate is not None or a_candidate is not None)
        }
        
        # 如果有B-A但没有C，说明有一个进行中的波峰
        if b_candidate and a_candidate and state == DetectionState.LOOKING_FOR_C:
            amplitude = a_candidate['value'] - b_candidate['value']
            current_state['incomplete_peak'] = {
                'b_point': b_candidate,
                'a_point': a_candidate,
                'amplitude': amplitude,
                'status': '等待C点形成'
            }
        
        return wave_peaks, current_state
    
    def detect_false_breakout(self, wave_peaks: List[Dict]) -> Optional[Dict]:
        """
        检测假突破信号
        
        连续3个波峰的A点都没有突破第一个波峰的前高，判断为假突破
        
        Args:
            wave_peaks: 波峰列表
            
        Returns:
            假突破信号字典，如果没有假突破返回None
        """
        if len(wave_peaks) < 3:
            return None
        
        # 检查最近的3个波峰
        recent_peaks = wave_peaks[-3:]
        
        peak1 = recent_peaks[0]
        peak2 = recent_peaks[1]
        peak3 = recent_peaks[2]
        
        first_high = peak1['a_point']['value']
        
        # 检查后续两个波峰是否都没有突破第一个波峰的高点
        if (peak2['a_point']['value'] <= first_high and 
            peak3['a_point']['value'] <= first_high):
            
            return {
                'consecutive_peaks': 3,
                'reference_high': first_high,
                'peaks': recent_peaks,
                'warning': '市场可能转跌，建议谨慎操作'
            }
        
        return None

def main():
    """主函数 - 测试指定日期的数据"""
    from datetime import datetime
    import sys
    
    detector = WavePeakDetector(min_amplitude=35.0, window_minutes=15)
    
    # 从命令行参数获取日期，如果没有则使用今天
    if len(sys.argv) > 1:
        today = sys.argv[1]
    else:
        today = datetime.now().strftime('%Y%m%d')
    
    file_path = f'/home/user/webapp/data/coin_change_tracker/coin_change_{today}.jsonl'
    
    data = detector.load_data(file_path)
    
    print('=' * 80)
    print('📊 波峰检测分析（状态机版 - B→A→C严格顺序）')
    print('=' * 80)
    print(f"\n📅 日期: {today}")
    print(f"📈 数据点数: {len(data)}")
    print(f"⚙️  参数设置:")
    print(f"   - 最小振幅: {detector.min_amplitude}%")
    print(f"   - 确认窗口: {detector.window_minutes}分钟")
    print(f"\n🔄 检测逻辑:")
    print(f"   1. 先找到B点 → 等待15分钟确认")
    print(f"   2. B点确认后 → 开始找A点 → 等待15分钟确认")
    print(f"   3. A点确认后 → 开始找C点")
    print(f"   4. C点找到后 → 作为下一个波峰的B点候选")
    
    print(f"\n{'=' * 80}")
    print('🔍 开始检测...')
    print('=' * 80)
    
    # 检测波峰
    wave_peaks, current_state = detector.detect_wave_peaks(data)
    
    print(f"\n{'=' * 80}")
    print(f"🏔️  检测到波峰数: {len(wave_peaks)}")
    print('=' * 80)
    
    if len(wave_peaks) > 0:
        for i, peak in enumerate(wave_peaks, 1):
            print(f"\n波峰 {i}:")
            print(f"  B点（谷底）: {peak['b_point']['beijing_time']} | 涨跌幅: {peak['b_point']['value']:.2f}%")
            print(f"  A点（峰顶）: {peak['a_point']['beijing_time']} | 涨跌幅: {peak['a_point']['value']:.2f}%")
            print(f"  C点（回调）: {peak['c_point']['beijing_time']} | 涨跌幅: {peak['c_point']['value']:.2f}%")
            print(f"  振幅 (B→A): {peak['amplitude']:.2f}%")
            print(f"  回调 (A→C): {peak['decline']:.2f}% (占振幅 {peak['decline_ratio']:.1f}%)")
    
    # 显示进行中的波峰
    if current_state.get('incomplete_peak'):
        print(f"\n{'=' * 80}")
        print(f"⏳ 进行中的波峰")
        print('=' * 80)
        incomplete = current_state['incomplete_peak']
        print(f"\n  B点（谷底）: {incomplete['b_point']['beijing_time']} | 涨跌幅: {incomplete['b_point']['value']:.2f}%")
        print(f"  A点（峰顶）: {incomplete['a_point']['beijing_time']} | 涨跌幅: {incomplete['a_point']['value']:.2f}%")
        print(f"  C点（回调）: {incomplete['status']}")
        print(f"  振幅 (B→A): {incomplete['amplitude']:.2f}%")
        print(f"\n  💡 提示：A点已确认，正在等待价格回落超过50%振幅后反弹，形成C点")
    
    # 检测假突破
    false_breakout = detector.detect_false_breakout(wave_peaks)
    
    if false_breakout:
        print(f"\n{'=' * 80}")
        print('⚠️  假突破信号')
        print('=' * 80)
        
        print(f"\n🚨 检测到假突破：连续3个波峰的A点均未突破第一个波峰前高")
        print(f"\n参考高点: {false_breakout['reference_high']:.2f}%")
        print(f"\n连续3个波峰:")
        for i, peak in enumerate(false_breakout['peaks'], 1):
            print(f"  波峰{i} A点: {peak['a_point']['value']:.2f}% ({peak['a_point']['beijing_time']})")
        print(f"\n⚠️  {false_breakout['warning']}")
    else:
        print(f"\n✅ 暂无假突破信号")
    
    print(f"\n{'=' * 80}")

if __name__ == '__main__':
    main()
