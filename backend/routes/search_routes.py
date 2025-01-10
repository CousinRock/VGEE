import geemap
from flask import Blueprint, jsonify, request
from config.satellite_config import SATELLITE_CONFIGS, save_satellite_configs

search_bp = Blueprint('search', __name__)

@search_bp.route('/search-data', methods=['POST'])
def search_data():
    try:
        data = request.json
        dataset_type = data.get('dataset_type', 'Landsat')
        print('search_routes.py - search_data-dataset_type:', dataset_type)
        
        # 使用 geemap 搜索数据集
        datasets = geemap.search_ee_data(dataset_type)
        dataset_list = [dataset for dataset in datasets]
        
        return jsonify({
            'success': True,
            'datasets': dataset_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@search_bp.route('/add-satellite', methods=['POST'])
def add_satellite():
    try:
        data = request.json
        new_satellite = data.get('id')
        print('search_routes.py - add_satellite-new_satellite:', new_satellite)
        
        if new_satellite and new_satellite not in SATELLITE_CONFIGS:
            # 添加新的卫星到列表
            SATELLITE_CONFIGS.append(new_satellite)
            # 保存更新后的配置
            save_satellite_configs(SATELLITE_CONFIGS)
            return jsonify({'success': True, 'message': 'Satellite added successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Satellite already exists or invalid input.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500