from samgeo import SamGeo
from samgeo.text_sam import LangSAM
import ee
import time
import os

def cleanup_temp_files():
    """清理临时文件"""
    current_dir = os.path.dirname(os.path.dirname(__file__))
    for filename in os.listdir(current_dir):
        if len(filename) > 16 and '.' not in filename:
            try:
                os.remove(os.path.join(current_dir, filename))
            except Exception as e:
                print(f"Error removing temp file {filename}: {str(e)}")


def text_segment_img(url, image_bounds, params, dimensions='1024x1024'):
    '''
    语义分割图像
    '''
    try:
        # 使用单例模型实例
        sam = LangSAM()

        # 从参数中获取文本提示和阈值
        text_prompt = params.get('textPrompt', "house")
        threshold = params.get('threshold', 0.24)
        print(f"text_prompt: {text_prompt}, threshold: {threshold}")
        
        # 从 dimensions 提取图像宽高
        try:
            img_width, img_height = map(int, dimensions.split('x'))
        except ValueError:
            img_width, img_height = 1024, 1024  # 默认值

        # 执行分割
        sam.predict(url, text_prompt, box_threshold=threshold, text_threshold=threshold)
        
        # 将边界框转换为地理坐标
        coordinates = []
        if sam.boxes is not None and len(sam.boxes) > 0:
            # 获取图像边界
            min_x, min_y, max_x, max_y = image_bounds
            
            for box in sam.boxes:
                box = box.cpu().numpy()
                
                # 将像素坐标转换为地理坐标，并转换为 Python float
                geo_x1 = float(min_x + (box[0] / img_width) * (max_x - min_x))
                geo_y1 = float(max_y - (box[1] / img_height) * (max_y - min_y))
                geo_x2 = float(min_x + (box[2] / img_width) * (max_x - min_x))
                geo_y2 = float(max_y - (box[3] / img_height) * (max_y - min_y))
                
                # 创建矩形坐标，确保所有值都是 Python float
                rect_coords = [
                    [geo_x1, geo_y1],  # 左上
                    [geo_x2, geo_y1],  # 右上
                    [geo_x2, geo_y2],  # 右下
                    [geo_x1, geo_y2],  # 左下
                    [geo_x1, geo_y1]   # 闭合多边形
                ]
                coordinates.append(rect_coords)
        
        # 清理临时文件
        cleanup_temp_files()
        
        return coordinates
        
    except Exception as e:
        cleanup_temp_files()
        print(f"Error in segment_img: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def text_single_layer(layer_id, datasets, datasetsNames, params, vis_params):
    """处理单个图层的函数"""
    try:
        image = datasets[layer_id]
        image_name = datasetsNames[layer_id]
        print('ai_routes-segment_image-image_name', image_name)
        
        # 获取该图层的特定参数
        layer_params = params.get(layer_id, {})
        text_prompt = layer_params.get('textPrompt', 'house')
        threshold = layer_params.get('threshold', 0.24)
        
        # 获取该图层的显示参数
        layer_vis = vis_params.get(layer_id, {})
        layer_min = layer_vis.get('min', 0)
        layer_max = layer_vis.get('max', 255)
        
        # 获取图像边界
        bounds = image.geometry().bounds().getInfo()['coordinates'][0]
        print('ai_routes-segment_image-bounds', bounds)

        image_bounds = [
            bounds[0][0],  # min_x
            bounds[0][1],  # min_y
            bounds[2][0],  # max_x
            bounds[2][1]   # max_y
        ]

        # 获取缩略图URL
        dimensions = '1024x1024'
        url = image.getThumbURL({
            'region': image.geometry(),
            'min': layer_min,
            'max': layer_max,
            'dimensions': dimensions
        })

        print(f"Generated URL for layer {layer_id}: {url}")
        coordinates = text_segment_img(url, image_bounds, {
            'textPrompt': text_prompt,
            'threshold': threshold
        }, dimensions)
        
        if coordinates is None:
            return None

        return {
            'layer_id': f'sam_prediction_{layer_id}_{int(time.time())}',
            'name': f'{image_name}_SAM预测结果',
            'type': 'vector',
            'geometryType': 'Polygon',
            'coordinates': coordinates,
            'visParams': {
                'color': '#ff0000',
                'weight': 2,
                'opacity': 1,
                'fillOpacity': 0.5
            }
        }
    except Exception as e:
        print(f"Error processing layer {layer_id}: {str(e)}")
        return None
