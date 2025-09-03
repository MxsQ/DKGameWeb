import hashlib
from datetime import datetime
from typing import Union


def md5_32(value: str) -> str:
    """生成32位MD5字符串"""
    return hashlib.md5(value.encode('utf-8')).hexdigest()


def generate_game_id(game_name: str) -> str:
    """根据游戏名生成游戏ID（32位MD5）"""
    normalized = (game_name or '').strip()
    return md5_32(normalized)


def generate_game_data_id(date_value: Union[str, datetime], channel: str) -> str:
    """根据日期与渠道生成 gameData 的唯一ID（32位MD5）"""
    if isinstance(date_value, datetime):
        date_str = date_value.strftime('%Y-%m-%d')
    else:
        date_str = str(date_value).strip()
    channel_str = (channel or '').strip()
    return md5_32(f"{date_str}{channel_str}") 