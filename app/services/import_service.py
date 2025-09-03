from typing import Dict
from datetime import datetime
import openpyxl
from app.utils.db import get_connection
from app.utils.id_utils import generate_game_data_id

# gameData 表（按 db.mdc 扩展需求）：
# id, gameID, date, category, channel, daNewUser, newUser, active, payUser, gain, ARPU, ARPPU, DAY1


def ensure_game_data_table():
    sql = (
        'CREATE TABLE IF NOT EXISTS `gameData` ('
        '  `id` VARCHAR(32) PRIMARY KEY,'
        '  `gameID` VARCHAR(32) NOT NULL,'
        '  `date` DATETIME,'
        '  `category` VARCHAR(64),'
        '  `channel` VARCHAR(128),'
        '  `daNewUser` INT,'
        '  `newUser` INT,'
        '  `active` INT,'
        '  `payUser` INT,'
        '  `gain` DOUBLE,'
        '  `ARPU` DOUBLE,'
        '  `ARPPU` DOUBLE,'
        '  `DAY1` DOUBLE,'
        '  `DAY7` DOUBLE'
        ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'
    )
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


HEADER_TO_FIELD = {
    '日期': 'date',
    '渠道': 'channel',
    '新增用户': 'newUser',
    'DA新增用户': 'daNewUser',
    '活跃用户': 'active',
    '新增留存_新增次留率': 'DAY1',
    '新增留存_新增7留率': 'DAY7',
    '付费数据_付费用户': 'payUser',
    '付费数据_收入': 'gain',
    '付费数据_ARPU': 'ARPU',
    '付费数据_ARPPU': 'ARPPU',
}


def parse_date(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d'):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
    raise ValueError('无法解析日期')


def parse_int(value):
    if value is None:
        return 0
    s = str(value).strip()
    if s == '':
        return 0
    s = s.replace(',', '')
    if s.endswith('%'):
        s = s[:-1]
    try:
        return int(float(s))
    except Exception:
        return 0


def parse_float(value):
    if value is None:
        return 0.0
    s = str(value).strip()
    if s == '':
        return 0.0
    s = s.replace(',', '')
    is_percentage = s.endswith('%')
    if is_percentage:
        s = s[:-1]  # 去掉百分号
    try:
        float_val = float(s)
        if is_percentage:
            return float_val / 100.0  # 将百分比转换为小数
        return float_val
    except Exception:
        try:
            float_val = float(int(s))
            if is_percentage:
                return float_val / 100.0  # 将百分比转换为小数
            return float_val
        except Exception:
            return 0.0


def check_record_exists(record_id: str) -> bool:
    """检查记录是否已存在"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) as count FROM `gameData` WHERE `id` = %s', (record_id,))
            result = cur.fetchone()
            return result['count'] > 0


def import_rainbow_excel(file_path: str, game_id: str) -> Dict:
    """导入彩虹数据excel，返回详细的导入统计信息"""
    ensure_game_data_table()

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active

    header_row = [cell.value if cell.value is not None else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    header_index: Dict[str, int] = {}
    for idx, title in enumerate(header_row):
        title_str = str(title).strip()
        if title_str in HEADER_TO_FIELD:
            header_index[HEADER_TO_FIELD[title_str]] = idx

    required = ['date', 'channel']
    missing = [k for k in required if k not in header_index]
    if missing:
        raise ValueError('缺少必要列: ' + ','.join(missing))

    # 准备批量插入的数据
    insert_data = []
    update_data = []
    
    # 先收集所有要处理的数据
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row is None:
            continue
        raw_date = row[header_index['date']]
        raw_channel = row[header_index['channel']]
        if raw_channel is None:
            continue
            
        date_val = parse_date(raw_date)
        channel_val = str(raw_channel).strip()
        row_id = generate_game_data_id(date_val, channel_val)

        # daNewUser 优先取"DA新增用户"，否则回退取"新增用户"
        if 'daNewUser' in header_index:
            da_new_user_val = parse_int(row[header_index.get('daNewUser')])
        elif 'newUser' in header_index:
            da_new_user_val = parse_int(row[header_index.get('newUser')])
        else:
            da_new_user_val = 0

        params = (
            row_id,
            game_id,
            date_val,
            '官包',
            channel_val,
            da_new_user_val,
            parse_int(row[header_index.get('newUser')]) if 'newUser' in header_index else 0,
            parse_int(row[header_index.get('active')]) if 'active' in header_index else 0,
            parse_int(row[header_index.get('payUser')]) if 'payUser' in header_index else 0,
            parse_float(row[header_index.get('gain')]) if 'gain' in header_index else 0.0,
            parse_float(row[header_index.get('ARPU')]) if 'ARPU' in header_index else 0.0,
            parse_float(row[header_index.get('ARPPU')]) if 'ARPPU' in header_index else 0.0,
            parse_float(row[header_index.get('DAY1')]) if 'DAY1' in header_index else 0.0,
            parse_float(row[header_index.get('DAY7')]) if 'DAY7' in header_index else 0.0,
        )
        
        # 检查记录是否已存在
        if check_record_exists(row_id):
            update_data.append(params)
        else:
            insert_data.append(params)

    # 批量执行插入和更新
    inserted_count = 0
    updated_count = 0
    
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # 批量插入新记录
            if insert_data:
                insert_sql = (
                    'INSERT INTO `gameData` '
                    '(`id`,`gameID`,`date`,`category`,`channel`,`daNewUser`,`newUser`,`active`,`payUser`,`gain`,`ARPU`,`ARPPU`,`DAY1`,`DAY7`) '
                    'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                )
                cur.executemany(insert_sql, insert_data)
                inserted_count = len(insert_data)
            
            # 批量更新已存在的记录
            if update_data:
                update_sql = (
                    'UPDATE `gameData` SET '
                    '`gameID`=%s,`date`=%s,`category`=%s,`channel`=%s,`daNewUser`=%s,`newUser`=%s,`active`=%s,'
                    '`payUser`=%s,`gain`=%s,`ARPU`=%s,`ARPPU`=%s,`DAY1`=%s,`DAY7`=%s '
                    'WHERE `id`=%s'
                )
                # 重新排列参数顺序：将id放在最后
                update_params = []
                for params in update_data:
                    # params[0]是id，需要移到最后
                    update_params.append(params[1:] + (params[0],))
                
                cur.executemany(update_sql, update_params)
                updated_count = len(update_data)
        
        conn.commit()

    return {
        'inserted': inserted_count,
        'updated': updated_count,
        'total': inserted_count + updated_count
    } 