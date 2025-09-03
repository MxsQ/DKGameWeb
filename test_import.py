#!/usr/bin/env python3
"""
测试新的导入功能
"""

from app.services.import_service import import_rainbow_excel, check_record_exists
from app.utils.id_utils import generate_game_data_id
from datetime import datetime

def test_import_function():
    """测试导入功能"""
    print("测试导入功能:")
    print("-" * 40)
    
    # 测试记录存在检查
    test_date = datetime.now()
    test_channel = "测试渠道"
    test_id = generate_game_data_id(test_date, test_channel)
    
    print(f"测试记录ID: {test_id}")
    exists = check_record_exists(test_id)
    print(f"记录是否存在: {exists}")
    
    print("-" * 40)
    print("注意：要测试完整导入功能，需要准备一个真实的Excel文件")
    print("文件应包含以下列：日期、渠道、新增用户、DA新增用户、活跃用户等")

if __name__ == "__main__":
    test_import_function()
