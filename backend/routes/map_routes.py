from flask import Blueprint, jsonify, request
from services.map_service import get_map_data_service

map_bp = Blueprint('map', __name__)

@map_bp.route('/map-data', methods=['GET'])
def get_map_data():
    try:
        # 获取前端参数
        satellite = request.args.get('satellite', 'LANDSAT')
        start_date = request.args.get('startDate', '2023-01-01')
        end_date = request.args.get('endDate', '2023-12-31')
        cloud_cover = float(request.args.get('cloudCover', 20))
        
        print(f"Received satellite: {satellite}, startDate: {start_date}, endDate: {end_date}, cloudCover: {cloud_cover}")
        result = get_map_data_service(satellite, start_date, end_date, cloud_cover)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in get_map_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 