from flask import Blueprint, jsonify, request
from services.map_service import get_dataset
from services.ai_service import segment_img
import ee
import time

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/segment', methods=['POST'])
def segment_image():
    try:
        data = request.json
        print('AI_routes.py - segment_image - data:', data)
        
        # 获取图层ID列表的第一个元素
        layer_ids = data.get('layer_ids', [])
        layer_min = data.get('min', 0)
        layer_max = data.get('max', 255)
        if not layer_ids:
            raise ValueError("No layer ID provided")
            
        # 只使用第一个图层进行处理
        layer_id = layer_ids[0]
        image = ee.Image(get_dataset(layer_id))
        
        # 获取图像边界
        bounds = image.geometry().bounds().getInfo()['coordinates'][0]
        print('ai_routes-segment_image-bounds',bounds)

        image_bounds = [
            bounds[0][0],  # min_x
            bounds[0][1],  # min_y
            bounds[2][0],  # max_x
            bounds[2][1]   # max_y
        ]

        # 获取缩略图URL
        dimensions = '1024x1024'
        url = image.getThumbURL({
            'region': image.geometry(),
            'min': layer_min,
            'max': layer_max,
            'dimensions': dimensions
        })

        print(f"Generated URL: {url}")
        coordinates = segment_img(url, image_bounds, dimensions)
        
        if coordinates is None:
            raise ValueError("Segmentation failed")

        # 返回分割结果
        return jsonify({
            'success': True,
            'message': 'Segmentation completed successfully',
            'results': [{
                'layer_id': f'sam_prediction_{int(time.time())}',
                'name': 'SAM预测结果',
                'type': 'vector',
                'geometryType': 'Polygon',
                'coordinates': coordinates,  # 直接返回坐标数组
                'visParams': {
                    'color': '#ff0000',
                    'width': 2,
                    'opacity': 1,
                    'fillOpacity': 0.5
                }
            }]
        }), 200

    except Exception as e:
        print(f"AI_routes.py - Error in segment_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

