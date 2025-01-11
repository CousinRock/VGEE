from .base_tool import BaseTool
import ee

class IndexTool(BaseTool):
    # 定义不同卫星的波段映射
    BAND_MAPPINGS = {
        'LANDSAT-9': {
            'BLUE': 'B2',
            'GREEN': 'B3',
            'RED': 'B4',
            'NIR': 'B5',
            'SWIR1': 'B6',
            'SWIR2': 'B7'
        },
        'LANDSAT-8': {
            'BLUE': 'B2',
            'GREEN': 'B3',
            'RED': 'B4',
            'NIR': 'B5',
            'SWIR1': 'B6',
            'SWIR2': 'B7'
        },
        'LANDSAT-5': {
            'BLUE': 'B1',
            'GREEN': 'B2',
            'RED': 'B3',
            'NIR': 'B4',
            'SWIR1': 'B5',
            'SWIR2': 'B7'
        },
        'LANDSAT-7': {
            'BLUE': 'B1',
            'GREEN': 'B2',
            'RED': 'B3',
            'NIR': 'B4',
            'SWIR1': 'B5',
            'SWIR2': 'B7'
        },
        'SENTINEL-2': {
            'BLUE': 'B2',
            'GREEN': 'B3',
            'RED': 'B4',
            'NIR': 'B8',
            'SWIR1': 'B11',
            'SWIR2': 'B12'
        }
    }

    @staticmethod
    def calculate_index(image, index_type, layer_id):
        """计算各种遥感指数"""
        try:
            # 从layer_id获取卫星类型
            satellite = layer_id.split('-')[-2]  # 获取倒数第二部分作为卫星类型
            num = layer_id.split('-')[-1]  # 获取倒数第一部分作为卫星编号
            print('CalculateIndex.py - calculate_index-satellite:', satellite)
            type = satellite+'-'+num
            bands = IndexTool.BAND_MAPPINGS.get(type, IndexTool.BAND_MAPPINGS['LANDSAT-8'])
            print('CalculateIndex.py - calculate_index-bands:', bands)

            
            
            index_functions = {
                'ndvi': lambda img: img.normalizedDifference([bands['NIR'], bands['RED']]).rename('NDVI'),
                'ndwi': lambda img: img.normalizedDifference([bands['GREEN'], bands['NIR']]).rename('NDWI'),
                'ndbi': lambda img: img.normalizedDifference([bands['SWIR1'], bands['NIR']]).rename('NDBI'),
                'evi': lambda img: img.expression(
                    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                    {
                        'NIR': img.select(bands['NIR']),
                        'RED': img.select(bands['RED']),
                        'BLUE': img.select(bands['BLUE'])
                    }
                ).rename('EVI'),
                'savi': lambda img: img.expression(
                    '((NIR - RED) * (1 + L)) / (NIR + RED + L)',
                    {
                        'NIR': img.select(bands['NIR']),
                        'RED': img.select(bands['RED']),
                        'L': 0.5
                    }
                ).rename('SAVI'),
                'mndwi': lambda img: img.normalizedDifference([bands['GREEN'], bands['SWIR1']]).rename('MNDWI'),
                'bsi': lambda img: img.expression(
                    '((SWIR1 + RED) - (NIR + BLUE)) / ((SWIR1 + RED) + (NIR + BLUE))',
                    {
                        'SWIR1': img.select(bands['SWIR1']),
                        'RED': img.select(bands['RED']),
                        'NIR': img.select(bands['NIR']),
                        'BLUE': img.select(bands['BLUE'])
                    }
                ).rename('BSI')
            }
            
            if index_type not in index_functions:
                raise ValueError(f"Unsupported index type: {index_type}")
                
            index = index_functions[index_type](image)
            return image.addBands(index)
            
        except Exception as e:
            raise Exception(f"Error calculating {index_type}: {str(e)}")
