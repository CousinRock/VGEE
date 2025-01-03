import os
import sys
# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests
from bs4 import BeautifulSoup
from config.satellite_config import SATELLITE_CONFIGS
import re
from datetime import datetime
import ee

def parse_date(date_str):
    """解析GEE日期格式为年份"""
    try:
        return datetime.strptime(date_str.split('T')[0], '%Y-%m-%d').strftime('%Y-%m-%d')
    except:
        return None

def get_dataset_bands(collection_id):
    """获取数据集的波段信息"""
    try:     
        # 获取一个示例影像
        collection = ee.ImageCollection(collection_id)
        first_image = ee.Image(collection.median())
        band_names = first_image.bandNames().getInfo()
        
        if len(band_names) >= 3:
            # 如果有3个或以上波段，返回前三个波段
            return band_names[:3]
        elif len(band_names) > 0:
            # 如果只有一个或两个波段，返回第一个波段
            return [band_names[0]]
        else:
            return ['B1']  # 默认返回 B1
            
    except Exception as e:
        print(f"Error getting bands for {collection_id}: {str(e)}")
        return ['B1']  # 出错时返回默认波段

def fetch_dataset_availability(collection_id):
    """获取数据集的可用时间范围"""
    # 从collection ID构建URL
    base_url = "https://developers.google.com/earth-engine/datasets/catalog/"
    url = base_url + collection_id.replace('/', '_')
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找数据集可用性信息
            availability_dt = soup.find('dt', string="Dataset Availability")
            if availability_dt:
                availability_dd = availability_dt.find_next_sibling('dd')
                if availability_dd:
                    time_range = availability_dd.text.strip()
                    # 使用正则表达式提取日期
                    dates = re.findall(r'(\d{4}-\d{2}-\d{2})T', time_range)
                    print(dates)
                    if len(dates) >= 2:
                        start_date = parse_date(dates[0])
                        end_date = parse_date(dates[1])
                        return start_date, end_date
    except Exception as e:
        print(f"Error fetching data for {collection_id}: {str(e)}")
    
    return None, None

def update_satellite_configs():
    """更新卫星配置的时间范围和波段信息"""
    updated_configs = {}
    
    for sat_id, config in SATELLITE_CONFIGS.items():
        collection = config.get('collection')
        if collection:
            print(f"Fetching information for {sat_id}...")
            
            # 获取时间范围
            start_date, end_date = fetch_dataset_availability(collection)
            if start_date:
                print(f"{sat_id} dates: {start_date} - {end_date or 'present'}")
                config['start_date'] = start_date
                config['end_date'] = end_date
            
            # 获取波段信息
            bands = get_dataset_bands(collection)
            print(f"{sat_id} bands: {bands}")
            if 'vis_params' in config:
                config['vis_params']['bands'] = bands
            
        updated_configs[sat_id] = config
    
    return updated_configs

