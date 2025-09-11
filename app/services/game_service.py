from typing import List, Dict
from app.utils.db import get_connection
from app.utils.id_utils import generate_game_id
from app.services.import_service import ensure_game_data_table


def ensure_game_table():
    sql = (
        'CREATE TABLE IF NOT EXISTS `game` ('
        '  `id` VARCHAR(64) PRIMARY KEY,'
        '  `name` VARCHAR(255) NOT NULL'
        ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'
    )
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def list_games() -> List[Dict]:
    """查询所有游戏，返回列表[{id,name}]"""
    ensure_game_table()
    sql = 'SELECT id, name FROM `game` ORDER BY name ASC'
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return list(cur.fetchall())


def add_game(name: str) -> Dict:
    """添加或更新游戏记录，id为name的32位md5，返回{id,name}"""
    ensure_game_table()
    game_id = generate_game_id(name)
    sql = 'INSERT INTO `game` (`id`, `name`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);'
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (game_id, name))
        conn.commit()
    return {'id': game_id, 'name': name}


def get_game_data(start_date=None, end_date=None, game_id=None):
    """获取游戏数据，支持时间段和游戏ID筛选"""
    ensure_game_data_table()
    
    # 默认查询近一周数据
    if not start_date:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
    
    sql = """
        SELECT 
            gd.channel,
            gd.date,
            gd.category,
            gd.newUser,
            gd.daNewUser,
            gd.active,
            gd.payUser,
            gd.gain,
            gd.ARPU,
            gd.DAY1,
            gd.DAY7,
            g.name as game_name
        FROM gameData gd
        LEFT JOIN game g ON gd.gameID = g.id
        WHERE gd.date >= %s AND gd.date <= %s
    """
    params = [start_date, end_date]
    
    if game_id:
        sql += " AND gd.gameID = %s"
        params.append(game_id)
    
    sql += " ORDER BY gd.date DESC, gd.channel ASC"
    
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = list(cur.fetchall())

    # 将日期字段序列化为字符串，避免前端解析失败
    serialized = []
    for r in rows:
        item = dict(r)
        d = item.get('date')
        if d is not None:
            try:
                item['date'] = d.strftime('%Y-%m-%d')
            except Exception:
                item['date'] = str(d)
        serialized.append(item)
    return serialized





def aggregate_game_data(start_date=None, end_date=None, game_id=None, 
                       time_group='day', channel_group='category'):
    """获取聚合后的游戏数据"""
    from .bind_data_service import bind_data_by_dimensions
    
    ensure_game_data_table()
    
    # 默认查询近一周数据
    if not start_date:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
    
    # 构建基础查询
    base_sql = """
        SELECT 
            gd.channel,
            gd.date,
            gd.category,
            gd.newUser,
            gd.daNewUser,
            gd.active,
            gd.payUser,
            gd.gain,
            gd.ARPU,
            gd.DAY1,
            gd.DAY7,
            g.name as game_name
        FROM gameData gd
        LEFT JOIN game g ON gd.gameID = g.id
        WHERE gd.date >= %s AND gd.date <= %s
    """
    params = [start_date, end_date]
    
    if game_id:
        base_sql += " AND gd.gameID = %s"
        params.append(game_id)
    
    base_sql += " ORDER BY gd.date DESC, gd.channel ASC"
    
    # 获取原始数据
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(base_sql, params)
            raw_data = list(cur.fetchall())
    
    if not raw_data:
        return []
    
    # 使用数据绑定服务进行聚合
    return bind_data_by_dimensions(raw_data, time_group, channel_group)


def get_channel_analysis_data(channel, start_date=None, end_date=None, time_group='day'):
    """获取指定渠道的分析数据，支持渠道分组"""
    from .bind_data_service import bind_data_by_dimensions, normalize_channel_name
    
    ensure_game_data_table()
    
    # 默认查询近一周数据
    if not start_date:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
    
    # 获取所有渠道，然后筛选出与指定渠道分组匹配的渠道
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # 先获取所有渠道
            cur.execute("SELECT DISTINCT channel FROM gameData")
            all_channels = [row['channel'] if isinstance(row, dict) else row[0] for row in cur.fetchall()]
            
            # 筛选出与指定渠道分组匹配的渠道
            matching_channels = []
            for db_channel in all_channels:
                if normalize_channel_name(db_channel) == normalize_channel_name(channel):
                    matching_channels.append(db_channel)
            
            if not matching_channels:
                return []
            
            # 构建查询SQL，使用IN子句查询所有匹配的渠道
            placeholders = ','.join(['%s'] * len(matching_channels))
            sql = f"""
                SELECT 
                    gd.channel,
                    gd.date,
                    gd.category,
                    gd.newUser,
                    gd.daNewUser,
                    gd.active,
                    gd.payUser,
                    gd.gain,
                    gd.ARPU,
                    gd.DAY1,
                    gd.DAY7,
                    g.name as game_name
                FROM gameData gd
                LEFT JOIN game g ON gd.gameID = g.id
                WHERE gd.date >= %s AND gd.date <= %s
                AND gd.channel IN ({placeholders})
                ORDER BY gd.date DESC, gd.channel ASC
            """
            params = [start_date, end_date] + matching_channels
            
            cur.execute(sql, params)
            raw_data = list(cur.fetchall())
    
    if not raw_data:
        return []
    
    # 使用数据绑定服务进行聚合，分组维度固定为渠道
    return bind_data_by_dimensions(raw_data, time_group, 'channel') 