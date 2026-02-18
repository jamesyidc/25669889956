#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
波峰检测和假突破判断模块（改进版）
动态确认B-A-C波峰结构，B/A点需要15分钟内保持极值才确认
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

class WavePeakDetector:
    """波峰检测器（动态确认版）"""
    
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
                    data.append(record)
        
        return data
    
    def is_confirmed_minimum(self, data: List[Dict], index: int) -> bool:
        """
        确认是否为确认的最低点（后续15分钟内没有更低点）
        
        Args:
            data: 数据列表
            index: 候选点的索引
            
        Returns:
            是否为确认的最低点
        """
        if index >= len(data):
            return False
        
        current_value = data[index]['total_change']
        
        # 检查后续15分钟内是否有更低点
        for i in range(index + 1, min(index + self.window_minutes + 1, len(data))):
            if data[i]['total_change'] < current_value:
                return False  # 后续有更低点，当前点不是确认的B点
        
        return True
    
    def is_confirmed_maximum(self, data: List[Dict], index: int) -> bool:
        """
        确认是否为确认的最高点（后续15分钟内没有更高点）
        
        Args:
            data: 数据列表
            index: 候选点的索引
            
        Returns:
            是否为确认的最高点
        """
        if index >= len(data):
            return False
        
        current_value = data[index]['total_change']
        
        # 检查后续15分钟内是否有更高点
        for i in range(index + 1, min(index + self.window_minutes + 1, len(data))):
            if data[i]['total_change'] > current_value:
                return False  # 后续有更高点，当前点不是确认的A点
        
        return True
    
    def detect_wave_peaks(self, data: List[Dict]) -> List[Dict]:
        """
        检测波峰（B-A-C结构）- 动态确认版
        
        算法逻辑：
        1. 找到一个局部最低点作为B点候选
        2. 等待15分钟，如果期间出现更低点，则重新确认B点
        3. B点确认后，向后查找局部最高点作为A点候选
        4. 等待15分钟，如果期间出现更高点，则重新确认A点
        5. A点确认且振幅≥35%，查找C点（回落超过一半后反弹）
        6. 找到C点后记录完整的B-A-C波峰
        
        Args:
            data: 数据列表
            
        Returns:
            波峰列表，每个波峰包含B、A、C三个点
        """
        if len(data) < self.window_minutes * 3:
            return []
        
        wave_peaks = []
        i = 0
        
        while i < len(data) - self.window_minutes * 2:
            # ==================== 步骤1: 查找并确认B点 ====================
            # 找到当前位置的局部最低点
            b_index = None
            b_value = None
            
            # 向前查找局部最低点（窗口内的最低值）
            for j in range(i, min(i + self.window_minutes, len(data))):
                if b_index is None or data[j]['total_change'] < b_value:
                    b_index = j
                    b_value = data[j]['total_change']
            
            # 检查B点是否被确认（后续15分钟内没有更低点）
            if not self.is_confirmed_minimum(data, b_index):
                i += 1  # B点未确认，继续向前找
                continue
            
            # B点已确认
            b_point = {
                'index': b_index,
                'timestamp': data[b_index]['timestamp'],
                'beijing_time': data[b_index]['beijing_time'],
                'value': b_value
            }
            
            # ==================== 步骤2: 查找并确认A点 ====================
            a_index = None
            a_value = None
            
            # 从B点之后开始查找局部最高点
            search_start = b_index + 1
            search_end = min(b_index + self.window_minutes * 4, len(data))  # 在更大的范围内找A点
            
            for j in range(search_start, search_end):
                if a_index is None or data[j]['total_change'] > a_value:
                    a_index = j
                    a_value = data[j]['total_change']
                
                # 每找到一个新的高点，都要确认它是否是确认的A点
                if a_index == j and self.is_confirmed_maximum(data, a_index):
                    # A点确认，检查振幅
                    amplitude = a_value - b_value
                    
                    if amplitude >= self.min_amplitude:
                        # 振幅满足要求，A点有效
                        break
                    else:
                        # 振幅不够，继续找更高的A点
                        continue
            
            # 检查是否找到了有效的A点
            if a_index is None or not self.is_confirmed_maximum(data, a_index):
                i = b_index + 1  # A点未找到或未确认，从B点后继续
                continue
            
            amplitude = a_value - b_value
            if amplitude < self.min_amplitude:
                i = b_index + 1  # 振幅不够，继续
                continue
            
            # A点已确认且振幅足够
            a_point = {
                'index': a_index,
                'timestamp': data[a_index]['timestamp'],
                'beijing_time': data[a_index]['beijing_time'],
                'value': a_value
            }
            
            # ==================== 步骤3: 查找C点 ====================
            # C点：A点之后下降超过振幅一半，且开始反弹的点
            half_amplitude = amplitude / 2
            target_decline = a_value - half_amplitude
            
            c_point = None
            for j in range(a_index + 1, len(data)):
                current_value = data[j]['total_change']
                
                # 找到下降超过一半的点
                if current_value <= target_decline:
                    # 检查是否止跌反升（后续有上升）
                    if j + 1 < len(data):
                        next_value = data[j + 1]['total_change']
                        if next_value > current_value:
                            c_point = {
                                'index': j,
                                'timestamp': data[j]['timestamp'],
                                'beijing_time': data[j]['beijing_time'],
                                'value': current_value
                            }
                            break
            
            # 如果找到了C点，记录这个完整的波峰
            if c_point:
                wave_peak = {
                    'b_point': b_point,
                    'a_point': a_point,
                    'c_point': c_point,
                    'amplitude': amplitude,
                    'decline': a_value - c_point['value'],
                    'decline_ratio': (a_value - c_point['value']) / amplitude * 100
                }
                wave_peaks.append(wave_peak)
                
                # 跳到C点之后继续查找下一个波峰
                i = c_point['index'] + 1
            else:
                # 没找到C点，从A点后继续
                i = a_index + 1
        
        return wave_peaks
    
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
    """主函数 - 测试今天的数据"""
    from datetime import datetime
    
    detector = WavePeakDetector(min_amplitude=35.0, window_minutes=15)
    
    # 加载今天的数据
    today = datetime.now().strftime('%Y%m%d')
    file_path = f'/home/user/webapp/data/coin_change_tracker/coin_change_{today}.jsonl'
    
    data = detector.load_data(file_path)
    
    print('=' * 80)
    print('📊 波峰检测分析（动态确认版）')
    print('=' * 80)
    print(f"\n📅 日期: {today}")
    print(f"📈 数据点数: {len(data)}")
    print(f"⚙️  参数设置:")
    print(f"   - 最小振幅: {detector.min_amplitude}%")
    print(f"   - 确认窗口: {detector.window_minutes}分钟")
    
    # 检测波峰
    wave_peaks = detector.detect_wave_peaks(data)
    
    print(f"\n🏔️  检测到波峰数: {len(wave_peaks)}")
    
    if len(wave_peaks) > 0:
        print(f"\n{'=' * 80}")
        print('🏔️  波峰详情（B-A-C结构）')
        print('=' * 80)
        
        for i, peak in enumerate(wave_peaks, 1):
            print(f"\n波峰 {i}:")
            print(f"  B点（谷底）: {peak['b_point']['beijing_time']} | 涨跌幅: {peak['b_point']['value']:.2f}%")
            print(f"  A点（峰顶）: {peak['a_point']['beijing_time']} | 涨跌幅: {peak['a_point']['value']:.2f}%")
            print(f"  C点（回调）: {peak['c_point']['beijing_time']} | 涨跌幅: {peak['c_point']['value']:.2f}%")
            print(f"  振幅 (B→A): {peak['amplitude']:.2f}%")
            print(f"  回调 (A→C): {peak['decline']:.2f}% (占振幅 {peak['decline_ratio']:.1f}%)")
    
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
