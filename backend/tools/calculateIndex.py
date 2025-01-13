from .base_tool import BaseTool
import ee

class IndexTool(BaseTool):
    @staticmethod
    def calculate_index(image, index_type):
        """计算各种遥感指数"""
        try:
            # 定义指数计算函数
            index_functions = {
                'ndvi': lambda img: img.normalizedDifference([IndexTool.get_band_name(img, 'NIR'), IndexTool.get_band_name(img, 'RED')]).rename('NDVI'),
                'ndwi': lambda img: img.normalizedDifference([IndexTool.get_band_name(img, 'GREEN'), IndexTool.get_band_name(img, 'NIR')]).rename('NDWI'),
                'ndbi': lambda img: img.normalizedDifference([IndexTool.get_band_name(img, 'SWIR1'), IndexTool.get_band_name(img, 'NIR')]).rename('NDBI'),
                'evi': lambda img: img.expression(
                    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                    {
                        'NIR': img.select(IndexTool.get_band_name(img, 'NIR')),
                        'RED': img.select(IndexTool.get_band_name(img, 'RED')),
                        'BLUE': img.select(IndexTool.get_band_name(img, 'BLUE'))
                    }
                ).rename('EVI'),
                'savi': lambda img: img.expression(
                    '((NIR - RED) * (1 + L)) / (NIR + RED + L)',
                    {
                        'NIR': img.select(IndexTool.get_band_name(img, 'NIR')),
                        'RED': img.select(IndexTool.get_band_name(img, 'RED')),
                        'L': 0.5
                    }
                ).rename('SAVI'),
                'mndwi': lambda img: img.normalizedDifference([IndexTool.get_band_name(img, 'GREEN'), IndexTool.get_band_name(img, 'SWIR1')]).rename('MNDWI'),
                'bsi': lambda img: img.expression(
                    '((SWIR1 + RED) - (NIR + BLUE)) / ((SWIR1 + RED) + (NIR + BLUE))',
                    {
                        'SWIR1': img.select(IndexTool.get_band_name(img, 'SWIR1')),
                        'RED': img.select(IndexTool.get_band_name(img, 'RED')),
                        'NIR': img.select(IndexTool.get_band_name(img, 'NIR')),
                        'BLUE': img.select(IndexTool.get_band_name(img, 'BLUE'))
                    }
                ).rename('BSI')
            }
            
            if index_type not in index_functions:
                raise ValueError(f"Unsupported index type: {index_type}")
                
            index = index_functions[index_type](image)
            return image.addBands(index)
            
        except Exception as e:
            raise Exception(f"Error calculating {index_type}: {str(e)}")

    @staticmethod
    def get_band_name(image, target_band):
        """获取目标波段的名称"""
        band_names = image.bandNames()
        # 使用服务器端的字符串匹配来查找波段
        matched_band = band_names.filter(ee.Filter.stringContains('item', target_band)).get(0)
        return ee.String(matched_band)
