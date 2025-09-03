#!/usr/bin/env python3
"""
测试数据库表结构是否包含DAY7字段
"""

from app.services.import_service import ensure_game_data_table
from app.utils.db import get_connection

def test_table_structure():
    """测试gameData表结构"""
    print("正在检查gameData表结构...")
    
    # 确保表存在
    ensure_game_data_table()
    
    # 查询表结构
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("DESCRIBE gameData")
            columns = cur.fetchall()
            
            print("gameData表字段:")
            for col in columns:
                print(f"  {col['Field']} - {col['Type']}")
            
            # 检查是否包含DAY7字段
            day7_exists = any(col['Field'] == 'DAY7' for col in columns)
            print(f"\nDAY7字段存在: {day7_exists}")

if __name__ == "__main__":
    test_table_structure()
