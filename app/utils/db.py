import pymysql


def get_connection():
    """获取到本地MySQL的连接，数据库：game_db，用户root，密码300217"""
    return pymysql.connect(
        host='localhost',
        user='root',
        password='300217',
        database='game_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    ) 