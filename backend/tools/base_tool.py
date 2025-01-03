import ee

class BaseTool:
    """工具基类，提供通用方法"""
    
    @staticmethod
    def validate_inputs(layer_ids, datasets):
        """验证输入的图层ID"""
        if not layer_ids or not all(layer_id in datasets for layer_id in layer_ids):
            raise ValueError('Invalid layer ID')
            
    @staticmethod
    def get_image_collection(layer_ids, datasets):
        """获取图像集合"""
        return ee.ImageCollection([datasets[layer_id] for layer_id in layer_ids]) 
    
class ConfigTool:
    """配置工具类，提供配置相关方法"""
    
    @staticmethod
    def get_satellite_config(satellite):
        """获取卫星配置"""
        return SATELLITE_CONFIGS.get(satellite)
        
