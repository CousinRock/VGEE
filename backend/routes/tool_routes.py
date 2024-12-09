from flask import Blueprint, jsonify, request
from services.tool_service import ToolService
import ee

tool_bp = Blueprint('tool', __name__)

datasets = None

def common_process(layer_ids, results, vis_params, message):
    '''
    通用的图层处理函数
    Args:
        layer_ids: 要处理的图层ID列表
        results: 处理后的结果列表
        vis_params: 可视化参数列表
        message: 成功时的消息
    '''
     # 为每个处理后的图层生成新的瓦片URL
    layer_results = []
    for i, layer_id in enumerate(layer_ids):
        result = ee.Image(results.get(i))
        # 更新数据集中的图层
        datasets[layer_id] = result
        
        # 使用对应图层的原始 visParams
        layer_vis = next((v for v in vis_params if v['id'] == layer_ids[i]), None)
        params = layer_vis['visParams'] if layer_vis else {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        }
        
        map_id = result.getMapId(params)
        
        layer_results.append({
            'layer_id': layer_ids[i],
            'tileUrl': map_id['tile_fetcher'].url_format
        })

    return jsonify({
            'success': True,
            'message': message,
            'results': layer_results
        })

@tool_bp.route('/cloud-removal', methods=['POST'])
def cloud_removal():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        vis_params = data.get('vis_params', [])
        print('Tool_routes.py - vis_params', vis_params)
        print(f"Tool_routes.py - cloud_removal-datasets: {datasets}")
        
        if not layer_ids or not all(layer_id in datasets for layer_id in layer_ids):
            return jsonify({
                'success': False,
                'error': 'Invalid layer ID'
            }), 400
            
        # 获取所有选中的图层数据
        selected_images = ee.ImageCollection([datasets[layer_id] for layer_id in layer_ids])
        
        # 在服务端处理图像并获取结果列表
        results = selected_images.map(ToolService.cloud_removal).toList(selected_images.size())
        
        return common_process(layer_ids, results, vis_params, '除云处理完成')
        
    except Exception as e:
        print(f"Tool_routes.py - Error in cloud_removal: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tool_bp.route('/calculate-index', methods=['POST'])
def calculate_index():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        index_type = data.get('index_type')
        vis_params = data.get('vis_params', [])

        print(f"Tool_routes.py - calculate_index-index_type: {index_type}")
        
        if not layer_ids or not all(layer_id in datasets for layer_id in layer_ids):
            return jsonify({
                'success': False,
                'error': 'Invalid layer ID'
            }), 400
            
        # 获取所有选中的图层数据
        selected_images = [datasets[layer_id] for layer_id in layer_ids]
        print('Tool_routes.py - calculate_index-layer_ids',layer_ids)
        
        results = ee.ImageCollection(selected_images).map(lambda image: ToolService.calculate_index(image, index_type))
        print('Tool_routes.py - calculate_index-results.size()',results.size().getInfo())
        results = results.toList(results.size())

        return common_process(layer_ids, results, vis_params, f'已添加 {index_type.upper()} 波段')
    except Exception as e:
        print(f"Error in calculate_index: {str(e)}")
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

@tool_bp.route('/image-filling', methods=['POST'])
def image_filling():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        vis_params = data.get('vis_params', [])
        
        if not layer_ids or not all(layer_id in datasets for layer_id in layer_ids):
            return jsonify({
                'success': False,
                'error': 'Invalid layer IDs'
            }), 400
            
        # 获取所有选中的图层数据
        selected_images = [datasets[layer_id] for layer_id in layer_ids]
        
        # 调用服务进行图像填补
        results = ToolService.image_filling(selected_images)
        
        # 检查返回值是否表示错误
        if isinstance(results, dict):
            return jsonify(results)
            
        # 如果是正常的结果，继续处理
        results = results.toList(results.size())
        return common_process(layer_ids, results, vis_params, '图像填补处理完成')
        
    except Exception as e:
        print(f"Error in image_filling: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'影像填补失败: {str(e)}'
        }), 500

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
        
        print('Tool_routes.py - Available Landsat layers:', landsat_layers)
        
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
        print(f"Tool_routes.py - Error in get_layers: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to get Landsat layers'
        }), 500 

@tool_bp.route('/kmeans-clustering', methods=['POST'])
def kmeans_clustering():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        print('Tool_routes.py - kmeans_clustering-layer_ids', layer_ids)
        num_clusters = data.get('num_clusters', 5)  # 默认5类
        
        if not layer_ids or not all(layer_id in datasets for layer_id in layer_ids):
            return jsonify({
                'success': False,
                'error': 'Invalid layer ID'
            }), 400
            
        # 获取选中的图层数据
        selected_images = ee.ImageCollection([datasets[layer_id] for layer_id in layer_ids])       
        num = len(layer_ids)  # 获取图层数量
        
        # 对每个图像执行聚类
        results = selected_images.map(
            lambda img: ToolService.kmeans_clustering(img, num_clusters)
        ).toList(num)
        
        # 为每个聚类结果创建新的图层ID并存储
        layer_results = []
        bandInfo = ['cluster']
        for i in range(num):
            # 创建新的图层ID，添加 _kmeans 后缀
            kmeans_id = f"{layer_ids[i]}_kmeans"
            # 存储聚类结果到 datasets
            datasets[kmeans_id] = ee.Image(results.get(i)).select(bandInfo)
            
            # 使用随机可视化参数
            map_id = datasets[kmeans_id].getMapId({
                'min': 0,
                'max': num_clusters - 1
            })
            
            layer_results.append({
                'layer_id': kmeans_id,  # 返回新的图层ID
                'tileUrl': map_id['tile_fetcher'].url_format,
                'bandInfo': bandInfo,
                'visParams': {
                    'bands': bandInfo,
                    'min': 0,
                    'max': num_clusters - 1
                }
            })

        return jsonify({
            'success': True,
            'message': 'K-means聚类分析完成',
            'results': layer_results  # 返回所有结果
        })
        
    except Exception as e:
        print(f"Error in kmeans_clustering: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'聚类分析失败: {str(e)}'
        }), 500 