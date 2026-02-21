#!/usr/bin/env python3
"""
Signal Stats Generator - 从price_position数据生成signal_stats
实时生成逃顶/抄底信号统计数据供图表显示
"""

import json
import time
from pathlib import Path
from datetime import datetime
import pytz

# 配置
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / 'data' / 'price_position'
OUTPUT_DIR = BASE_DIR / 'data' / 'signal_stats'
COLLECT_INTERVAL = 180  # 3分钟，与price_position_collector同步

# 创建输出目录
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_beijing_time():
    """获取北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz)

def generate_stats_for_date(date_str):
    """
    为指定日期生成统计数据
    
    Args:
        date_str: 日期字符串，格式YYYYMMDD
    """
    input_file = INPUT_DIR / f'price_position_{date_str}.jsonl'
    
    if not input_file.exists():
        print(f"⚠️  数据文件不存在: {input_file}")
        return False
    
    # 读取price_position数据
    all_records = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                all_records.append(json.loads(line))
    
    if not all_records:
        print(f"⚠️  没有数据记录")
        return False
    
    # 生成统计数据
    stats_data_sell = []
    stats_data_buy = []
    
    for record in all_records:
        snapshot_time = record['snapshot_time']
        summary = record['summary']
        
        # 获取压力线和支撑线数量
        pressure_line1 = summary.get('pressure_line1_count', 0)
        pressure_line2 = summary.get('pressure_line2_count', 0)
        support_line1 = summary.get('support_line1_count', 0)
        support_line2 = summary.get('support_line2_count', 0)
        
        # 逃顶信号统计（压力线数量）
        sell_24h = pressure_line1 + pressure_line2
        sell_2h = pressure_line1
        
        # 抄底信号统计（支撑线数量）
        buy_24h = support_line1 + support_line2
        buy_2h = support_line1
        
        stats_data_sell.append({
            'time': snapshot_time,
            'sell_24h': sell_24h,
            'sell_2h': sell_2h
        })
        
        stats_data_buy.append({
            'time': snapshot_time,
            'buy_24h': buy_24h,
            'buy_2h': buy_2h
        })
    
    # 保存统计数据
    sell_file = OUTPUT_DIR / f'signal_stats_sell_{date_str}.jsonl'
    buy_file = OUTPUT_DIR / f'signal_stats_buy_{date_str}.jsonl'
    
    with open(sell_file, 'w', encoding='utf-8') as f:
        for record in stats_data_sell:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    with open(buy_file, 'w', encoding='utf-8') as f:
        for record in stats_data_buy:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"✅ 生成统计数据: {date_str}")
    print(f"   逃顶信号: {len(stats_data_sell)} 条 -> {sell_file.name}")
    print(f"   抄底信号: {len(stats_data_buy)} 条 -> {buy_file.name}")
    
    # 显示最新数据
    if stats_data_sell:
        latest = stats_data_sell[-1]
        print(f"   最新数据: {latest['time']} - 逃顶24h={latest['sell_24h']}, 2h={latest['sell_2h']}")
    
    return True

def main():
    """主循环"""
    print("Signal Stats Generator 启动")
    print(f"输入目录: {INPUT_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"采集间隔: {COLLECT_INTERVAL} 秒")
    print("=" * 60)
    
    while True:
        try:
            # 获取今天的日期
            beijing_time = get_beijing_time()
            today_str = beijing_time.strftime('%Y%m%d')
            
            print(f"\n⏰ {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 生成今天的统计数据
            generate_stats_for_date(today_str)
            
            # 等待下次采集
            next_time = beijing_time.replace(second=0, microsecond=0)
            next_time = next_time + timedelta(seconds=COLLECT_INTERVAL)
            print(f"\n⏳ 下次生成时间: {next_time.strftime('%H:%M:%S')}")
            print("等待中...")
            
            time.sleep(COLLECT_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n收到停止信号，退出...")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            print(f"等待 {COLLECT_INTERVAL} 秒后重试...")
            time.sleep(COLLECT_INTERVAL)

if __name__ == '__main__':
    from datetime import timedelta
    main()
