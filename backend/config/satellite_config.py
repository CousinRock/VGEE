import json
import os

# 获取当前文件所在目录的路径
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(CONFIG_DIR, 'satellite_configs.json')

def load_satellite_configs():
    """从 JSON 文件加载卫星配置"""
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('satellites', [])
    except FileNotFoundError:
        # 如果文件不存在，创建默认配置
        default_configs = {
            "satellites": [
                "LANDSAT/LT05/C02/T1_TOA",
                "LANDSAT/LE07/C02/T1_TOA",
                "LANDSAT/LC08/C02/T1_TOA",
                "LANDSAT/LC09/C02/T1_TOA",
                "COPERNICUS/S2_HARMONIZED"
            ]
        }
        save_satellite_configs(default_configs['satellites'])
        return default_configs['satellites']

def save_satellite_configs(satellites):
    """保存卫星配置到 JSON 文件"""
    try:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump({"satellites": satellites}, f, indent=4)
    except Exception as e:
        print(f"Error saving satellite configs: {str(e)}")

# 导出卫星配置
SATELLITE_CONFIGS = load_satellite_configs()