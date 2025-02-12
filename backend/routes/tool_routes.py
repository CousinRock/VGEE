from flask import Blueprint, jsonify, request
from services.map_service import save_dataset, get_all_datasets, get_dataset
from services.sample_service import get_all_samples
from tools.preprocessing import PreprocessingTool
from tools.classification import ClassificationTool 
from tools.calculateIndex import IndexTool
from tools.parallel_processor import ParallelProcessor
from tools.rasterOperator import RasterOperatorTool
from tools.terrainOperator import TerrainOperationTool
import ee
import time

tool_bp = Blueprint('tool', __name__)

datasets = None
datasetsNames = None
maxthread_num = 4


def ReturnOriginLayer(layer_ids, results, vis_params, message):
    '''
    返回原始图层
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
    
def ReturnNewLayer(layer_ids, results, original_names, message, result_type=''):
    '''
    返回新的图层处理函数
    参数:
        layer_ids: 原始图层ID列表
        results: 处理结果列表 (ee.Image 对象列表)
        original_names: 原始图层名称字典
        message: 返回给前端的消息
        result_type: 结果类型标识(可选)，用于生成新图层名称前缀
    '''
    layer_results = []
    
    for i, result in enumerate(results):
        try:
            # 生成新的图层ID和名称
            timestamp = int(time.time())
            new_id = f"{result_type}_{timestamp}" if result_type else f"new_{timestamp}"
            original_name = original_names.get(layer_ids[i], f'Layer_{layer_ids[i]}')
            new_name = f"{original_name} ({result_type}结果)" if result_type else f"{original_name} (处理结果)"
            
            # 获取波段信息
            bandNames = result.bandNames().getInfo()
            
            # 获取处理函数设置的可视化参数，如果没有则使用默认参数
            try:
                vis_params = result.get('vis_params').getInfo()
            except:
                default_bands = bandNames[:3] if len(bandNames) >= 3 else bandNames
                vis_params = {
                    'bands': default_bands,
                    'min': 0,
                    'max': 1,
                    'gamma': 1.4
                }
            
            # 获取地图瓦片URL
            map_id = result.getMapId(vis_params)
            
            # 构建图层结果对象
            layer_result = {
                'layer_id': new_id,
                'name': new_name,
                'tileUrl': map_id['tile_fetcher'].url_format,
                'bandInfo': bandNames,
                'visParams': vis_params,
                'type': 'Raster'
            }
            
            # 保存新的数据集
            save_dataset(new_id, result, new_name)
            
            layer_results.append(layer_result)
            
        except Exception as e:
            print(f"处理图层 {layer_ids[i]} 时出错: {str(e)}")
            continue
    
    if not layer_results:
        raise ValueError("没有成功处理的结果")
    
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
        
        return ReturnOriginLayer(layer_ids, results, vis_params, '除云处理完成')
        
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
        
        def process_layer(layer_id, images_list=None, index_type=None):
            try:
                i = layer_ids.index(layer_id)
                image = ee.Image(images_list.get(i))
                result = IndexTool.calculate_index(image, index_type)
                return result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        # 使用通用的并行处理函数
        results = ParallelProcessor.process_layers(
            layer_ids=layer_ids,
            process_func=process_layer,
            max_workers=maxthread_num,
            images_list=images_list,
            index_type=index_type
        )

        if not results:
            raise ValueError("No successful index calculation results")
            
        # 转换结果为 ee.List
        results = ee.List(results)
        
        # 使用原有的 common_process 处理结果
        return ReturnOriginLayer(layer_ids, results, vis_params, f'已添加 {index_type.upper()} 波段')
        
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
        return ReturnOriginLayer(layer_ids, results, vis_params, '图像填补处理完成')
        
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
        
        def process_layer(layer_id, images_list=None, cluster_counts=None):
            try:
                i = layer_ids.index(layer_id)
                num_clusters = cluster_counts.get(layer_id, 5)
                result = ClassificationTool.kmeans_clustering(
                    ee.Image(images_list.get(i)), 
                    num_clusters
                )
                # 设置聚类结果的可视化参数
                result = result.set('vis_params', {
                    'bands': ['cluster'],
                    'min': 0,
                    'max': num_clusters - 1
                })
                return result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        # 使用通用的并行处理函数
        results = ParallelProcessor.process_layers(
            layer_ids=layer_ids,
            process_func=process_layer,
            max_workers=maxthread_num,
            images_list=images_list,
            cluster_counts=cluster_counts
        )

        if not results:
            raise ValueError("No successful classification results")

        return ReturnNewLayer(
            layer_ids=layer_ids,
            results=results,
            original_names=datasetsNames,
            message='K-means聚类分析完成',
            result_type='kmeans'
        )
        
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

        
        return ReturnOriginLayer(layer_ids, results, vis_params, '直方图均衡化处理完成')
        
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
        
        samples = get_all_samples()
        if not samples:
            raise ValueError('No training samples available')
            
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        images_list = selected_images.toList(len(layer_ids))
        
        def process_layer(layer_id, images_list=None, rf_params=None, samples=None):
            try:
                i = layer_ids.index(layer_id)
                layer_params = rf_params.get(layer_id, {})
                num_trees = layer_params.get('numberOfTrees', 50)
                train_ratio = layer_params.get('trainRatio', 0.7)
                
                image = ee.Image(images_list.get(i))
                result = ClassificationTool.random_forest_classification(
                    image, samples,
                    num_trees=num_trees,
                    train_ratio=train_ratio
                )
                # 设置分类结果的可视化参数
                result = result.set('vis_params', {
                    'bands': ['classification'],
                    'min': 0,
                    'max': len(samples) - 1
                })
                return result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        results = ParallelProcessor.process_layers(
            layer_ids=layer_ids,
            process_func=process_layer,
            max_workers=maxthread_num,
            images_list=images_list,
            rf_params=rf_params,
            samples=samples
        )

        if not results:
            raise ValueError("No successful classification results")

        return ReturnNewLayer(
            layer_ids=layer_ids,
            results=results,
            original_names=datasetsNames,
            message='随机森林分类完成',
            result_type='rf'
        )
        
    except Exception as e:
        print(f"Error in random_forest: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/raster-calculator', methods=['POST'])
def raster_calculator():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        expression = data.get('expression')
        mode = data.get('mode', 'single')

        if mode == 'multi':
            # 多图层模式 - 一次性处理所有图层
            result = RasterOperatorTool.raster_calculator_multi(layer_ids, expression, datasets, datasetsNames)
            # 设置计算结果的可视化参数
            vis_params = get_vis_params(result)
            result = result.set('vis_params', vis_params)
            results = [result]  # 将单个结果转换为列表
            
            return ReturnNewLayer(
                layer_ids=layer_ids,
                results=results,
                original_names=datasetsNames,
                message='多图层计算完成',
                result_type='calc_multi'
            )
                
        elif mode == 'all_bands':
            selected_bands = eval(expression)
            print('Tool_routes.py - raster_calculator-selected_bands:', selected_bands)
            
            def process_layer(layer_id, selected_bands=None):
                try:
                    if layer_id not in datasets:
                        return None
                    image = ee.Image(datasets[layer_id])
                    result = RasterOperatorTool.raster_calculator_all_bands(
                        image, 
                        expression,
                        selected_bands
                    )
                    # 设置计算结果的可视化参数
                    vis_params = get_vis_params(result)
                    result = result.set('vis_params', vis_params)
                    return result
                except Exception as e:
                    print(f"Error processing layer {layer_id}: {str(e)}")
                    return None

            results = ParallelProcessor.process_layers(
                layer_ids=layer_ids,
                process_func=process_layer,
                max_workers=maxthread_num,
                selected_bands=selected_bands
            )
            
            return ReturnNewLayer(
                layer_ids=layer_ids,
                results=results,
                original_names=datasetsNames,
                message='全波段计算完成',
                result_type='calc_all'
            )

        else:
            # 单波段模式
            def process_layer(layer_id, expression=None):
                try:
                    if layer_id not in datasets:
                        return None
                    image = ee.Image(datasets[layer_id])
                    result = RasterOperatorTool.raster_calculator_single(image, expression)
                    # 设置计算结果的可视化参数
                    vis_params = get_vis_params(result)
                    result = result.set('vis_params', vis_params)
                    return result
                except Exception as e:
                    print(f"Error processing layer {layer_id}: {str(e)}")
                    return None

            results = ParallelProcessor.process_layers(
                layer_ids=layer_ids,
                process_func=process_layer,
                max_workers=maxthread_num,
                expression=expression
            )

            return ReturnNewLayer(
                layer_ids=layer_ids,
                results=results,
                original_names=datasetsNames,
                message='单波段计算完成',
                result_type='calc'
            )

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
        
        return ReturnOriginLayer(layer_ids, results, vis_params, '波段重命名完成')
        
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
        svm_params = data.get('svm_params', {})
        
        samples = get_all_samples()
        if not samples:
            raise ValueError('No training samples available')
            
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        images_list = selected_images.toList(len(layer_ids))
        
        def process_layer(layer_id, images_list=None, svm_params=None, samples=None):
            try:
                i = layer_ids.index(layer_id)
                layer_params = svm_params.get(layer_id, {})
                kernel = layer_params.get('kernel', 'RBF')
                train_ratio = layer_params.get('trainRatio', 0.7)
                
                image = ee.Image(images_list.get(i))
                result = ClassificationTool.svm_classification(
                    image, samples,
                    kernel=kernel,
                    train_ratio=train_ratio
                )
                # 设置分类结果的可视化参数
                result = result.set('vis_params', {
                    'bands': ['classification'],
                    'min': 0,
                    'max': len(samples) - 1
                })
                return result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        results = ParallelProcessor.process_layers(
            layer_ids=layer_ids,
            process_func=process_layer,
            max_workers=maxthread_num,
            images_list=images_list,
            svm_params=svm_params,
            samples=samples
        )

        if not results:
            raise ValueError("No successful classification results")

        return ReturnNewLayer(
            layer_ids=layer_ids,
            results=results,
            original_names=datasetsNames,
            message='SVM分类完成',
            result_type='svm'
        )
        
    except Exception as e:
        print(f"Error in svm_classification: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    

@tool_bp.route('/mosaic', methods=['POST'])
def mosaic():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        print('Tool_routes.py - mosaic-data:', data)
        
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)
        # 执行拼接
        result = RasterOperatorTool.img_mosaic(selected_images)
        
        # 设置拼接结果的可视化参数
        vis_params = get_vis_params(result)
        result = result.set('vis_params', vis_params)

        return ReturnNewLayer(
            layer_ids=layer_ids,
            results=[result],  # 拼接只有一个结果
            original_names=datasetsNames,
            message='影像拼接完成',
            result_type='mosaic'
        )

    except Exception as e:
        print(f"Error in mosaic: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/clip', methods=['POST'])
def clip():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')
        geometry = data.get('geometry',{})
        print('Tool_routes.py - clip-data:', data)
        
        def process_layer(layer_id, geometry=None):
            try:
                if layer_id not in datasets:
                    return None
                image = ee.Image(datasets[layer_id])
                result = RasterOperatorTool.img_clip(image, geometry)
                # 设置裁剪结果的可视化参数
                vis_params = get_vis_params(result)
                result = result.set('vis_params', vis_params)
                return result
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        # 使用通用的并行处理函数
        results = ParallelProcessor.process_layers(
            layer_ids=layer_ids,
            process_func=process_layer,
            max_workers=maxthread_num,
            geometry=geometry
        )

        if not results:
            raise ValueError("No successful clip results")

        return ReturnNewLayer(
            layer_ids=layer_ids,
            results=results,
            original_names=datasetsNames,
            message='影像裁剪完成',
            result_type='clip'
        )

    except Exception as e:
        print(f"Error in clip: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@tool_bp.route('/terrain', methods=['POST'])
def terrain():
    try:
        data = request.json
        layer_ids = data.get('layer_ids')

        PreprocessingTool.validate_inputs(layer_ids, datasets)
        selected_images = PreprocessingTool.get_image_collection(layer_ids, datasets)

        def process_layer(layer_id):
            try:
                if layer_id not in datasets:
                    return None
                image = ee.Image(datasets[layer_id])
                    
                # 执行地形分析
                result = TerrainOperationTool.terrain(image)
                
                # 保持原始图像的边界范围
                result = result.clip(image.geometry())
                
                return result   
            except Exception as e:
                print(f"Error processing layer {layer_id}: {str(e)}")
                return None

        results = ParallelProcessor.process_layers(
            layer_ids=layer_ids,
            process_func=process_layer,
            max_workers=maxthread_num
        )

        if not results:
            raise ValueError("No successful terrain analysis results")

        return ReturnNewLayer(
            layer_ids=layer_ids,
            results=results,
            original_names=datasetsNames,
            message='地形分析完成',
            result_type='terrain'
        )

    except Exception as e:
        print(f"Error in terrain analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500








