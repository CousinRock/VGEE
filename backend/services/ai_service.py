from samgeo import SamGeo
from samgeo.text_sam import LangSAM
import ee
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

def segment_img(url, image_bounds, dimensions='1024x1024'):
    try:
        # 使用单例模型实例
        sam = LangSAM()
        
        # 设置分割参数
        text_prompt = "house"  # 可以根据需要修改提示词
        box_threshold = 0.24
        text_threshold = 0.24
        
        # 从 dimensions 提取图像宽高
        try:
            img_width, img_height = map(int, dimensions.split('x'))
        except ValueError:
            img_width, img_height = 1024, 1024  # 默认值

        # 执行分割
        sam.predict(url, text_prompt, box_threshold=box_threshold, text_threshold=text_threshold)
        
        # 将边界框转换为 EE 几何对象
        features = []
        if sam.boxes is not None and len(sam.boxes) > 0:
            # 获取图像边界
            min_x, min_y, max_x, max_y = image_bounds
            
            for box in sam.boxes:
                box = box.cpu().numpy()
                
                # 将像素坐标（0-图像宽高）转换为地理坐标
                geo_x1 = min_x + (box[0] / img_width) * (max_x - min_x)
                geo_y1 = max_y - (box[1] / img_height) * (max_y - min_y)  # 注意 y 轴方向
                geo_x2 = min_x + (box[2] / img_width) * (max_x - min_x)
                geo_y2 = max_y - (box[3] / img_height) * (max_y - min_y)
                
                # 创建矩形几何对象
                geometry = ee.Geometry.Rectangle([
                    float(geo_x1),  # west
                    float(geo_y2),  # south
                    float(geo_x2),  # east
                    float(geo_y1)   # north
                ])
                
                # 创建要素
                feature = ee.Feature(geometry)
                features.append(feature)
        
        # 创建要素集合
        feature_collection = ee.FeatureCollection(features)
        
        # 清理临时文件
        cleanup_temp_files()
        
        return feature_collection
    except Exception as e:
        cleanup_temp_files()  # 发生错误时也清理
        print(f"Error in segment_img: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


