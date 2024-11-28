import ee

# 使用字典存储每个图层的 dataset
datasets = {}
datasetsNames  ={}
index = 0

def get_dataset(layer_id):
    '''
    获取图层
    '''
    print('datasets: ', datasets)
    return datasets.get(layer_id)

def get_all_datasets():
    '''
    获取所有图层
    '''
    return datasets,datasetsNames

def remove_dataset(layer_id):
    '''
    移除图层
    '''
    if layer_id in datasets:
        del datasets[layer_id]
        del datasetsNames[layer_id]
        print(f"remove_dataset-datasets: {datasets}")

def get_map_data_service(satellite, start_date, end_date, cloud_cover, region=None,layerName=None):
    """获取地图数据服务"""
    try:
        global index
        # 生成唯一的图层ID
        index += 1
        layer_id = f"layer-{index}-{satellite}"
        print(f"Generated layer ID: {layer_id}")
        
        # 根据不同的卫星类型返回不同的数据
        if satellite == 'LANDSAT':
            dataset = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA') \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUD_COVER', cloud_cover))
            
            dataset = dataset.median()
            
            if region:
                dataset = dataset.clip(region)
                
                
            vis_params = {
                'bands': ['B4', 'B3', 'B2'],
                'min': 0,
                'max': 0.3
            }
            layer_name = f'Landsat 8 ({start_date} to {end_date})'
            
        elif satellite == 'SENTINEL':
            dataset = ee.ImageCollection('COPERNICUS/S2_SR') \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
                
            dataset = dataset.median()
            
            if region:
                dataset = dataset.clip(region)
                
                
            vis_params = {
                'bands': ['B4', 'B3', 'B2'],
                'min': 0,
                'max': 3000
            }
            layer_name = f'Sentinel-2 ({start_date} to {end_date})'
            
        else:  # MODIS
            dataset = ee.ImageCollection('MODIS/006/MOD13A2') \
                .filterDate(start_date, end_date)
                
            dataset = dataset.first()
            
            if region:
                dataset = dataset.clip(region)
                
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

        # 存储 dataset
        datasets[layer_id] = dataset
        datasetsNames[layer_id] = layerName

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
                'id': layer_id  # 返回图层ID
            }],
            'satellite': satellite,
            'visParams': vis_params
        }
        
    except Exception as e:
        raise Exception(f"Error in get_map_data_service: {str(e)}") 