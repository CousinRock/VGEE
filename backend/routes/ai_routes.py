from flask import Blueprint, jsonify, request
from services.map_service import get_all_datasets
from services.ai_service import text_single_layer, point_single_layer
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.sample_service import get_all_samples
from tools.parallel_processor import ParallelProcessor

ai_bp = Blueprint('ai', __name__)
maxthread_num = 4

@ai_bp.route('/text_segment', methods=['POST'])
def text_segment():
    '''
    文本提示分割
    '''
    try:
        data = request.json
        layer_ids = data.get('layer_ids', [])
        vis_params = data.get('visParams', {})
        params = data.get('params', {})
        
        if not layer_ids:
            raise ValueError("No layer ID provided")
            
        datasets, datasetsNames = get_all_datasets()
        
        # 使用通用的并行处理函数
        results = ParallelProcessor.process_layers(
            layer_ids=layer_ids,
            process_func=text_single_layer,
            max_workers=maxthread_num,
            datasets=datasets,
            datasetsNames=datasetsNames,
            params=params,
            vis_params=vis_params
        )

        if not results:
            raise ValueError("No successful segmentation results")

        return jsonify({
            'success': True,
            'message': 'Segmentation completed successfully',
            'results': results
        }), 200

    except Exception as e:
        print(f"Error in segment_image: {str(e)}")
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
        layer_ids = data.get('layer_ids', [])
        vis_params = data.get('visParams', {})
        samples = get_all_samples()
        
        if not layer_ids:
            raise ValueError("No layer ID provided")
            
        datasets, datasetsNames = get_all_datasets()
        
        # 使用通用的并行处理函数
        results = ParallelProcessor.process_layers(
            layer_ids=layer_ids,
            process_func=point_single_layer,
            max_workers=maxthread_num,
            datasets=datasets,
            datasetsNames=datasetsNames,
            samples=samples,
            vis_params=vis_params
        )

        if not results:
            raise ValueError("No successful segmentation results")

        return jsonify({
            'success': True,
            'message': 'Point segmentation completed successfully',
            'results': results
        }), 200

    except Exception as e:
        print(f"Error in point_segment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
        
