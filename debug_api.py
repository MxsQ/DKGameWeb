#!/usr/bin/env python3
"""
测试API返回格式
"""

import requests
import json
from datetime import datetime

def test_api_response():
    """测试API返回格式"""
    print("测试API返回格式:")
    print("-" * 40)
    
    # 模拟一个简单的测试
    test_data = {
        'inserted': 5,
        'updated': 3,
        'total': 8
    }
    
    print("期望的返回格式:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    print("\n前端处理逻辑:")
    print("if (data.inserted !== undefined && data.updated !== undefined):")
    print("    message = `导入完成！新增 ${data.inserted} 条记录，更新 ${data.updated} 条记录，共处理 ${data.total} 条记录`")
    
    print("\n如果看到 '导入成功x条' 的提示，可能的原因:")
    print("1. API返回的格式不是预期的 {inserted, updated, total}")
    print("2. 前端JavaScript没有正确解析返回数据")
    print("3. 浏览器控制台可能有错误信息")
    
    print("\n建议检查:")
    print("1. 在浏览器开发者工具中查看Network标签页的API响应")
    print("2. 查看Console标签页是否有JavaScript错误")
    print("3. 确认API实际返回的数据格式")

if __name__ == "__main__":
    test_api_response()
