from flask import Flask
from flask_cors import CORS
from routes.map_routes import map_bp
from routes.tool_routes import tool_bp
from routes.layer_routes import layer_bp
from setting import init_earth_engine
from scripts.fetch_satellite_dates import update_satellite_configs
from config.satellite_config import SATELLITE_CONFIGS

app = Flask(__name__)
CORS(app)

def init_app():
    """初始化应用"""
    # 初始化 Earth Engine
    init_earth_engine()
    
    # 更新卫星时间范围
    try:
        updated_configs = update_satellite_configs()
        # 更新全局配置
        SATELLITE_CONFIGS.update(updated_configs)
        print(SATELLITE_CONFIGS)
    except Exception as e:
        print(f"Warning: Failed to update satellite date ranges: {e}")
        print("Using default date ranges from config")

    # 注册路由蓝图
    app.register_blueprint(map_bp)
    app.register_blueprint(layer_bp)
    app.register_blueprint(tool_bp, url_prefix='/tools')

if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
