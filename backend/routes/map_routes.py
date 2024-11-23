from flask import Blueprint, jsonify, request
from services.map_service import get_map_data_service
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
        
        print(f"Received satellite: {satellite}, startDate: {start_date}, endDate: {end_date}, cloudCover: {cloud_cover}")
        
        # 如果有多个研究区域，将它们合并成一个多边形
        merged_area = None
        if study_areas:
            # 将所有多边形合并成一个
            merged_area = ee.Geometry.MultiPolygon(study_areas)
            
        # 传入合并后的研究区域进行筛选和裁剪
        result = get_map_data_service(satellite, start_date, end_date, cloud_cover, merged_area)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in get_map_data: {str(e)}")
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
            
        print(f"Added new study area. Total areas: {len(study_areas)}")
        
        return jsonify({
            'success': True,
            'message': f'Study area added successfully. Total areas: {len(study_areas)}'
        })

    except Exception as e:
        print(f"Error in filter_by_geometry: {str(e)}")
        return jsonify({'error': str(e)}), 500

@map_bp.route('/remove-geometry', methods=['POST'])
def remove_geometry():
    try:
        global study_areas
        data = request.json
        deleted_coordinates = data['coordinates']
        
        # 将要删除的坐标转换为字符串进行比较
        deleted_str = [str(coords) for coords in deleted_coordinates]
        
        # 过滤掉被删除的坐标
        study_areas = [area for area in study_areas 
                      if str(area) not in deleted_str]
        
        
        print(f"Removed geometries. Remaining areas: {len(study_areas)}")
        
        return jsonify({
            'success': True,
            'message': f'Geometries removed successfully. Remaining areas: {len(study_areas)}'
        })

    except Exception as e:
        print(f"Error in remove_geometry: {str(e)}")
        return jsonify({'error': str(e)}), 500