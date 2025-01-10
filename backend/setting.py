import ee
import geemap
import os

def init_earth_engine():
    """初始化 Earth Engine"""
    proxy_config = os.environ.get("PROXY_CONFIG")
    if proxy_config:
        port, project = proxy_config.split(":")  # 按分隔符解析
        print(f"Port: {port}, Project: {project}")
        geemap.set_proxy(port=port)
        ee.Authenticate()
        ee.Initialize(project=project)
    else:
        print("PROXY_CONFIG 环境变量未设置")