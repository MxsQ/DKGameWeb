from app import db
from datetime import datetime

class GameOverview(db.Model):
    """游戏概览数据模型"""
    __tablename__ = 'game_overview'
    
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100), nullable=False, comment='游戏名称')
    total_players = db.Column(db.Integer, default=0, comment='总玩家数')
    active_players = db.Column(db.Integer, default=0, comment='活跃玩家数')
    revenue = db.Column(db.Float, default=0.0, comment='收入')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

class DataDetail(db.Model):
    """数据详情模型"""
    __tablename__ = 'data_details'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game_overview.id'), nullable=False, comment='游戏ID')
    data_type = db.Column(db.String(50), nullable=False, comment='数据类型')
    value = db.Column(db.Float, nullable=False, comment='数值')
    date = db.Column(db.Date, nullable=False, comment='日期')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关联关系
    game = db.relationship('GameOverview', backref=db.backref('details', lazy='dynamic')) 