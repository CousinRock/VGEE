from flask import Blueprint, jsonify, request
from services.map_service import get_all_datasets
from services.ai_service import text_single_layer, point_single_layer
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.sample_service import get_all_samples

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/text_segment', methods=['POST'])
def text_segment():
    '''
    文本提示分割
    '''
    try:
        data = request.json


        print('AI_routes.py - text_segment - data:', data)     

        layer_ids = data.get('layer_ids', [])
        vis_params = data.get('visParams', {})
        params = data.get('params', {})
        
        if not layer_ids:
            raise ValueError("No layer ID provided")
            
        datasets, datasetsNames = get_all_datasets()
        results = []
        
        # 使用线程池并行处理图层
        with ThreadPoolExecutor(max_workers=min(len(layer_ids), 4)) as executor:
            future_to_layer = {
                executor.submit(
                    text_single_layer, 
                    layer_id, 
                    datasets, 
                    datasetsNames, 
                    params, 
                    vis_params
                ): layer_id for layer_id in layer_ids

            }
            
            for future in as_completed(future_to_layer):
                result = future.result()
                if result is not None:
                    results.append(result)

        if not results:
            raise ValueError("No successful segmentation results")

        return jsonify({
            'success': True,
            'message': 'Segmentation completed successfully',
            'results': results
        }), 200

    except Exception as e:
        print(f"AI_routes.py - Error in segment_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        

@ai_bp.route('/point_segment', methods=['POST'])
def point_segment():
    '''
    点提示分割
    '''
    try:
        data = request.json
        print('AI_routes.py - point_segment - data:', data)

        layer_ids = data.get('layer_ids', [])
        vis_params = data.get('visParams', {})
        samples = get_all_samples()
        print('AI_routes.py - point_segment - samples:', samples)
        
        if not layer_ids:
            raise ValueError("No layer ID provided")
            
        datasets, datasetsNames = get_all_datasets()
        results = []
        
        # 使用线程池并行处理图层
        with ThreadPoolExecutor(max_workers=min(len(layer_ids), 4)) as executor:
            future_to_layer = {
                executor.submit(
                    point_single_layer, 
                    layer_id, 
                    datasets, 
                    datasetsNames, 
                    samples,
                    vis_params
                ): layer_id for layer_id in layer_ids
            }

            
            for future in as_completed(future_to_layer):
                result = future.result()
                if result is not None:
                    results.append(result)

        if not results:
            raise ValueError("No successful segmentation results")

        return jsonify({
            'success': True,
            'message': 'Point segmentation completed successfully',
            'results': results
        }), 200

    except Exception as e:
        print(f"AI_routes.py - Error in point_segment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
        
