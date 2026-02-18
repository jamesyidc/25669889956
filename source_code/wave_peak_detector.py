#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
波峰检测和假突破判断模块
检测27币涨跌幅曲线的波峰波谷，判断市场假突破信号
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

class WavePeakDetector:
    """波峰检测器"""
    
    def __init__(self, min_amplitude: float = 40.0):
        """
        初始化波峰检测器
        
        Args:
            min_amplitude: 最小振幅（B到A的涨跌幅差值），默认40%
        """
        self.min_amplitude = min_amplitude
        self.data_dir = '/home/user/webapp/data/coin_change_tracker'
    
    def load_data(self, date_str: str) -> List[Dict]:
        """
        加载指定日期的数据
        
        Args:
            date_str: 日期字符串，格式YYYYMMDD
            
        Returns:
            数据列表
        """
        file_path = os.path.join(self.data_dir, f'coin_change_{date_str}.jsonl')
        
        if not os.path.exists(file_path):
            print(f"❌ 数据文件不存在: {file_path}")
            return []
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        
        return data
    
    def find_local_extrema(self, data: List[Dict], window_minutes: int = 15) -> Tuple[List[Dict], List[Dict]]:
        """
        查找局部极值点（局部最高点和最低点）
        
        Args:
            data: 数据列表
            window_minutes: 窗口大小（分钟），默认15分钟
            
        Returns:
            (局部最高点列表, 局部最低点列表)
        """
        if len(data) < window_minutes:
            return [], []
        
        local_maxima = []  # 局部最高点
        local_minima = []  # 局部最低点
        
        for i in range(window_minutes, len(data) - window_minutes):
            current_value = data[i]['total_change']
            
            # 检查是否是局部最高点
            is_local_max = True
            for j in range(i - window_minutes, i + window_minutes + 1):
                if j != i and data[j]['total_change'] > current_value:
                    is_local_max = False
                    break
            
            if is_local_max:
                local_maxima.append({
                    'index': i,
                    'timestamp': data[i]['timestamp'],
                    'beijing_time': data[i]['beijing_time'],
                    'value': current_value
                })
            
            # 检查是否是局部最低点
            is_local_min = True
            for j in range(i - window_minutes, i + window_minutes + 1):
                if j != i and data[j]['total_change'] < current_value:
                    is_local_min = False
                    break
            
            if is_local_min:
                local_minima.append({
                    'index': i,
                    'timestamp': data[i]['timestamp'],
                    'beijing_time': data[i]['beijing_time'],
                    'value': current_value
                })
        
        return local_maxima, local_minima
    
    def detect_wave_peaks(self, data: List[Dict]) -> List[Dict]:
        """
        检测波峰（B-A-C结构）
        
        Args:
            data: 数据列表
            
        Returns:
            波峰列表，每个波峰包含B、A、C三个点
        """
        local_maxima, local_minima = self.find_local_extrema(data)
        
        if len(local_maxima) == 0 or len(local_minima) == 0:
            return []
        
        wave_peaks = []
        
        # 遍历所有局部最低点作为B点候选
        for min_point in local_minima:
            b_index = min_point['index']
            b_value = min_point['value']
            
            # 查找B点之后的局部最高点作为A点候选
            a_candidates = [m for m in local_maxima if m['index'] > b_index]
            
            if not a_candidates:
                continue
            
            # 找最近的且满足振幅要求的A点
            for a_point in a_candidates:
                a_index = a_point['index']
                a_value = a_point['value']
                
                # 计算振幅（B到A的差值）
                amplitude = a_value - b_value
                
                # 检查是否满足最小振幅要求
                if amplitude < self.min_amplitude:
                    continue
                
                # 查找C点：A点之后下降超过一半且止跌反升的点
                half_amplitude = amplitude / 2
                target_decline = a_value - half_amplitude
                
                c_point = None
                for i in range(a_index + 1, len(data)):
                    current_value = data[i]['total_change']
                    
                    # 找到下降超过一半的点
                    if current_value <= target_decline:
                        # 检查是否止跌反升（后续有上升）
                        if i + 1 < len(data) and data[i + 1]['total_change'] > current_value:
                            c_point = {
                                'index': i,
                                'timestamp': data[i]['timestamp'],
                                'beijing_time': data[i]['beijing_time'],
                                'value': current_value
                            }
                            break
                
                # 如果找到了C点，记录这个波峰
                if c_point:
                    wave_peak = {
                        'B': {
                            'index': b_index,
                            'timestamp': min_point['timestamp'],
                            'beijing_time': min_point['beijing_time'],
                            'value': b_value
                        },
                        'A': {
                            'index': a_index,
                            'timestamp': a_point['timestamp'],
                            'beijing_time': a_point['beijing_time'],
                            'value': a_value
                        },
                        'C': c_point,
                        'amplitude': amplitude,
                        'decline': a_value - c_point['value'],
                        'decline_ratio': (a_value - c_point['value']) / amplitude * 100
                    }
                    wave_peaks.append(wave_peak)
                    break  # 找到一个波峰后，从下一个B点开始
        
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
        for i in range(len(wave_peaks) - 2):
            peak1 = wave_peaks[i]
            peak2 = wave_peaks[i + 1]
            peak3 = wave_peaks[i + 2]
            
            first_high = peak1['A']['value']
            
            # 检查后续两个波峰是否都没有突破第一个波峰的高点
            if (peak2['A']['value'] <= first_high and 
                peak3['A']['value'] <= first_high):
                
                return {
                    'signal': 'FALSE_BREAKOUT',
                    'description': '假突破信号：连续3个波峰未能突破前高',
                    'peak1_high': first_high,
                    'peak2_high': peak2['A']['value'],
                    'peak3_high': peak3['A']['value'],
                    'peak1_time': peak1['A']['beijing_time'],
                    'peak2_time': peak2['A']['beijing_time'],
                    'peak3_time': peak3['A']['beijing_time'],
                    'warning': '市场可能转跌，建议谨慎操作'
                }
        
        return None
    
    def analyze_today(self) -> Dict:
        """
        分析今天的数据
        
        Returns:
            分析结果字典
        """
        today = datetime.now().strftime('%Y%m%d')
        data = self.load_data(today)
        
        if not data:
            return {
                'success': False,
                'error': f'无法加载今天的数据: {today}'
            }
        
        # 检测波峰
        wave_peaks = self.detect_wave_peaks(data)
        
        # 检测假突破
        false_breakout = self.detect_false_breakout(wave_peaks)
        
        return {
            'success': True,
            'date': today,
            'data_count': len(data),
            'wave_peak_count': len(wave_peaks),
            'wave_peaks': wave_peaks,
            'false_breakout': false_breakout,
            'has_false_breakout': false_breakout is not None
        }

def main():
    """主函数"""
    detector = WavePeakDetector(min_amplitude=40.0)
    
    result = detector.analyze_today()
    
    print('=' * 80)
    print('📊 波峰检测和假突破判断分析')
    print('=' * 80)
    
    if not result['success']:
        print(f"❌ {result['error']}")
        return
    
    print(f"\n📅 日期: {result['date']}")
    print(f"📈 数据点数: {result['data_count']}")
    print(f"🏔️  检测到波峰数: {result['wave_peak_count']}")
    
    if result['wave_peak_count'] > 0:
        print(f"\n{'=' * 80}")
        print('🏔️  波峰详情（B-A-C结构）')
        print('=' * 80)
        
        for i, peak in enumerate(result['wave_peaks'], 1):
            print(f"\n波峰 {i}:")
            print(f"  B点（起点）: {peak['B']['beijing_time']} | 涨跌幅: {peak['B']['value']:.2f}%")
            print(f"  A点（顶点）: {peak['A']['beijing_time']} | 涨跌幅: {peak['A']['value']:.2f}%")
            print(f"  C点（回调）: {peak['C']['beijing_time']} | 涨跌幅: {peak['C']['value']:.2f}%")
            print(f"  振幅: {peak['amplitude']:.2f}% (B→A)")
            print(f"  回调: {peak['decline']:.2f}% (A→C，占振幅 {peak['decline_ratio']:.1f}%)")
    
    if result['has_false_breakout']:
        print(f"\n{'=' * 80}")
        print('⚠️  假突破信号')
        print('=' * 80)
        
        fb = result['false_breakout']
        print(f"\n🚨 {fb['description']}")
        print(f"\n波峰详情:")
        print(f"  波峰1高点: {fb['peak1_high']:.2f}% ({fb['peak1_time']})")
        print(f"  波峰2高点: {fb['peak2_high']:.2f}% ({fb['peak2_time']})")
        print(f"  波峰3高点: {fb['peak3_high']:.2f}% ({fb['peak3_time']})")
        print(f"\n⚠️  {fb['warning']}")
    else:
        print(f"\n✅ 暂无假突破信号")
    
    print(f"\n{'=' * 80}")

if __name__ == '__main__':
    main()
