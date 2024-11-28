from flask import Blueprint, jsonify, request
from services.tool_service import ToolService

tool_bp = Blueprint('tool', __name__)

datasets = None

@tool_bp.route('/cloud-removal', methods=['POST'])
def cloud_removal():
    try:
        data = request.json
        layer_id = data.get('layer_id')
        print(layer_id)
        
        if not layer_id or layer_id not in datasets:
            return jsonify({
                'success': False,
                'error': 'Invalid layer ID'
            }), 400
            
        # 获取图层数据并进行除云处理
        result = ToolService.cloud_removal(datasets[layer_id])
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in cloud_removal: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tool_bp.route('/calculate-index', methods=['POST'])
def calculate_index():
    try:
        data = request.json
        result = ToolService.calculate_index(
            data.get('image'),
            data.get('index_type'),
            data.get('params')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tool_bp.route('/supervised-classification', methods=['POST'])
def supervised_classification():
    try:
        data = request.json
        result = ToolService.supervised_classification(
            data.get('image'),
            data.get('training_data'),
            data.get('params')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tool_bp.route('/change-detection', methods=['POST'])
def change_detection():
    try:
        data = request.json
        result = ToolService.change_detection(
            data.get('image1'),
            data.get('image2'),
            data.get('method'),
            data.get('params')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tool_bp.route('/get-layers', methods=['GET'])
def get_layers():
    try:
        global datasets
        from services.map_service import get_all_datasets
        datasets , datasetsNames = get_all_datasets()
        landsat_layers = {}
        
        for layer_id, dataset in datasets.items():
            if 'LANDSAT' in layer_id.upper():
                layer_name = datasetsNames[layer_id]
                landsat_layers[layer_id] = {
                    'id': layer_id,
                    'name': layer_name,
                    'dataset': dataset
                }
        
        print('Available Landsat layers:', landsat_layers)
        
        return jsonify({
            'success': True,
            'layers': [
                {
                    'id': layer_id,
                    'name': info['name']
                } for layer_id, info in landsat_layers.items()
            ]
        })
    except Exception as e:
        print(f"Error in get_layers: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to get Landsat layers'
        }), 500 