from .base_tool import BaseTool
import ee

class IndexTool(BaseTool):
    @staticmethod
    def calculate_index(image, index_type):
        """计算各种遥感指数"""
        try:
            index_functions = {
                'ndvi': lambda img: img.normalizedDifference(['B5', 'B4']).rename('NDVI'),
                'ndwi': lambda img: img.normalizedDifference(['B3', 'B5']).rename('NDWI'),
                'ndbi': lambda img: img.normalizedDifference(['B6', 'B5']).rename('NDBI'),
                'evi': lambda img: img.expression(
                    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                    {
                        'NIR': img.select('B5'),
                        'RED': img.select('B4'),
                        'BLUE': img.select('B2')
                    }
                ).rename('EVI'),
                'savi': lambda img: img.expression(
                    '((NIR - RED) * (1 + L)) / (NIR + RED + L)',
                    {
                        'NIR': img.select('B5'),
                        'RED': img.select('B4'),
                        'L': 0.5
                    }
                ).rename('SAVI'),
                'mndwi': lambda img: img.normalizedDifference(['B3', 'B6']).rename('MNDWI'),
                'bsi': lambda img: img.expression(
                    '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))',
                    {
                        'SWIR': img.select('B6'),
                        'RED': img.select('B4'),
                        'NIR': img.select('B5'),
                        'BLUE': img.select('B2')
                    }
                ).rename('BSI')
            }
            
            if index_type not in index_functions:
                raise ValueError(f"Unsupported index type: {index_type}")
                
            index = index_functions[index_type](image)
            return image.addBands(index)
            
        except Exception as e:
            raise Exception(f"Error calculating {index_type}: {str(e)}")
