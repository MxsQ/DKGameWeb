#!/usr/bin/env python3
"""
测试数据聚合功能
"""

from app.services.game_service import normalize_channel_name, aggregate_game_data
from datetime import datetime, timedelta

def test_channel_normalization():
    """测试渠道名称标准化"""
    test_cases = [
        ("田地CPS", "田地CPS"),
        ("田地CPS-1", "田地CPS"),
        ("田地CPS-10", "田地CPS"),
        ("TapTap", "TapTap"),
        ("TapTap-5", "TapTap"),
        ("360CPS", "360CPS"),
        ("PC国服官方包", "PC国服官方包"),
        ("", ""),
        (None, None),
    ]
    
    print("测试渠道名称标准化:")
    print("-" * 40)
    
    for input_val, expected in test_cases:
        result = normalize_channel_name(input_val)
        status = "✅" if result == expected else "❌"
        print(f"{status} 输入: {repr(input_val)} -> 输出: {repr(result)} (期望: {repr(expected)})")
    
    print("-" * 40)

def test_aggregation():
    """测试数据聚合功能"""
    print("测试数据聚合功能:")
    print("-" * 40)
    
    # 设置测试时间范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"查询时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # 测试日维度 + 分包维度
        data_day_category = aggregate_game_data(start_date, end_date, time_group='day', channel_group='category')
        print(f"日维度+分包维度: {len(data_day_category)} 条记录")
        
        # 测试日维度 + 渠道维度
        data_day_channel = aggregate_game_data(start_date, end_date, time_group='day', channel_group='channel')
        print(f"日维度+渠道维度: {len(data_day_channel)} 条记录")
        
        # 测试周维度 + 分包维度
        data_week_category = aggregate_game_data(start_date, end_date, time_group='week', channel_group='category')
        print(f"周维度+分包维度: {len(data_week_category)} 条记录")
        
        # 测试月维度 + 分包维度
        data_month_category = aggregate_game_data(start_date, end_date, time_group='month', channel_group='category')
        print(f"月维度+分包维度: {len(data_month_category)} 条记录")
        
        if data_day_category:
            print(f"\n示例聚合数据:")
            sample = data_day_category[0]
            print(f"  日期: {sample['date']}")
            print(f"  渠道: {sample['channel']}")
            print(f"  新增: {sample['newUser']}")
            print(f"  次留: {sample['DAY1']:.4f}")
            print(f"  七留: {sample['DAY7']:.4f}")
            
    except Exception as e:
        print(f"聚合测试失败: {e}")
    
    print("-" * 40)

if __name__ == "__main__":
    test_channel_normalization()
    test_aggregation()

