#!/usr/bin/env python3
"""
启动应用并测试
"""

import subprocess
import time
import requests
from datetime import datetime, timedelta

def start_app():
    """启动应用"""
    print("正在启动应用...")
    
    # 启动应用
    process = subprocess.Popen(['python3', 'run.py'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    # 等待应用启动
    time.sleep(3)
    
    # 测试API
    test_api()
    
    # 停止应用
    process.terminate()
    process.wait()

def test_api():
    """测试API"""
    try:
        # 设置查询参数
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
        response = requests.get('http://localhost:7070/api/game-data', params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"API测试成功，返回 {len(data)} 条数据")
            if data:
                print(f"第一条数据: {data[0]}")
        else:
            print(f"API测试失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"API测试异常: {e}")

if __name__ == "__main__":
    start_app()
