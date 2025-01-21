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
        text_prompt = "house"
        box_threshold = 0.24
        text_threshold = 0.24
        
        # 从 dimensions 提取图像宽高
        try:
            img_width, img_height = map(int, dimensions.split('x'))
        except ValueError:
            img_width, img_height = 1024, 1024  # 默认值

        # 执行分割
        sam.predict(url, text_prompt, box_threshold=box_threshold, text_threshold=text_threshold)
        
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


