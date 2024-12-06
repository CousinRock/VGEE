from flask import Blueprint, jsonify, request
from services.map_service import get_map_data_service,remove_dataset
import ee

map_bp = Blueprint('map', __name__)

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
            # 将所有多边形合并成一个
            merged_area = ee.Geometry.MultiPolygon(study_areas)

        # 传入合并后的研究区域进行筛选和裁���
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
        geometry = data['geometry']
        
        # 将新的多边形坐标添加到列表中
        study_areas.append(geometry['coordinates'][0])
            
        print(f"Map_routes.py - Added new study area. Total areas: {len(study_areas)}")
        
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
        deleted_coordinates = data['coordinates']
        
        # 将要删除的���标转换为字符串进行比较
        deleted_str = [str(coords) for coords in deleted_coordinates]
        
        # 过滤掉被删除的坐标
        study_areas = [area for area in study_areas 
                      if str(area) not in deleted_str]
        
        
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