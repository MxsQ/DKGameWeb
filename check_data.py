#!/usr/bin/env python3
"""
检查数据库中是否有数据
"""

from app.services.game_service import get_game_data
from datetime import datetime, timedelta

def check_data():
    """检查数据库中的数据"""
    print("正在检查数据库中的数据...")
    
    # 查询最近一周的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"查询时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    
    try:
        data = get_game_data(start_date, end_date)
        print(f"查询到 {len(data)} 条记录")
        
        if data:
            print("\n前3条记录:")
            for i, row in enumerate(data[:3]):
                print(f"  记录{i+1}: {row}")
        else:
            print("没有查询到数据")
            
    except Exception as e:
        print(f"查询失败: {e}")

if __name__ == "__main__":
    check_data()
