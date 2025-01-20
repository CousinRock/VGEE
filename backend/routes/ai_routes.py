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
        print('ai_routes-segment_image-image_bounds',image_bounds)

        # 获取缩略图 URL
        dimensions = '1024x1024'  # 动态调整图像尺寸参数
        url = image.getThumbURL({
            'region': image.geometry(),
            'min': layer_min,
            'max': layer_max,
            'dimensions': dimensions
        })

        print(f"Generated URL: {url}")
        result = segment_img(url, image_bounds, dimensions)
        
        if result is None:
            raise ValueError("Segmentation failed")
            
        # 设置样式参数
        style_params = {
            'color': 'ff0000',  # 红色
            'width': 2,
            'opacity': 1,
            'fillOpacity': 0.5
        }
        
        # 获取瓦片URL
        map_id = result.getMapId(style_params)
        
        # 获取所有特征的坐标
        features = result.getInfo()['features']
        coordinates = []
        for feature in features:
            coords = feature['geometry']['coordinates'][0]  # 获取每个多边形的外环坐标
            coordinates.append(coords)

        # 返回分割结果
        return jsonify({
            'success': True,
            'message': 'Segmentation completed successfully',
            'results': [{
                'layer_id': f'sam_prediction_{int(time.time())}',
                'name': 'SAM预测结果',
                'type': 'vector',
                'geometryType': 'Polygon',
                'tileUrl': map_id['tile_fetcher'].url_format,
                'visParams': style_params,
                'coordinates': coordinates  # 添加坐标数据
            }]
        }), 200

    except Exception as e:
        print(f"AI_routes.py - Error in segment_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

