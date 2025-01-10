from flask import Flask
from flask_cors import CORS
from routes.map_routes import map_bp
from routes.tool_routes import tool_bp
from routes.layer_routes import layer_bp
from routes.search_routes import search_bp
from routes.upload_routes import upload_bp
from setting import init_earth_engine

app = Flask(__name__)
CORS(app)

def init_app():
    """初始化应用"""
    # 初始化 Earth Engine
    init_earth_engine()

    # 注册路由蓝图
    app.register_blueprint(map_bp)
    app.register_blueprint(layer_bp)
    app.register_blueprint(tool_bp, url_prefix='/tools')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(upload_bp, url_prefix='/upload')

if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=5000)
