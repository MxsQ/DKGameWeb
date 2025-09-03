#!/usr/bin/env python3
"""
测试百分比解析功能
"""

from app.services.import_service import parse_float

def test_percentage_parsing():
    """测试百分比解析"""
    test_cases = [
        ("45.59%", 0.4559),
        ("25.30%", 0.253),
        ("100%", 1.0),
        ("0%", 0.0),
        ("42.59", 42.59),  # 非百分比
        ("1234", 1234.0),  # 普通数字
        ("", 0.0),  # 空字符串
        (None, 0.0),  # None值
    ]
    
    print("测试百分比解析功能:")
    print("-" * 40)
    
    for input_val, expected in test_cases:
        result = parse_float(input_val)
        status = "✅" if abs(result - expected) < 0.0001 else "❌"
        print(f"{status} 输入: {repr(input_val)} -> 输出: {result} (期望: {expected})")
    
    print("-" * 40)
    print("测试完成！")

if __name__ == "__main__":
    test_percentage_parsing()
