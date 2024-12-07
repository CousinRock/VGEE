import ee

index = 0
def  get_layer_info_service(image, satellite):
    """获取图层信息服务"""
    try:
        global index
        band_names = image.bandNames().getInfo()
            
        return {
            'success': True,
            'bands': band_names,
            'satellite': satellite,
        }
        
    except Exception as e:
        raise Exception(f"Layer_service.py - Error in get_layer_info_service: {str(e)}")

def update_vis_params_service(data, current_dataset):
    """更新可视化参数服务"""
    try:
        vis_params = data.get('visParams')
        
        if current_dataset is None:
            raise Exception("Layer_service.py - No dataset available")

        # 获取选择的波段
        selected_bands = vis_params.get('bands', [])
        
        # 打印当前数据集的波段信息，用于调试
        print(f"Layer_service.py - Current dataset bands: {selected_bands}")
        
        img = current_dataset.select(selected_bands)
        
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
        
        print(f"Layer_service.py - Selected bands for visualization: {vis_params['bands']}")
        map_id = img.getMapId(vis_params)
        return {
            'tileUrl': map_id['tile_fetcher'].url_format
        }
            
    except Exception as e:
        raise Exception(f"Layer_service.py - Error in update_vis_params_service: {str(e)}") 