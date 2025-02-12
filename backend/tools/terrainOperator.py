from .base_tool import BaseTool
import ee

class TerrainOperationTool(BaseTool):
    @staticmethod
    def terrain(dem):
        """地形分析
        Args:
            dem: 输入的数字高程模型
        Returns:
            包含坡度、坡向、阴影等信息的地形分析结果
        """
        try:
            # 计算地形参数
            terrain = ee.Algorithms.Terrain(dem)
            
            # 设置可视化参数
            terrain = terrain.set('vis_params', {
                'bands': ['elevation'],  # 默认显示高程
                'min': 0,
                'max': 3000,  # 根据实际高程范围调整
                'palette': ['006600', '002200', 'fff700', 'ab7634', 'c4d0ff', 'ffffff']
            })
            
            return terrain
            
        except Exception as e:
            raise Exception(f"Error in terrain analysis: {str(e)}")

