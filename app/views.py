from flask import Blueprint, render_template, jsonify, request
import hashlib
import pymysql
import os
import tempfile
import json
from datetime import datetime
from app.services.game_service import list_games, add_game, get_game_data, aggregate_game_data, get_channel_analysis_data
from app.services.import_service import import_rainbow_excel

main_bp = Blueprint('main', __name__)

# 假数据
MOCK_GAMES = [
    {
        'id': 1,
        'game_name': '王者荣耀',
        'total_players': 1500000,
        'active_players': 850000,
        'revenue': 1250000.50,
        'created_at': '2024-01-15',
        'updated_at': '2024-08-19 14:30:00'
    },
    {
        'id': 2,
        'game_name': '和平精英',
        'total_players': 980000,
        'active_players': 520000,
        'revenue': 890000.75,
        'created_at': '2024-02-20',
        'updated_at': '2024-08-19 14:30:00'
    },
    {
        'id': 3,
        'game_name': '原神',
        'total_players': 750000,
        'active_players': 380000,
        'revenue': 2100000.00,
        'created_at': '2024-03-10',
        'updated_at': '2024-08-19 14:30:00'
    },
    {
        'id': 4,
        'game_name': '英雄联盟手游',
        'total_players': 1200000,
        'active_players': 650000,
        'revenue': 1560000.25,
        'created_at': '2024-04-05',
        'updated_at': '2024-08-19 14:30:00'
    }
]

@main_bp.route('/')
def index():
    """首页 - 游戏概览"""
    return render_template('index.html', games=MOCK_GAMES)

@main_bp.route('/game-overview')
def game_overview():
    """游戏概览页面"""
    return render_template('game_overview.html', games=MOCK_GAMES)

@main_bp.route('/data-details')
def data_details():
    """数据详情页面"""
    return render_template('data_details.html')

@main_bp.route('/channel-analysis')
def channel_analysis():
    """渠道分析页面"""
    return render_template('channel_analysis.html')

@main_bp.route('/data-entry')
def data_entry():
    """数据录入页面"""
    return render_template('data_entry.html')

@main_bp.route('/config')
def config_page():
    """配置页面（游戏配置）"""
    return render_template('config.html')

@main_bp.route('/api/games', methods=['GET'])
def api_games():
    """获取游戏数据的API接口（仍返回假数据）"""
    return jsonify([{
        'id': game['id'],
        'name': game['game_name'],
        'total_players': game['total_players'],
        'active_players': game['active_players'],
        'revenue': game['revenue']
    } for game in MOCK_GAMES])

@main_bp.route('/api/games/all', methods=['GET'])
def api_games_all():
    """返回数据库中的所有游戏，用于下拉选项"""
    return jsonify(list_games())

@main_bp.route('/api/games', methods=['POST'])
def api_add_game():
    """增加游戏：将游戏写入MySQL的game_db库的game表，id为name的32位md5"""
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'message': 'name必填'}), 400
    try:
        result = add_game(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'message': '数据库错误', 'error': str(e)}), 500

@main_bp.route('/api/import/rainbow', methods=['POST'])
def api_import_rainbow():
    """导入彩虹数据：接收FormData(game_id,file)，保存临时文件，调用导入服务"""
    game_id = (request.form.get('game_id') or '').strip()
    f = request.files.get('file')
    if not game_id:
        return jsonify({'message': 'game_id必填'}), 400
    if not f:
        return jsonify({'message': 'file必传'}), 400

    # 保存到临时文件
    suffix = os.path.splitext(f.filename)[1] or '.xlsx'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        f.save(tmp.name)
        tmp_path = tmp.name
    try:
        result = import_rainbow_excel(tmp_path, game_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': '导入失败', 'error': str(e)}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

@main_bp.route('/api/game-data', methods=['GET'])
def api_game_data():
    """获取游戏数据，支持时间段筛选和聚合"""
    # 获取查询参数
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    game_id = request.args.get('game_id')
    time_group = request.args.get('time_group', 'day')  # day/week/month
    channel_group = request.args.get('channel_group', 'category')  # category/channel
    
    # 解析日期
    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': '开始日期格式错误'}), 400
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': '结束日期格式错误'}), 400
    
    try:
        # 根据聚合参数选择查询方式
        if time_group == 'day' and channel_group == 'category':
            # 使用原始查询（保持向后兼容）
            data = get_game_data(start_date, end_date, game_id)
        else:
            # 使用聚合查询
            data = aggregate_game_data(start_date, end_date, game_id, time_group, channel_group)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'message': '获取数据失败', 'error': str(e)}), 500

@main_bp.route('/api/channel-config', methods=['GET'])
def api_channel_config():
    """获取渠道配置信息"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'message': '获取配置失败', 'error': str(e)}), 500

@main_bp.route('/api/channel-analysis', methods=['GET'])
def api_channel_analysis():
    """获取渠道分析数据"""
    # 获取查询参数
    channel = request.args.get('channel')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    time_group = request.args.get('time_group', 'day')
    
    if not channel:
        return jsonify({'message': '渠道参数必填'}), 400
    
    # 解析日期
    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': '开始日期格式错误'}), 400
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': '结束日期格式错误'}), 400
    
    try:
        # 获取渠道分析数据
        data = get_channel_analysis_data(channel, start_date, end_date, time_group)
        return jsonify(data)
    except Exception as e:
        return jsonify({'message': '获取渠道数据失败', 'error': str(e)}), 500 