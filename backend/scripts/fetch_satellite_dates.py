import os
import sys
# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import ee
import geemap
from config.satellite_config import SATELLITE_CONFIGS

def parse_date(date_str):
    """解析GEE日期格式为年份"""
    try:
        return date_str.split('T')[0]
    except:
        return None

def fetch_dataset_details(collection_id):
    """使用 geemap 获取数据集的详细信息，包括可用时间范围和波段信息"""
    try:
        datasets = geemap.search_ee_data(collection_id)
        for dataset in datasets:
            if dataset['id'] == collection_id:
                # 获取波段信息
                if dataset['type'] == 'image_collection':
                    collection = ee.ImageCollection(collection_id)
                
                    first_image = ee.Image(collection.first())
                    band_names = first_image.bandNames().getInfo()
                    bands = band_names[:3] if len(band_names) >= 3 else band_names
                elif dataset['type'] == 'image':
                    image = ee.Image(collection_id)
                    band_names = image.bandNames().getInfo()
                    bands = band_names[:3] if len(band_names) >= 3 else band_names

                return {
                    'id': dataset['id'],
                    'title': dataset['title'],
                    'start_date': dataset['start_date'],
                    'end_date': dataset['end_date'],
                    'bands': bands,
                    'provider': dataset['provider'],
                    'tags': dataset['tags'],
                    'thumbnail_url': dataset['thumbnail_url'],
                    'asset_url': dataset['asset_url'],
                    'type': dataset['type']
                }
    except Exception as e:
        print(f"Error fetching data for {collection_id}: {str(e)}")
    return None

