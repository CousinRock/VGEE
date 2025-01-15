from flask import Blueprint, jsonify, request
from services.ai_service import AIService
from services.map_service import get_dataset
import ee

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()

@ai_bp.route('/segment', methods=['POST'])
def segment_image():
    try:
        data = request.json
        layer_id = data.get('layer_id')
        model_name = data.get('model_name', 'unet')
        print('AI_routes.py - segment_image - model_name:', model_name)
        
        # 获取图像数据
        image = get_dataset(layer_id)
        if not image:
            raise ValueError(f"Layer {layer_id} not found")
            
        # 转换为numpy数组进行处理
        region = image.geometry()
        scale = 30
        numpy_image = image.getRegion(region, scale).getInfo()
        
        # 进行AI预测
        result = ai_service.predict(model_name, numpy_image)
        
        # 将结果转回Earth Engine格式
        result_image = ee.Image.fromArray(result)
        
        # 返回处理结果
        return jsonify({
            'success': True,
            'message': 'AI processing completed',
            'result': result_image
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 