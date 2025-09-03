from flask import Flask
from config import config

def create_app(config_name='default'):
    """创建Flask应用实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 注册蓝图
    from .views import main_bp
    app.register_blueprint(main_bp)
    
    return app 