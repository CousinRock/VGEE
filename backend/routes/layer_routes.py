from flask import Blueprint, jsonify, request
from services.layer_service import get_layer_info_service, update_vis_params_service

layer_bp = Blueprint('layer', __name__)

@layer_bp.route('/layer-info', methods=['GET'])
def get_layer_info():
    try:
        satellite = request.args.get('satellite', 'LANDSAT')
        result = get_layer_info_service(satellite)
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_layer_info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@layer_bp.route('/update-vis-params', methods=['POST'])
def update_vis_params():
    try:
        data = request.json
        result = update_vis_params_service(data)
        return jsonify(result)
    except Exception as e:
        print(f"Error in update_vis_params: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 