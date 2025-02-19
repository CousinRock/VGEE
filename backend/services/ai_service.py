from samgeo import SamGeo
from samgeo.text_sam import LangSAM
import time
import os
import numpy as np
import cv2
import requests
import tempfile
import traceback

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
        
        # 存储所有掩膜结果
        all_masks = []
        
        if sam.masks is not None:
            min_x, min_y, max_x, max_y = image_bounds
            
            # 遍历每个掩膜
            for mask in sam.masks:
                mask = mask.cpu().numpy()
                
                # 处理掩膜轮廓
                contours, _ = cv2.findContours(
                    mask.astype(np.uint8), 
                    cv2.RETR_EXTERNAL, 
                    cv2.CHAIN_APPROX_SIMPLE
                )
                
                # 转换每个轮廓为地理坐标
                for contour in contours:
                    geo_coords = []
                    for point in contour:
                        x, y = point[0]
                        geo_x = float(min_x + (x / img_width) * (max_x - min_x))
                        geo_y = float(max_y - (y / img_height) * (max_y - min_y))
                        geo_coords.append([geo_x, geo_y])
                    
                    # 确保多边形闭合
                    if geo_coords[0] != geo_coords[-1]:
                        geo_coords.append(geo_coords[0])
                        
                    all_masks.append(geo_coords)
        
        # 清理临时文件
        cleanup_temp_files()
        
        return all_masks
        
    except Exception as e:
        cleanup_temp_files()
        print(f"Error in segment_img: {str(e)}")
        return None

def text_single_layer(layer_id, datasets, datasetsNames, params, vis_params):
    """处理单个语义识别的函数"""
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
        mask_coords = text_segment_img(url, image_bounds, {
            'textPrompt': text_prompt,
            'threshold': threshold
        }, dimensions)
        
        if mask_coords is None or len(mask_coords) == 0:
            return None

        # 创建掩膜图层
        mask_layer = {
            'layer_id': f'{layer_id}_mask_{int(time.time())}',  # 包含原始layer_id
            'name': f'{image_name}_mask',
            'type': 'vector',
            'geometryType': 'Polygon',
            'coordinates': mask_coords,
            'visParams': {
                'color': '#ff0000',
                'weight': 2,
                'opacity': 1,
                'fillOpacity': 0.3
            }
        }

        return mask_layer
    except Exception as e:
        print(f"Error processing layer {layer_id}: {str(e)}")
        traceback.print_exc()  # 添加详细的错误跟踪
        return None
    
    
def point_segment_img(url, image_bounds, samples, dimensions='1024x1024'):
    '''
    点提示分割图像
    '''
    try:
        # 初始化 SAM 模型
        sam = SamGeo(
            model_type="vit_h",
            automatic=False,
            sam_kwargs=None,
        )
        
        # 直接在内存中读取图像
        response = requests.get(url)
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # 直接设置图像数组
        sam.set_image(image)
        
        # 从 dimensions 提取图像宽高
        try:
            img_width, img_height = map(int, dimensions.split('x'))
        except ValueError:
            img_width, img_height = 1024, 1024
            
        # 转换样本数据格式
        point_coords = []
        point_labels = []
        for layer_name, layer_data in samples.items():
            for feature in layer_data['features']:
                coords = feature['coordinates']
                # 转换地理坐标到图像坐标
                img_x = int((coords[0] - image_bounds[0]) / (image_bounds[2] - image_bounds[0]) * img_width)
                img_y = int((image_bounds[3] - coords[1]) / (image_bounds[3] - image_bounds[1]) * img_height)
                point_coords.append([img_x, img_y])
                point_labels.append(1)  # 1 表示前景点
        
        point_coords = np.array(point_coords)
        point_labels = np.array(point_labels)
        
        print('Image coordinates:', point_coords)
        print('Point labels:', point_labels)
            
        # 执行分割预测
        masks, scores, logits = sam.predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels
        )
        
        # 将掩码转换为地理坐标
        coordinates = []
        if masks is not None and len(masks) > 0:
            # 获取图像边界
            min_x, min_y, max_x, max_y = image_bounds
            
            # 找到得分最高的掩码
            best_mask_idx = np.argmax(scores)
            mask = masks[best_mask_idx]
            
            # 使用 OpenCV 找到掩码的轮廓
            contours, _ = cv2.findContours(
                mask.astype(np.uint8), 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # 转换每个轮廓为地理坐标
            for contour in contours:
                geo_coords = []
                for point in contour:
                    x, y = point[0]
                    geo_x = float(min_x + (x / img_width) * (max_x - min_x))
                    geo_y = float(max_y - (y / img_height) * (max_y - min_y))
                    geo_coords.append([geo_x, geo_y])
                
                # 确保多边形闭合
                if geo_coords[0] != geo_coords[-1]:
                    geo_coords.append(geo_coords[0])
                    
                coordinates.append(geo_coords)
        
        return coordinates
        
    except Exception as e:
        print(f"Error in point_segment_img: {str(e)}")
        traceback.print_exc()
        return None

def point_single_layer(layer_id, datasets, datasetsNames, samples, vis_params):
    """处理单个点提示分割的函数"""
    try:
        image = datasets[layer_id]
        image_name = datasetsNames[layer_id]
        print('ai_service-point_segment-image_name', image_name)
        
        
        # 获取该图层的显示参数
        layer_vis = vis_params.get(layer_id, {})
        layer_min = layer_vis.get('min', 0)
        layer_max = layer_vis.get('max', 255)
        
        # 获取图像边界
        bounds = image.geometry().bounds().getInfo()['coordinates'][0]
        print('ai_service-point_segment-bounds', bounds)


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
        coordinates = point_segment_img(url, image_bounds, samples, dimensions)
        

        if coordinates is None:
            return None

        return {
            'layer_id': f'sam_prediction_{layer_id}_{int(time.time())}',
            'name': f'{image_name}_SAM_point_prediction',
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
