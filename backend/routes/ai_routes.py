from flask import Blueprint, jsonify, request
from services.map_service import get_dataset,get_all_datasets
from services.ai_service import text_segment_img
import ee
import time

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/segment', methods=['POST'])
def segment_image():
    try:
        data = request.json
        print('AI_routes.py - segment_image - data:', data)
        
        layer_ids = data.get('layer_ids', [])
        vis_params = data.get('visParams', {})  # 每个图层的显示参数
        params = data.get('params', {})  # 直接获取每个图层的参数
        
        if not layer_ids:
            raise ValueError("No layer ID provided")
            
        results = []
        # 处理每个图层
        for layer_id in layer_ids:
            datasets, datasetsNames = get_all_datasets()#获取所有数据
            image = datasets[layer_id]
            image_name = datasetsNames[layer_id]
            print('ai_routes-segment_image-image_name', image_name)
            
            # 获取该图层的特定参数
            print('ai_routes-segment_image-params', params)
            layer_params = params.get(layer_id, {})  # 直接获取该图层的参数
            text_prompt = layer_params.get('textPrompt', 'house')
            threshold = layer_params.get('threshold', 0.24)
            
            # 获取该图层的显示参数
            layer_vis = vis_params.get(layer_id, {})
            layer_min = layer_vis.get('min', 0)
            layer_max = layer_vis.get('max', 255)
            
            # 获取图像边界
            bounds = image.geometry().bounds().getInfo()['coordinates'][0]
            print('ai_routes-segment_image-bounds', bounds)

            image_bounds = [
                bounds[0][0],  # min_x
                bounds[0][1],  # min_y
                bounds[2][0],  # max_x
                bounds[2][1]   # max_y
            ]

            # 获取缩略图URL，使用该图层的特定显示参数
            dimensions = '1024x1024'
            url = image.getThumbURL({
                'region': image.geometry(),
                'min': layer_min,
                'max': layer_max,
                'dimensions': dimensions
            })

            print(f"Generated URL for layer {layer_id}: {url}")
            #调用语义分割图像
            coordinates = text_segment_img(url, image_bounds, {
                'textPrompt': text_prompt,
                'threshold': threshold
            }, dimensions)
            
            if coordinates is None:
                continue

            # 为每个图层创建结果
            results.append({
                'layer_id': f'sam_prediction_{layer_id}_{int(time.time())}',
                'name': f'{image_name}_SAM预测结果',
                'type': 'vector',
                'geometryType': 'Polygon',
                'coordinates': coordinates,
                'visParams': {
                    'color': '#ff0000',
                    'weight': 2,
                    'opacity': 1,
                    'fillOpacity': 0.5
                }
            })

        if not results:
            raise ValueError("No successful segmentation results")

        return jsonify({
            'success': True,
            'message': 'Segmentation completed successfully',
            'results': results
        }), 200

    except Exception as e:
        print(f"AI_routes.py - Error in segment_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

