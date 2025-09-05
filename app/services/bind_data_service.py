#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据绑定服务
负责将原始数据按照时间维度和分组维度进行合并
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any


def normalize_channel_name(channel: str) -> str:
    """标准化渠道名称，用于渠道合并"""
    if not channel:
        return '未知'
    
    # 使用正则表达式提取渠道名称的主要部分
    import re
    # 匹配类似 "田地CPS-1", "田地CPS-2" 等，提取 "田地CPS"
    match = re.match(r'^(.+?)(?:-\d+)?$', channel.strip())
    
    if match:
        return match.group(1).strip()
    return channel.strip()


def bind_data_by_dimensions(raw_data: List[Dict[str, Any]], 
                           time_group: str = 'day', 
                           channel_group: str = 'category') -> List[Dict[str, Any]]:
    """
    根据时间维度和分组维度合并数据
    
    Args:
        raw_data: 原始数据列表
        time_group: 时间维度 ('day', 'week', 'month')
        channel_group: 分组维度 ('category', 'channel')
    
    Returns:
        合并后的数据列表
    """
    if not raw_data:
        return []
    
    # 数据聚合处理
    aggregated_data = {}
    
    for row in raw_data:
        # 确定时间分组键
        time_key = _get_time_key(row['date'], time_group)
        
        # 确定渠道分组键
        channel_key = _get_channel_key(row, channel_group)
        
        # 组合键
        group_key = f"{time_key}|{channel_key}"
        
        if group_key not in aggregated_data:
            # 格式化显示日期
            display_date = _format_display_date(time_key, time_group)
            
            aggregated_data[group_key] = {
                'date': display_date,
                'channel': channel_key,
                'category': row['category'],
                'newUser': 0,
                'daNewUser': 0,
                'active': 0,
                'payUser': 0,
                'gain': 0.0,
                'ARPU': 0.0,
                'ARPPU': 0.0,
                'DAY1': 0.0,
                'DAY7': 0.0,
                'total_retention1': 0.0,  # 用于计算加权平均
                'total_retention7': 0.0,  # 用于计算加权平均
                'game_name': row['game_name']
            }
        
        # 累加数值
        agg = aggregated_data[group_key]
        agg['newUser'] += row['newUser'] or 0
        agg['daNewUser'] += row['daNewUser'] or 0
        agg['active'] += row['active'] or 0
        agg['payUser'] += row['payUser'] or 0
        agg['gain'] += row['gain'] or 0.0
        
        # 处理留存数据（空值当0处理）
        day1_val = row['DAY1'] or 0.0
        day7_val = row['DAY7'] or 0.0
        new_user_val = row['newUser'] or 0
        
        # 计算留存贡献
        agg['total_retention1'] += day1_val * new_user_val
        agg['total_retention7'] += day7_val * new_user_val
    
    # 计算最终的留存率和ARPU
    result = []
    for group_key, agg in aggregated_data.items():
        # 计算加权平均留存率
        if agg['newUser'] > 0:
            agg['DAY1'] = agg['total_retention1'] / agg['newUser']
            agg['DAY7'] = agg['total_retention7'] / agg['newUser']
        else:
            agg['DAY1'] = 0.0
            agg['DAY7'] = 0.0
        
        # 计算ARPU = 收入总值 / 总活跃用户，保留两位小数
        if agg['active'] > 0:
            agg['ARPU'] = round(agg['gain'] / agg['active'], 2)
        else:
            agg['ARPU'] = 0.0
        
        # 计算ARPPU = 收入总值 / 总付费用户，保留两位小数
        if agg['payUser'] > 0:
            agg['ARPPU'] = round(agg['gain'] / agg['payUser'], 2)
        else:
            agg['ARPPU'] = 0.0
        
        # 移除临时字段
        del agg['total_retention1']
        del agg['total_retention7']
        
        result.append(agg)
    
    # 按日期和渠道排序
    result.sort(key=lambda x: (x['date'], x['channel']), reverse=True)
    
    return result


def _get_time_key(date_obj: datetime, time_group: str) -> str:
    """获取时间分组键"""
    if time_group == 'day':
        return date_obj.strftime('%Y-%m-%d')
    elif time_group == 'week':
        # 计算周数（简化实现，以周一为一周开始）
        days_since_monday = date_obj.weekday()
        monday = date_obj - timedelta(days=days_since_monday)
        return monday.strftime('%Y-%m-%d')
    elif time_group == 'month':
        return date_obj.strftime('%Y-%m')
    else:
        return date_obj.strftime('%Y-%m-%d')


def _get_channel_key(row: Dict[str, Any], channel_group: str) -> str:
    """获取渠道分组键"""
    if channel_group == 'category':
        # 当选择"分包"时，按渠道字段分组（标准化后）
        return normalize_channel_name(row['channel']) or '未知'
    else:  # channel
        # 当选择"渠道"时，按渠道字段分组（标准化后）
        return normalize_channel_name(row['channel']) or '未知'


def _format_display_date(time_key: str, time_group: str) -> str:
    """格式化显示日期"""
    if time_group == 'week':
        # 周维度显示为月/日-月/日格式
        monday_date = datetime.strptime(time_key, '%Y-%m-%d')
        sunday_date = monday_date + timedelta(days=6)
        return f"{monday_date.month}/{monday_date.day}-{sunday_date.month}/{sunday_date.day}"
    else:
        return time_key
