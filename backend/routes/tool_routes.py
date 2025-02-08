from flask import Blueprint, jsonify, request
from services.map_service import save_dataset, get_all_datasets, get_dataset
from services.sample_service import get_all_samples
from tools.preprocessing import PreprocessingTool
from tools.classification import ClassificationTool 
from tools.calculateIndex import IndexTool
import ee
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

tool_bp = Blueprint('tool', __name__)

datasets = None
datasetsNames = None
maxthread_num = 4


def common_process(layer_ids, results, vis_params, message):
    '''
    通用的图层处理函数
    '''
    layer_results = []
    for i, layer_id in enumerate(layer_ids):
        result = ee.Image(results.get(i))
        # 获取波段信息
        try:
            bandNames = result.bandNames().getInfo()
        except Exception as e:
            print(f"Error getting band names: {str(e)}")
            return jsonify({
                'success': False,
                'message': f"Error processing layer: {str(e)}"
            }), 500
        
        print(f"Tool_routes.py - common_process - bandNames for {layer_id}:", bandNames)

        datasets[layer_id] = result        
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
        print('Tool_routes.py - cloud_removal-layer_ids:', layer_ids)
        
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
        selected_images = IndexTool.get_image_collection(layer_ids, datasets)
        images_list = selected_images.toList(len(layer_ids))
        
        def process_layer(args):
            i, layer_id = args
            try:
                image = ee.Image(images_list.get(i))
                # 计算指数并添加为新波段
                result = IndexTool.calculate_index(image, index_type)
                return result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        # 使用线程池并行处理
        results = []
        with ThreadPoolExecutor(max_workers=min(len(layer_ids), maxthread_num)) as executor:
            future_to_layer = {
                executor.submit(process_layer, (i, layer_id)): layer_id 
                for i, layer_id in enumerate(layer_ids)
            }
            
            for future in as_completed(future_to_layer):
                result = future.result()
                if result is not None:
                    results.append(result)

        if not results:
            raise ValueError("No successful index calculation results")
            
        # 转换结果为 ee.List
        results = ee.List(results)
        
        # 使用原有的 common_process 处理结果
        return common_process(layer_ids, results, vis_params, f'已添加 {index_type.upper()} 波段')
        
    except Exception as e:
        print(f"Error in calculate_index: {str(e)}")
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
        images_list = selected_images.toList(len(layer_ids))
        
        layer_results = []
        bandInfo = ['cluster']

        # 定义处理单个图层的函数
        def process_layer(args):
            i, layer_id = args
            try:
                num_clusters = cluster_counts.get(layer_id, 5)
                result = ClassificationTool.kmeans_clustering(
                    ee.Image(images_list.get(i)), 
                    num_clusters
                )

                # 获取原始图层名称和创建新名称
                original_name = datasetsNames.get(layer_id, f'Layer_{layer_id}')
                kmeans_id = f"kmeans_{int(time.time())}-{layer_id}"
                kmeans_name = f"{original_name} (K-means聚类)"

                map_id = result.getMapId({
                    'min': 0,
                    'max': num_clusters - 1
                })
                
                layer_result = {
                    'layer_id': kmeans_id,
                    'name': kmeans_name,
                    'tileUrl': map_id['tile_fetcher'].url_format,
                    'bandInfo': bandInfo,
                    'visParams': {
                        'bands': bandInfo,
                        'min': 0,
                        'max': num_clusters - 1
                    },
                    'type': 'Raster'
                }

                # 保存分类结果
                save_dataset(kmeans_id, result.select(bandInfo), kmeans_name)
                
                return layer_result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=min(len(layer_ids), maxthread_num)) as executor:
            future_to_layer = {
                executor.submit(process_layer, (i, layer_id)): layer_id 
                for i, layer_id in enumerate(layer_ids)
            }
            
            for future in as_completed(future_to_layer):
                result = future.result()
                if result is not None:
                    layer_results.append(result)

        if not layer_results:
            raise ValueError("No successful classification results")

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
        rf_params = data.get('rf_params', {})  # 现在是一个字典，key是layer_id
        
        samples = get_all_samples()
        if not samples:
            raise ValueError('No training samples available')
            
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        images_list = selected_images.toList(len(layer_ids))
        
        def process_layer(args):
            i, layer_id = args
            try:
                # 获取该图层的特定参数
                layer_params = rf_params.get(layer_id, {})
                num_trees = layer_params.get('numberOfTrees', 50)
                train_ratio = layer_params.get('trainRatio', 0.7)
                
                image = ee.Image(images_list.get(i))
                classified = ClassificationTool.random_forest_classification(
                    image, samples,
                    num_trees=num_trees,
                    train_ratio=train_ratio
                )

                original_name = datasetsNames.get(layer_id, f'Layer_{layer_id}')
                rf_id = f"rf_{int(time.time())}-{layer_id}"
                rf_name = f"{original_name} (随机森林分类)"
                
                map_id = classified.getMapId({
                    'min': 0,
                    'max': len(samples) - 1
                })
                
                layer_result = {
                    'layer_id': rf_id,
                    'name': rf_name,
                    'tileUrl': map_id['tile_fetcher'].url_format,
                    'bandInfo': ['classification'],
                    'visParams': {
                        'bands': ['classification'],
                        'min': 0,
                        'max': len(samples) - 1
                    },
                    'type': 'Raster'
                }

                save_dataset(rf_id, classified.select(['classification']), rf_name)
                return layer_result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        layer_results = []
        with ThreadPoolExecutor(max_workers=min(len(layer_ids), maxthread_num)) as executor:
            future_to_layer = {
                executor.submit(process_layer, (i, layer_id)): layer_id 
                for i, layer_id in enumerate(layer_ids)
            }

            
            for future in as_completed(future_to_layer):
                result = future.result()
                if result is not None:
                    layer_results.append(result)

        if not layer_results:
            raise ValueError("No successful classification results")

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
        expression = data.get('expression')
        mode = data.get('mode', 'single')  # 默认为单波段模式

        layer_results = []
        
        if mode == 'multi':
            # 多图层模式 - 一次性处理所有图层
            try:
                result = PreprocessingTool.raster_calculator_multi(layer_ids, expression, datasets, datasetsNames)
                
                calc_id = f"calc_multi_{int(time.time())}"
                calc_name = "多图层计算结果"
                save_dataset(calc_id, result, calc_name)
                
                # 获取波段名称并设置可视化参数
                band_names = result.bandNames().getInfo()
                default_bands = band_names[:3] if len(band_names) >= 3 else band_names
                vis_params = {'bands': default_bands, 'min': 0, 'max': 1, 'gamma': 1.4}
                
                layer_results.append(create_layer_result(calc_id, calc_name, result, vis_params))
            except Exception as e:
                print(f"Error in multi-layer calculation: {str(e)}")
                
        elif mode == 'all_bands':
            # 例如: {'x*2': ['B1','B2','B3'], 'x/2': ['B5','B6','B7']}
            # {'x/10000':['B1','B2','B3','B4','B5','B6','B7','B8','B8A','B9','B10','B11','B12']}
            # 全波段模式 - 并行处理每个图层
            selected_bands = eval(expression)
            print('Tool_routes.py - raster_calculator-selected_bands:', selected_bands)
            with ThreadPoolExecutor(max_workers=min(len(layer_ids), maxthread_num)) as executor:
                futures = []
                for layer_id in layer_ids:
                    if layer_id not in datasets:
                        continue
                    future = executor.submit(
                        lambda x: PreprocessingTool.raster_calculator_all_bands(
                            datasets[x], 
                            expression, 
                            selected_bands
                        ), 
                        layer_id
                    )
                    futures.append((future, layer_id))
                
                for future, layer_id in futures:
                    try:
                        result = future.result()
                        if result is not None:
                            calc_id = f"calc_all_{int(time.time())}-{layer_id}"
                            calc_name = f"{datasetsNames.get(layer_id, f'Layer_{layer_id}')} (全波段计算结果)"
                            save_dataset(calc_id, result, calc_name)
                            
                            band_names = result.bandNames().getInfo()
                            default_bands = band_names[:3] if len(band_names) >= 3 else band_names
                            vis_params = {'bands': default_bands, 'min': 0, 'max': 1, 'gamma': 1.4}
                            
                            layer_results.append(create_layer_result(calc_id, calc_name, result, vis_params))
                    except Exception as e:
                        print(f"Error processing layer {layer_id}: {str(e)}")
                        continue
                        
        else:
            # 单波段模式 - 并行处理每个图层
            def process_single_layer(args):
                layer_id = args
                try:
                    if layer_id not in datasets:
                        raise ValueError(f'Invalid layer ID: {layer_id}')
                        
                    result = PreprocessingTool.raster_calculator_single(datasets[layer_id], expression)
                    
                    # 创建结果图层
                    calc_id = f"calc_{int(time.time())}-{layer_id}"
                    calc_name = f"{datasetsNames.get(layer_id, f'Layer_{layer_id}')} (计算结果)"
                    save_dataset(calc_id, result, calc_name)
                    
                    # 设置可视化参数
                    vis_params = get_vis_params(result)
                    
                    return create_layer_result(calc_id, calc_name, result, vis_params)
                except Exception as e:
                    print(f"Error processing layer {layer_id}: {str(e)}")
                    return None
            with ThreadPoolExecutor(max_workers=min(len(layer_ids), maxthread_num )) as executor:
                future_to_layer = {
                    executor.submit(process_single_layer, layer_id): layer_id 
                    for layer_id in layer_ids
                }
                
                for future in as_completed(future_to_layer):
                    result = future.result()
                    if result is not None:
                        layer_results.append(result)

        if not layer_results:
            raise ValueError("No successful calculation results")

        return jsonify({
            'success': True,
            'message': '栅格计算完成',
            'results': layer_results
        })
        
    except Exception as e:
        print(f"Error in raster calculator: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@tool_bp.route('/rename-bands', methods=['POST'])
def rename_bands():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        bands_mapping = data.get('bands')
        vis_params = data.get('vis_params', [])
        
        # 验证 bands_mapping 中的条目
        for band in bands_mapping:
            if not band['original'] or (not band['new'] and not band['customName']):
                return jsonify({
                    'success': False,
                    'message': '波段映射包含空值。请提供有效的波段名称。'
                }), 400
        

        PreprocessingTool.validate_inputs(layer_ids, datasets)
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        
        # 对每个图像应用 rename_bands
        results = selected_images.map(lambda img: PreprocessingTool.rename_bands(img, bands_mapping)).toList(selected_images.size())
        
        # 更新 vis_params 中的波段名称
        for vis_param in vis_params:
            vis_param['visParams']['bands'] = [
                next((band['customName'] if band['new'] == 'custom' else band['new'] for band in bands_mapping if band['original'] == b), b)
                for b in vis_param['visParams']['bands']
            ]
        
        return common_process(layer_ids, results, vis_params, '波段重命名完成')
        
    except Exception as e:
        print(f"Error renaming bands: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/svm', methods=['POST'])
def svm_classification():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        svm_params = data.get('svm_params', {})  # 现在是一个字典，key是layer_id
        print('Tool_routes.py - svm_classification-svm_params:', svm_params)
        
        samples = get_all_samples()
        if not samples:
            raise ValueError('No training samples available')
            
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        images_list = selected_images.toList(len(layer_ids))
        
        def process_layer(args):
            i, layer_id = args
            try:
                # 获取该图层的特定参数
                layer_params = svm_params.get(layer_id, {})
                kernel = layer_params.get('kernel', 'RBF')
                train_ratio = layer_params.get('trainRatio', 0.7)
                
                image = ee.Image(images_list.get(i))
                classified = ClassificationTool.svm_classification(
                    image, samples,
                    kernel=kernel,
                    train_ratio=train_ratio
                )

                original_name = datasetsNames.get(layer_id, f'Layer_{layer_id}')
                svm_id = f"svm_{int(time.time())}-{layer_id}"
                svm_name = f"{original_name} (SVM分类)"
                
                map_id = classified.getMapId({
                    'min': 0,
                    'max': len(samples) - 1
                })
                
                layer_result = {
                    'layer_id': svm_id,
                    'name': svm_name,
                    'tileUrl': map_id['tile_fetcher'].url_format,
                    'bandInfo': ['classification'],
                    'visParams': {
                        'bands': ['classification'],
                        'min': 0,
                        'max': len(samples) - 1
                    },
                    'type': 'Raster'
                }

                save_dataset(svm_id, classified.select(['classification']), svm_name)
                return layer_result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        layer_results = []
        with ThreadPoolExecutor(max_workers=min(len(layer_ids), maxthread_num)) as executor:
            future_to_layer = {
                executor.submit(process_layer, (i, layer_id)): layer_id 
                for i, layer_id in enumerate(layer_ids)
            }
            
            for future in as_completed(future_to_layer):
                result = future.result()
                if result is not None:
                    layer_results.append(result)

        if not layer_results:
            raise ValueError("No successful classification results")

        return jsonify({
            'success': True,
            'message': 'SVM分类完成',
            'results': layer_results
        })
        
    except Exception as e:
        print(f"Error in svm_classification: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
