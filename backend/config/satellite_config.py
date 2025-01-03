# 卫星数据源配置
SATELLITE_CONFIGS = {
    # Landsat 系列
    'LANDSAT-5': {
        'collection': 'LANDSAT/LT05/C02/T1_TOA',
        'start_date': None,
        'end_date': None,
        'vis_params': {
            'bands': ['B3', 'B2', 'B1'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        },
        'cloud_band': 'QA_PIXEL',
        'name_template': 'Landsat 5 ({start_date} to {end_date})'
    },
    'LANDSAT-7': {
        'collection': 'LANDSAT/LE07/C02/T1_TOA',
        'start_date': None,
        'end_date': None,
        'vis_params': {
            'bands': ['B3', 'B2', 'B1'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        },
        'cloud_band': 'QA_PIXEL',
        'name_template': 'Landsat 7 ({start_date} to {end_date})'
    },
    'LANDSAT-8': {
        'collection': 'LANDSAT/LC08/C02/T1_TOA',
        'start_date': None,
        'end_date': None,  # 持续更新
        'vis_params': {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        },
        'cloud_band': 'QA_PIXEL',
        'name_template': 'Landsat 8 ({start_date} to {end_date})'
    },
    'LANDSAT-9': {
        'collection': 'LANDSAT/LC09/C02/T1_TOA',
        'start_date': None,
        'end_date': None,
        'vis_params': {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        },
        'cloud_band': 'QA_PIXEL',
        'name_template': 'Landsat 9 ({start_date} to {end_date})'
    },
    
    # Sentinel 系列
    'SENTINEL-2': {
        'collection': 'COPERNICUS/S2_HARMONIZED',
        'start_date': None,
        'end_date': None,
        'vis_params': {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 3000,
            'gamma': 1.4
        },
        'cloud_band': 'QA60',
        'name_template': 'Sentinel-2 ({start_date} to {end_date})'
    },
    
    # MODIS 系列
    'MODIS-NDVI': {
        'collection': 'MODIS/006/MOD13A2',
        'start_date': None,
        'end_date': None,
        'vis_params': {
            'bands': ['NDVI'],
            'min': -2000,
            'max': 10000,
            'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', 
                       '99B718', '74A901', '66A000', '529400', '3E8601', 
                       '207401', '056201', '004C00', '023B01', '012E01', 
                       '011D01', '011301']
        },
        'name_template': 'MODIS NDVI ({start_date} to {end_date})'
    },
} 