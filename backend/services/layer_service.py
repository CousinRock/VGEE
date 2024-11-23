import ee

index = 0
def  get_layer_info_service(satellite):
    """获取图层信息服务"""
    try:
        global index
        if satellite == 'LANDSAT':
            dataset = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA').first()
            band_names = dataset.bandNames().getInfo()
            band_stats = {band: {'min': 0, 'max': 1} for band in band_names}
            
        elif satellite == 'SENTINEL':
            dataset = ee.ImageCollection('COPERNICUS/S2_SR').first()
            band_names = dataset.bandNames().getInfo()
            band_stats = {band: {'min': 0, 'max': 4000} for band in band_names}
            
        else:  # MODIS
            dataset = ee.ImageCollection('MODIS/006/MOD13A2').first()
            band_names = dataset.bandNames().getInfo()
            band_stats = {band: {'min': -2000, 'max': 10000} for band in band_names}
            
        index += 1
            
        return {
            'bands': band_names,
            'bandStats': band_stats,
            'satellite': satellite,
            'index': index
        }
        
    except Exception as e:
        raise Exception(f"Error in get_layer_info_service: {str(e)}")

def update_vis_params_service(data, current_dataset):
    """更新可视化参数服务"""
    try:
        vis_params = data.get('visParams')
        
        if current_dataset is None:
            raise Exception("No dataset available")

        # 获取选择的波段
        selected_bands = vis_params.get('bands', [])
        
        # 如果是单波段且提供了调色板
        if len(selected_bands) == 1 and vis_params.get('palette'):
            # 单波段显示时，使用调色板但不使用 gamma
            vis_params = {
                'bands': selected_bands,
                'min': float(vis_params.get('min', 0)),
                'max': float(vis_params.get('max', 10000)),
                'palette': [color.replace('#', '') if isinstance(color, str) and color.startswith('#') else color 
                          for color in vis_params['palette']]
            }
        else:
            # 多波段显示或没有调色板时，使用 gamma
            vis_params = {
                'bands': selected_bands,
                'min': float(vis_params.get('min', 0)),
                'max': float(vis_params.get('max', 10000)),
                'gamma': float(vis_params.get('gamma', 1.4))
            }
        
        map_id = current_dataset.getMapId(vis_params)
        return {
            'tileUrl': map_id['tile_fetcher'].url_format
        }
            
    except Exception as e:
        raise Exception(f"Error in update_vis_params_service: {str(e)}") 