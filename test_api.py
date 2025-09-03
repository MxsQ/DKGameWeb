#!/usr/bin/env python3
"""
测试API接口
"""

import requests
from datetime import datetime, timedelta

def test_api():
    """测试API接口"""
    base_url = "http://localhost:7070"
    
    # 设置查询参数
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    print(f"测试API: {base_url}/api/game-data")
    print(f"参数: {params}")
    
    try:
        response = requests.get(f"{base_url}/api/game-data", params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据条数: {len(data)}")
            if data:
                print(f"第一条数据: {data[0]}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_api()
