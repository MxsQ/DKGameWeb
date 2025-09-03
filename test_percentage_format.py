#!/usr/bin/env python3
"""
测试百分比格式化函数
"""

def test_percentage_format():
    """测试百分比格式化"""
    test_cases = [
        (None, ''),
        (0, ''),
        (0.0, ''),
        (0.1, '10.00%'),
        (0.255, '25.50%'),
        (0.4259, '42.59%'),
        (1.0, '100.00%'),
    ]
    
    print("测试百分比格式化:")
    print("-" * 40)
    
    for input_val, expected in test_cases:
        # 模拟JavaScript的formatPercentage函数
        if input_val is None or input_val == 0 or input_val == 0.0:
            result = ''
        else:
            result = f"{(input_val * 100):.2f}%"
        
        status = "✅" if result == expected else "❌"
        print(f"{status} 输入: {repr(input_val)} -> 输出: {repr(result)} (期望: {repr(expected)})")
    
    print("-" * 40)
    print("测试完成！")

if __name__ == "__main__":
    test_percentage_format()
