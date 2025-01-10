from flask import Blueprint, jsonify, request
from services.map_service import save_dataset, get_all_datasets
from services.sample_service import get_all_samples
from tools.preprocessing import PreprocessingTool
from tools.classification import ClassificationTool 
from tools.calculateIndex import IndexTool
import ee

tool_bp = Blueprint('tool', __name__)

datasets = None
datasetsNames = None

def common_process(layer_ids, results, vis_params, message):
    '''
    通用的图层处理函数
    '''
    layer_results = []
    for i, layer_id in enumerate(layer_ids):
        result = ee.Image(results.get(i))
        datasets[layer_id] = result
        
        # 获取波段信息
        bandNames = result.bandNames().getInfo()
        print(f"Tool_routes.py - common_process - bandNames for {layer_id}:", bandNames)
        
        layer_vis = next((v for v in vis_params if v['id'] == layer_ids[i]), None)
        params = layer_vis['visParams'] if layer_vis else {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        }
        
        map_id = result.getMapId(params)
        print('Tool_routes.py - common_process-map_id:',params)
        
        layer_results.append({
            'layer_id': layer_ids[i],
            'tileUrl': map_id['tile_fetcher'].url_format,
            'bandInfo': bandNames,  # 添加波段信息
            'visParams': {
                'bands': params['bands'],
                'min': params['min'],
                'max': params['max'],
                'gamma': params.get('gamma', 1.4)
            }
        })

    return jsonify({
        'success': True,
        'message': message,
        'results': layer_results
    })
    
def get_vis_params(result):
    """动态计算可视化参数"""
    try:
        # 计算结果的统计信息
        stats = result.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=result.geometry(),
            scale=150,
            maxPixels=1e13
        ).getInfo()
        
        # 获取第一个波段的名称
        first_band = result.bandNames().getInfo()[0]
        print('Tool_routes.py - get_vis_params-first_band:', first_band)
        
        # 获取最小最大值
        min_val = stats.get(f'{first_band}_min', 0)
        max_val = stats.get(f'{first_band}_max', 1)
        
        return {
            'min': min_val,
            'max': max_val,
            'bands': [first_band]  # 使用第一个波段作为显示波段
        }
    except Exception as e:
        print(f"Error computing vis params: {str(e)}")
        # 如果计算失败，返回默认值
        return {
            'min': 0,
            'max': 1,
            'bands': ['constant']  # 默认波段名
        }


@tool_bp.route('/cloud-removal', methods=['POST'])
def cloud_removal():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        vis_params = data.get('vis_params', [])
        
        PreprocessingTool.validate_inputs(layer_ids, datasets)
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        
        
        results = selected_images.map(PreprocessingTool.cloud_removal).toList(selected_images.size())
        
        return common_process(layer_ids, results, vis_params, '除云处理完成')
        
    except Exception as e:
        print(f"Error in cloud_removal: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/calculate-index', methods=['POST'])
def calculate_index():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        index_type = data.get('index_type')
        vis_params = data.get('vis_params', [])
        
        IndexTool.validate_inputs(layer_ids, datasets)
        selected_images = IndexTool.get_image_collection(layer_ids, datasets).toList(len(layer_ids))
        
        # 修改这里，传入layer_id
        results = []
        for i, layer_id in enumerate(layer_ids):
            image = ee.Image(selected_images.get(i))
            result = IndexTool.calculate_index(image, index_type, layer_id)
            results.append(result)
            
        results = ee.List(results)
        # bandNames = ee.Image(results.get(0)).bandNames().getInfo()
        # print('Tool_routes.py - calculate_index-bandNames:',bandNames)
        
        return common_process(layer_ids, results, vis_params, f'已添加 {index_type.upper()} 波段')
        
    except Exception as e:
        print(f"Error in calculate_index: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/supervised-classification', methods=['POST'])
def supervised_classification():
    try:
        data = request.json
        result = ClassificationTool.supervised_classification(
            data.get('image'),
            data.get('training_data'),
            data.get('params')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/image-filling', methods=['POST'])
def image_filling():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        vis_params = data.get('vis_params', [])
        
        PreprocessingTool.validate_inputs(layer_ids, datasets)
        
        # 获取图像集合
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        # 转换为列表以便处理
        images_list = selected_images.toList(selected_images.size())
        
        # 创建图像集合用于填补
        image_collection = ee.ImageCollection.fromImages(images_list)
        
        # 对每个图像进行填补处理，并添加状态标记
        results = images_list.map(
            lambda img: PreprocessingTool.image_filling(ee.Image(img), image_collection)
        )
        
        #防止填补失败时出错
        print('Tool_routes.py - image_filling-results:',results.size().getInfo())
        # 使用 common_process 处理结果
        return common_process(layer_ids, results, vis_params, '图像填补处理完成')
        
    except Exception as e:
        print(f"Error in image_filling: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/get-layers', methods=['GET'])
def get_layers():
    try:
        global datasets, datasetsNames
        datasets, datasetsNames = get_all_datasets()
        landsat_layers = {}
        
        for layer_id, dataset in datasets.items():
            # if 'LANDSAT' in layer_id.upper() or 'SENTINEL-2' in layer_id.upper():
            layer_name = datasetsNames[layer_id]
            landsat_layers[layer_id] = {
                'id': layer_id,
                'name': layer_name,
                'dataset': dataset
            }
        
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
            'success': False,
            'message': 'Failed to get Landsat layers'
        }), 500 

@tool_bp.route('/kmeans-clustering', methods=['POST'])
def kmeans_clustering():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        cluster_counts = data.get('cluster_counts', {})
        
        ClassificationTool.validate_inputs(layer_ids, datasets)
        selected_images = ClassificationTool.get_image_collection(layer_ids, datasets)
        
        # 为每个图像执行聚类
        # 处理结果
        layer_results = []
        bandInfo = ['cluster']
        num = len(layer_ids)
        for i, layer_id in enumerate(layer_ids):
            num_clusters = cluster_counts.get(layer_id, 5)
            print('Tool_routes.py - kmeans_clustering-num_clusters',num_clusters)
            result = ClassificationTool.kmeans_clustering(
                ee.Image(selected_images.toList(num).get(i)), 
                num_clusters
            )

            num_clusters = cluster_counts.get(layer_id, 5)

             # 获取原始图层名称
            original_name = datasetsNames.get(layer_id, f'Layer_{layer_id}')
            kmeans_id = f"kmeans_{layer_id}"  # 为分类结果创建新的ID
            
            # 创建新的图层名称，包含原始名称和工具名称
            kmeans_name = f"{original_name} (K-means聚类)"  

            map_id = result.getMapId({
                'min': 0,
                'max': num_clusters - 1
            })
            
            layer_results.append({
                'layer_id': kmeans_id,
                'name': kmeans_name,  # 添加名称到返回结果
                'tileUrl': map_id['tile_fetcher'].url_format,
                'bandInfo': bandInfo,
                'visParams': {
                    'bands': bandInfo,
                    'min': 0,
                    'max': num_clusters - 1
                },
                'type':'Raster'
            })

             # 保存分类结果到数据集
            save_dataset(kmeans_id, result.select(bandInfo), kmeans_name)
           

        return jsonify({
            'success': True,
            'message': 'K-means聚类分析完成',
            'results': layer_results
        })
        
    except Exception as e:
        print(f"Error in kmeans_clustering: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/histogram-equalization', methods=['POST'])
def histogram_equalization():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        vis_params = data.get('vis_params', [])
        
        PreprocessingTool.validate_inputs(layer_ids, datasets)
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        results = selected_images.map(PreprocessingTool.histogram_equalization).toList(selected_images.size())
        
        return common_process(layer_ids, results, vis_params, '直方图均衡化处理完成')
        
    except Exception as e:
        print(f"Error in histogram_equalization: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@tool_bp.route('/random-forest', methods=['POST'])
def random_forest():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        rf_params = data.get('rf_params', {})
        
        # 获取参数
        num_trees = rf_params.get('numberOfTrees', 50)
        train_ratio = rf_params.get('trainRatio', 0.7)
        
        # 从 sample_service 获取样本数据
        samples = get_all_samples()
        if not samples:
            raise ValueError('No training samples available')
            
        # 获取影像
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        
        # 执行分类并创建结果列表
        num = len(layer_ids)
         # 处理结果
        layer_results = []
        bandInfo = ['classification']  # 分类结果波段名
        for i, layer_id in enumerate(layer_ids):
            image = ee.Image(selected_images.toList(num).get(i))
            classified = ClassificationTool.random_forest_classification(
                image, 
                samples,
                num_trees=num_trees,
                train_ratio=train_ratio
            )

             # 获取原始图层名称
            original_name = datasetsNames.get(layer_id, f'Layer_{layer_id}')
            rf_id = f"rf_{layer_id}"  # 为分类结果创建新的ID
            
            # 创建新的图层名称，包含原始名称和工具名称
            rf_name = f"{original_name} (随机森林分类)"
            
            # 设置可视化参数
            map_id = classified.getMapId({
                'min': 0,
                'max': len(samples) - 1
            })
            
            layer_results.append({
                'layer_id': rf_id,
                'name': rf_name,  # 添加名称到返回结果
                'tileUrl': map_id['tile_fetcher'].url_format,
                'bandInfo': bandInfo,
                'visParams': {
                    'bands': bandInfo,
                    'min': 0,
                    'max': len(samples) - 1
                },
                'type':'Raster'
            })

            # 保存分类结果到数据集
            save_dataset(rf_id, classified.select(bandInfo), rf_name)     

        return jsonify({
            'success': True,
            'message': '随机森林分类完成',
            'results': layer_results
        })
        
    except Exception as e:
        print(f"Error in random_forest: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/raster-calculator', methods=['POST'])
def raster_calculator():
    def create_layer_result(layer_id, name, result, vis_params):
        """创建图层结果对象
        
        Args:
            layer_id (str): 图层ID
            name (str): 图层名称
            result (ee.Image): 计算结果影像
            vis_params (dict): 可视化参数
            
        Returns:
            dict: 包含图层信息的字典
        """
        map_id = result.getMapId(vis_params)
        return {
            'layer_id': layer_id,
            'name': name,
            'tileUrl': map_id['tile_fetcher'].url_format,
            'bandInfo': result.bandNames().getInfo(),
            'visParams': vis_params,
            'type':'Raster'
        }
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        params = data.get('expression', {})
        expression = params.get('expression')
        calc_mode = params.get('mode', 'single')
        
        if not layer_ids or not expression:
            raise ValueError('Missing required parameters')
            
        layer_results = []
        
        if calc_mode == 'multi':
            # 多图层计算
            result = PreprocessingTool.raster_calculator_multi(layer_ids, expression, datasets, datasetsNames)
            
            # 创建结果图层
            calc_id = f"calc_multi_{layer_ids[0]}"
            calc_name = "多图层计算结果"
            save_dataset(calc_id, result, calc_name)
            
            # 设置可视化参数并添加结果
            vis_params = get_vis_params(result)
            layer_results.append(create_layer_result(calc_id, calc_name, result, vis_params))
            
        elif calc_mode == 'all_bands':
            # 全波段计算
            for layer_id in layer_ids:
                if layer_id not in datasets:
                    raise ValueError(f'Invalid layer ID: {layer_id}')
                
                # 从请求中获取波段组设置
                # 例如: {'x*2': ['B1','B2','B3'], 'x/2': ['B5','B6','B7']}
                # {'x/10000':['B1','B2','B3','B4','B5','B6','B7','B8','B8A','B9','B10','B11','B12']}
                selected_bands = eval(expression)
                print('Tool_routes.py - raster_calculator-selected_bands:', selected_bands)
                
                result = PreprocessingTool.raster_calculator_all_bands(
                    datasets[layer_id], 
                    expression,
                    selected_bands
                )
                
                # 创建结果图层
                calc_id = f"calc_all_{layer_id}"
                calc_name = f"{datasetsNames.get(layer_id, f'Layer_{layer_id}')} (多波段计算结果)"
                save_dataset(calc_id, result, calc_name)
                
                # 设置可视化参数
                band_names = result.bandNames()
                default_bands = ee.List(band_names.slice(0, 3))
                vis_params = {'bands': default_bands.getInfo(), 'min': 0, 'max': 1, 'gamma': 1.4}
                print('Tool_routes.py - raster_calculator-vis_params:', vis_params)
                
                layer_results.append(create_layer_result(calc_id, calc_name, result, vis_params))
                
        else:
            # 单波段计算
            for layer_id in layer_ids:
                if layer_id not in datasets:
                    raise ValueError(f'Invalid layer ID: {layer_id}')
                    
                result = PreprocessingTool.raster_calculator_single(datasets[layer_id], expression)
                
                # 创建结果图层
                calc_id = f"calc_{layer_id}"
                calc_name = f"{datasetsNames.get(layer_id, f'Layer_{layer_id}')} (计算结果)"
                save_dataset(calc_id, result, calc_name)
                
                # 设置可视化参数
                vis_params = get_vis_params(result)
                layer_results.append(create_layer_result(calc_id, calc_name, result, vis_params))
        
        return jsonify({
            'success': True,
            'message': '栅格计算完成',
            'results': layer_results
        })
        
    except Exception as e:
        print(f"Error in raster calculator: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
