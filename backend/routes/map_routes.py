from flask import Blueprint, jsonify, request
from services.map_service import get_map_data_service,remove_dataset,compute_image_stats,get_dataset,save_dataset,get_all_datasets
from config.satellite_config import SATELLITE_CONFIGS
import ee
from services.sample_service import add_sample_service, remove_sample_service,get_all_samples
from flask_cors import CORS

map_bp = Blueprint('map', __name__)
CORS(map_bp)

# 存储研究区域列表
study_areas = []

@map_bp.route('/map-data', methods=['GET'])
def get_map_data():
    try:
        # 获取前端参数
        satellite = request.args.get('satellite', 'LANDSAT')
        start_date = request.args.get('startDate', '2023-01-01')
        end_date = request.args.get('endDate', '2023-12-31')
        cloud_cover = float(request.args.get('cloudCover', 20))
        layerName = request.args.get('layerName',None)
        
        print(f"Map_routes.py - Received satellite: {satellite}, startDate: {start_date}," +
              f"endDate: {end_date}, cloudCover: {cloud_cover}, layerName:{layerName}")
        
        # 如果有多个研究区域，将它们合并成一个多边形
        merged_area = None
        if study_areas:
            # 将所有多边形合并成一个，只使用坐标部分
            merged_area = ee.Geometry.MultiPolygon([area['coordinates'] for area in study_areas])

        # 传入合并后的研究区域进行筛选和裁
        result = get_map_data_service(satellite, start_date, end_date, 
                                      cloud_cover, merged_area,layerName)
        return jsonify(result)
        
    except Exception as e:
        print(f"Map_routes.py - Error in get_map_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 
    
@map_bp.route('/filter-by-geometry', methods=['POST'])
def filter_by_geometry():
    try:
        global study_areas
        data = request.json
        print(f"Map_routes.py - Received data: {data}")
        
        if data.get('type') == 'vector':
            # 处理矢量资产
            asset_id = data.get('asset_id')
            vector_asset = ee.FeatureCollection(asset_id)
            
            # 在服务器端处理几何信息
            def extract_geometry(feature):
                geometry = feature.geometry()
                coordinates = ee.List([])
                
                # 判断几何类型并提取外环坐标
                geometry_type = geometry.type()
                coordinates = ee.Algorithms.If(
                    geometry_type.equals('Polygon'),
                    ee.List([geometry.coordinates().get(0)]),
                    ee.Algorithms.If(
                        geometry_type.equals('MultiPolygon'),
                        geometry.coordinates().map(lambda poly: ee.List(poly).get(0)),
                        ee.List([])
                    )
                )
                return ee.Feature(None, {
                    'coordinates': coordinates,
                    'asset_id': asset_id
                })
            
            # 将处理后的几何信息提取到列表
            processed_features = vector_asset.map(extract_geometry).getInfo()
            
            # 添加到 study_areas 列表
            for feature in processed_features['features']:
                study_areas.append({
                    'asset_id': feature['properties']['asset_id'],
                    'coordinates': feature['properties']['coordinates']
                })
            
            print(f"Map_routes.py - Added vector asset as study area. Total areas: {len(study_areas)}")
        
        else:
            # 处理手动绘制的几何图形
            geometry = data['geometry']
            study_areas.append({
                'asset_id': 'manual',
                'coordinates': [geometry['coordinates'][0]]
            })
            
        return jsonify({
            'success': True,
            'message': f'Study area added successfully. Total areas: {len(study_areas)}'
        })

    except Exception as e:
        print(f"Map_routes.py - Error in filter_by_geometry: {str(e)}")
        return jsonify({'error': str(e)}), 500


@map_bp.route('/remove-geometry', methods=['POST'])
def remove_geometry():
    try:
        global study_areas
        data = request.json
        print(f"Map_routes.py - Received data: {data}")
        
        if data.get('type') == 'vector':
            # 处理矢量资产
            asset_id = data.get('asset_id')
            # 获取移除前的数量
            before_count = len(study_areas)
            
            # 直接根据资产ID过滤
            study_areas = [area for area in study_areas if area['asset_id'] != asset_id]
            
            # 获取移除后的数量
            after_count = len(study_areas)
            print(f"Map_routes.py - Removed {before_count - after_count} areas for asset {asset_id}")
            
        else:
            # 处理手动绘制的几何图形
            deleted_coordinates = data['geometry']['coordinates']
            # 将要删除的坐标转换为字符串进行比较
            deleted_str = [str(coords) for coords in deleted_coordinates]
            # 过滤掉被删除的坐标
            study_areas = [area for area in study_areas 
                          if str(area['coordinates'][0]) not in deleted_str]
        
        print(f"Map_routes.py - Removed geometries. Remaining areas: {len(study_areas)}")
        
        return jsonify({
            'success': True,
            'message': f'Geometries removed successfully. Remaining areas: {len(study_areas)}'
        })

    except Exception as e:
        print(f"Map_routes.py - Error in remove_geometry: {str(e)}")
        return jsonify({'error': str(e)}), 500

@map_bp.route('/remove-layer', methods=['POST'])
def remove_layer():
    try:
        data = request.get_json()
        layer_id = data.get('layer_id')
        
        
        if not layer_id:
            return jsonify({
                'success': False,
                'message': '缺少图层ID'
            }), 400
            
        # 调用已有的 remove_dataset 服务
        remove_dataset(layer_id)
        
        return jsonify({
            'success': True,
            'message': '图层已从数据集中移除'
        })
        
    except Exception as e:
        print(f"Map_routes.py - Error removing layer: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'移除图层时发生错误: {str(e)}'
        }), 500

@map_bp.route('/compute-stats', methods=['POST'])
def compute_band_stats():
    try:
        data = request.get_json()
        layer_id = data.get('layer_id')
        bands = data.get('bands')
        print(f"Map_routes.py - Received bands: {bands}")

        if not layer_id or not bands:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
            
        # 从服务中获取数据集
        dataset = get_dataset(layer_id)
        if not dataset:
            return jsonify({
                'success': False,
                'message': '未找到指定图层'
            }), 404
            

        
        # 计算统计值
        stats = compute_image_stats(dataset, bands, dataset.geometry())
        
        if stats:
            stats_dict = stats.getInfo()
            print(f"Map_routes.py - Final stats: min={stats_dict.get('global_min')}, max={stats_dict.get('global_max')}")
            return jsonify({
                'success': True,
                'min': stats_dict.get('global_min'),
                'max': stats_dict.get('global_max')
            })
        else:
            return jsonify({
                'success': False,
                'message': '计算统计值失败'
            }), 500
            
    except Exception as e:
        print(f"Map_routes.py - Error computing stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'计算统计值时发生错误: {str(e)}'
        }), 500

@map_bp.route('/satellite-config', methods=['GET'])
def get_satellite_config():
    try:
        # 从 SATELLITE_CONFIGS 中提取配置信息
        satellite_options = []
        
        # Landsat 系列
        landsat_options = {
            'label': 'Landsat系列',
            'options': []
        }
        for sat_id, config in SATELLITE_CONFIGS.items():
            if 'LANDSAT' in sat_id:
                landsat_options['options'].append({
                    'value': sat_id,
                    'label': config['name_template'].split('(')[0].strip(),
                    'startDate': config['start_date'],
                    'endDate': config['end_date']
                })
        satellite_options.append(landsat_options)
        
        # Sentinel 系列
        sentinel_options = {
            'label': 'Sentinel系列',
            'options': []
        }
        for sat_id, config in SATELLITE_CONFIGS.items():
            if 'SENTINEL' in sat_id:
                sentinel_options['options'].append({
                    'value': sat_id,
                    'label': config['name_template'].split('(')[0].strip(),
                    'startDate': config['start_date'],
                    'endDate': config['end_date']
                })
        satellite_options.append(sentinel_options)
        
        # MODIS 系列
        modis_options = {
            'label': 'MODIS系列',
            'options': []
        }
        for sat_id, config in SATELLITE_CONFIGS.items():
            if 'MODIS' in sat_id:
                modis_options['options'].append({
                    'value': sat_id,
                    'label': config['name_template'].split('(')[0].strip(),
                    'startDate': config['start_date'],
                    'endDate': config['end_date']
                })
        satellite_options.append(modis_options)
        
        return jsonify({
            'success': True,
            'satelliteOptions': satellite_options
        })
        
    except Exception as e:
        print(f"Error getting satellite config: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@map_bp.route('/add-sample', methods=['POST'])
def add_sample():
    try:
        data = request.json
        result = add_sample_service(
            layer_id=data.get('layer_id'),
            class_name=data.get('class_name'),
            geometry_type=data.get('geometry_type'),
            features=data.get('features'),
            layer_type=data.get('type')
        )
        return jsonify(result)
    except Exception as e:
        print(f"Map_routes.py - Error in add_sample: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@map_bp.route('/remove-sample', methods=['POST'])
def remove_sample():
    try:
        data = request.json
        result = remove_sample_service(data.get('layer_id'))
        return jsonify(result)
    except Exception as e:
        print(f"Map_routes.py - Error in remove_sample: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@map_bp.route('/get-samples', methods=['GET'])
def get_samples():
    try:
        # 从 sample_service 获取所有样本
        samples = get_all_samples()
        return jsonify({
            'success': True,
            'samples': samples
        })
    except Exception as e:
        print(f"Error getting samples: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@map_bp.route('/rename-layer', methods=['POST'])
def rename_layer():
    try:
        data = request.json
        layer_id = data.get('layer_id')
        new_name = data.get('new_name')
        
        if not layer_id or not new_name:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
            
        # 更新图层名称
        save_dataset(layer_id, get_dataset(layer_id), new_name)
            
        return jsonify({
            'success': True,
            'message': '图层重命名成功'
        })
            
    except Exception as e:
        print(f"Error renaming layer: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@map_bp.route('/export-to-cloud', methods=['POST'])
def export_layer_to_cloud():
    try:
        data = request.get_json()
        layer_id = data.get('layer_id')
        layer_name = data.get('layer_name', 'export').replace(' ', '_')
        layer_type = data.get('layer_type')
        vis_params = data.get('vis_params')
        features = data.get('features', [])
        geometry_type = data.get('geometryType')
        folder = data.get('folder', 'EarthEngine_Exports')  # 获取文件夹参数
        
        # 确保导出名称符合 GEE 要求
        safe_name = ''.join(c for c in layer_name if c.isalnum() or c in '._-')[:100]
        safe_folder = ''.join(c for c in folder if c.isalnum() or c in '._-')  # 处理文件夹名称
        
        if layer_type == 'Raster':
            dataset, datasetsNames = get_all_datasets()
            img = ee.Image(dataset[layer_id]).toFloat()
            
            task = ee.batch.Export.image.toDrive(
                image=img,
                description=safe_name,
                folder=safe_folder,  # 使用用户指定的文件夹
                fileNamePrefix=safe_name,
                scale=30,
                region=img.geometry(),
                fileFormat='GeoTIFF',
                maxPixels=1e13
            )
            
        else:
            if layer_type == 'vector':
                vector_fc = ee.FeatureCollection(layer_id)
                task = ee.batch.Export.table.toDrive(
                    collection=vector_fc,
                    description=safe_name,
                    folder=safe_folder,  # 使用用户指定的文件夹
                    fileNamePrefix=safe_name,
                    fileFormat='SHP'
                )
            else:
                # 处理手动绘制的矢量数据
                features_list = []
                
                try:
                    if geometry_type == 'Point':
                        # 处理点数据
                        for feature in features:
                            if isinstance(feature['coordinates'], list) and len(feature['coordinates']) == 2:
                                ee_feature = ee.Feature(
                                    ee.Geometry.Point(feature['coordinates'])
                                )
                                features_list.append(ee_feature)
                    else:
                        # 处理多边形数据
                        for feature in features:
                            if isinstance(feature['coordinates'], list):
                                print(f"Processing polygon coordinates: {feature['coordinates']}")
                                ee_feature = ee.Feature(
                                    ee.Geometry.Polygon([feature['coordinates']])
                                )
                                features_list.append(ee_feature)
                except Exception as e:
                    print(f"Error processing features: {str(e)}")
                    raise
                
                if not features_list:
                    raise ValueError("No valid features to export")
                
                print(f"Created {len(features_list)} features")
                
                # 创建 FeatureCollection
                manual_fc = ee.FeatureCollection(features_list)
                
                task = ee.batch.Export.table.toDrive(
                    collection=manual_fc,
                    description=safe_name,
                    folder=safe_folder,  # 使用用户指定的文件夹
                    fileNamePrefix=safe_name,
                    fileFormat='SHP'
                )

        # 启动导出任务
        task.start()
        
        return jsonify({
            'success': True,
            'message': '导出任务已启动'
        })
    except Exception as e:
        print(f"Error exporting layer: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500