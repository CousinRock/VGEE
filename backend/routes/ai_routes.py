from flask import Blueprint, jsonify, request
from services.map_service import get_dataset
from services.ai_service import segment_img
import ee

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/segment', methods=['POST'])
def segment_image():
   try:
       data = request.json
       print('AI_routes.py - segment_image - data:', data)
       url = data.get('url')
       result = segment_img(url)
       print('AI_routes.py - segment_image - result:', result)

       return jsonify({'message': 'Segmentation completed successfully'}), 200

   except Exception as e:
        print(f"AI_routes.py - Error in segment_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

