from flask import Blueprint, jsonify, request
from services.map_service import get_dataset
from services.ai_service import segment_img
import ee

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/segment', methods=['POST'])
def segment_image():
    try:
        data = request.json
        print('AI_routes.py - segment_image - data:', data)
        
        # 获取图层ID列表的第一个元素
        layer_ids = data.get('layer_ids', [])
        if not layer_ids:
            raise ValueError("No layer ID provided")
            
        # 只使用第一个图层进行处理
        layer_id = layer_ids[0]
        image = ee.Image(get_dataset(layer_id))

        # 获取缩略图URL
        url = image.getThumbURL({
            'region': image.geometry(),
            'min': 0,
            'max': 255
        })

        print(f"Generated URL: {url}")
        result = segment_img(url)
        print('AI_routes.py - segment_image - result:', result)

        # 返回分割结果
        return jsonify({
            'success': True,
            'message': 'Segmentation completed successfully',
            'result': result
        }), 200

    except Exception as e:
        print(f"AI_routes.py - Error in segment_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

