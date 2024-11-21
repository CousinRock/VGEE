import ee

def init_earth_engine():
    """初始化 Earth Engine"""
    ee.Authenticate()
    ee.Initialize(project='ee-renjiewu660') 