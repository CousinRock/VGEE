import ee

# 使用字典存储每个图层的 dataset
datasets = {}
datasetsNames  ={}
index = 0

def get_dataset(layer_id):
    '''
    获取图层对应的数据集
    '''
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
        
        band_img = dataset.select(bands)
        # 如果没有指定region，使用全球范围
        
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

def get_map_data_service(satellite, start_date, end_date, cloud_cover, region=None,layerName=None):
    """获取地图数据服务"""
    try:
        global index
        index += 1
        layer_id = f"layer-{index}-{satellite}"
        print(f"Map_service.py - Generated layer ID: {layer_id}")
        
        # 根据不同的卫星类型返回不同的数据
        if satellite == 'LANDSAT':
            dataset = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA') \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUD_COVER', cloud_cover))
            
            dataset = dataset.median()
            
            # 保存原始波段名称
            original_band_names = dataset.bandNames()
            
            if region:
                dataset = dataset.clip(region)
                
            # 确保波段名称保持一致
            dataset = dataset.rename(original_band_names)
                
            vis_params = {
                'bands': ['B4', 'B3', 'B2'],
                'min': 0,
                'max': 0.3,
                'gamma': 1.4
            }
            layer_name = f'Landsat 8 ({start_date} to {end_date})'
            
        elif satellite == 'SENTINEL':
            dataset = ee.ImageCollection('COPERNICUS/S2_SR') \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
                
            dataset = dataset.median()
            
            # 保存原始波段名称
            original_band_names = dataset.bandNames()
            
            if region:
                dataset = dataset.clip(region)
                
            # 确保波段名称保持一致
            dataset = dataset.rename(original_band_names)
                
            vis_params = {
                'bands': ['B4', 'B3', 'B2'],
                'min': 0,
                'max': 3000,
                'gamma': 1.4
            }
            layer_name = f'Sentinel-2 ({start_date} to {end_date})'
            
        else:  # MODIS
            dataset = ee.ImageCollection('MODIS/006/MOD13A2') \
                .filterDate(start_date, end_date)
                
            dataset = dataset.first()
            
            # 保存原始波段名称
            original_band_names = dataset.bandNames()
            
            if region:
                dataset = dataset.clip(region)
                
            # 确保波段名称保持一致
            dataset = dataset.rename(original_band_names)
                
            vis_params = {
                'min': -2000,
                'max': 10000,
                'bands': ['NDVI'],
                'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', 
                           '99B718', '74A901', '66A000', '529400', '3E8601', 
                           '207401', '056201', '004C00', '023B01', '012E01', 
                           '011D01', '011301']
            }
            layer_name = f'MODIS NDVI ({start_date} to {end_date})'

        # 打印波段信息用于调试
        print(f"Map_service.py - Dataset bands: {dataset.bandNames().getInfo()}")

        # 计算统计值
        stats = compute_image_stats(dataset, vis_params['bands'], region)
        
        # 如果计算成功,使用计算值
        if stats:
            stats_dict = stats.getInfo()  # 只调用一次 getInfo
            img_min = stats_dict.get('global_min')
            img_max = stats_dict.get('global_max')
        else:
            # 使用默认值
            if satellite == 'LANDSAT':
                img_min, img_max = 0, 1
            elif satellite == 'SENTINEL':
                img_min, img_max = 0, 3000
            else:  # MODIS
                img_min, img_max = -2000, 10000

        print(f"Map_service.py - Final stats: min={img_min}, max={img_max}")

        # 存储 dataset
        save_dataset(layer_id, dataset, layerName)

        map_id = dataset.getMapId(vis_params)
        tile_url = map_id['tile_fetcher'].url_format
        
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
                'url': tile_url,
                'visible': True,
                'opacity': 1.0,
                'id': layer_id,
                'min': img_min,
                'max': img_max
            }],
            'satellite': satellite,
            'visParams': vis_params
        }
        
    except Exception as e:
        raise Exception(f"Map_service.py - Error in get_map_data_service: {str(e)}")