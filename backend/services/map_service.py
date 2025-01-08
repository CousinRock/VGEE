import ee
import time
from scripts.fetch_satellite_dates import fetch_dataset_details

# 使用字典存储每个图层的 dataset
datasets = {}
datasetsNames  ={}
index = 0

def get_dataset(layer_id):
    '''
    获取图层对应的数据集
    '''
    print(f"Map_service.py - get_dataset-layer_id: {layer_id}")
    print(f"Map_service.py - get_dataset-datasets: {datasets}")
    return datasets.get(layer_id)

def get_all_datasets():
    '''
    获取所有图层
    '''
    return datasets,datasetsNames

def save_dataset(layer_id, dataset, layer_name):
    '''
    保存图层
    '''
    datasets[layer_id] = dataset
    datasetsNames[layer_id] = layer_name

def remove_dataset(layer_id):
    '''
    移除图层
    '''
    if layer_id in datasets:
        del datasets[layer_id]
        del datasetsNames[layer_id]
        print(f"Map_service.py - remove_dataset-datasets: {datasets}")

def compute_image_stats(dataset, bands,region=None):
    """
    计算影像的统计信息
    
    Args:
        dataset: ee.Image 对象
        bands: 需要计算统计的波段列表
        region: 可选的计算区域
    
    Returns:
        tuple: (min_value, max_value) 所有波段的全局最小值和最大值
    """
    try:
        if region is None:
            return None
        
        print(f"Map_service.py - compute_image_stats-bands: {bands}")
        band_img = dataset.select(bands)
        
       # 使用 ee.Reducer.minMax 计算每个波段的最小值和最大值
        stats = band_img.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=region,
            scale=150,
            maxPixels=1e13
        )
        
        # 提取字典中的所有键
        keys = stats.keys()

        # 过滤包含 'min' 和 'max' 的键
        min_keys = keys.filter(ee.Filter.stringContains("item", "min"))
        max_keys = keys.filter(ee.Filter.stringContains("item", "max"))

        # 获取所有最小值和最大值
        min_values = min_keys.map(lambda key: ee.Number(ee.Dictionary(stats).get(key)))
        max_values = max_keys.map(lambda key: ee.Number(ee.Dictionary(stats).get(key)))
        
         # 计算全局最小值和最大值
        global_min = ee.Number(min_values.reduce(ee.Reducer.min()))
        global_max = ee.Number(max_values.reduce(ee.Reducer.max()))
        
        # 返回全局最小值和最大值
        return ee.Dictionary({
            "global_min": global_min,
            "global_max": global_max
        })
            
    except Exception as stats_error:
        print(f"Warning: Could not compute image statistics: {stats_error}")
        return None, None

def get_map_data_service(satellite, start_date, end_date, cloud_cover, region=None, layerName=None):
    """获取地图数据服务"""
    try:
        # 移除全局 index 变量，直接使用时间戳作为唯一标识
        layer_id = f"layer-{int(time.time())}-{satellite}"

        # 获取数据集信息
        dataset_info = fetch_dataset_details(satellite)
        if not dataset_info:
            raise ValueError(f"Unsupported satellite type: {satellite}")

        # 获取图像集合
        collection = ee.ImageCollection(satellite)
        first_word = satellite.split('/')[0]

        # 时间过滤
        if start_date and end_date:
            collection = collection.filterDate(start_date, end_date)

        # 云量过滤
        if 'COPERNICUS' in first_word:
            collection = collection.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
        elif 'LANDSAT' in first_word:
            collection = collection.filter(ee.Filter.lt('CLOUD_COVER', cloud_cover))

        # 获取中值图像
        dataset = collection.median()

        # 保存原始波段名称
        original_band_names = dataset.bandNames()

        # 区域裁剪
        if region:
            dataset = dataset.clip(region)

        # 确保波段名称保持一致
        dataset = dataset.rename(original_band_names)

        # 获取可视化参数
        vis_params = {
            'bands': dataset_info['bands'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        }

        # 计算统计值
        stats = compute_image_stats(dataset, vis_params['bands'], region)

        # 如果计算成功，使用计算值
        if stats:
            stats_dict = stats.getInfo()
            img_min = stats_dict.get('global_min')
            img_max = stats_dict.get('global_max')

            # 更新可视化参数
            if 'palette' not in vis_params:
                vis_params.update({
                    'min': img_min,
                    'max': img_max
                })

        # 存储数据集
        layer_name = f"{dataset_info['title']} ({start_date} to {end_date})"
        save_dataset(layer_id, dataset, layerName or layer_name)

        # 获取地图ID
        map_id = dataset.getMapId(vis_params)

        return {
            'center': [20, 0],
            'zoom': 3,
            'baseLayer': {
                'url': 'http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                'subdomains': ['mt0', 'mt1', 'mt2', 'mt3'],
                'attribution': '© Google'
            },
            'overlayLayers': [{
                'name': layer_name,
                'url': map_id['tile_fetcher'].url_format,
                'visible': True,
                'opacity': 1.0,
                'id': layer_id,
                'min': img_min if stats else vis_params.get('min'),
                'max': img_max if stats else vis_params.get('max')
            }],
            'satellite': satellite,
            'visParams': vis_params,
            'type':'Raster'
        }

    except Exception as e:
        print(f"Error in get_map_data_service: {str(e)}")
        return {
            'success': False,
            'message': str(e)
        }