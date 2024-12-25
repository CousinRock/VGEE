import ee
from typing import List, Dict, Any, Union

# 存储样本数据的字典
samples_dict = {}

def add_sample_service(
    layer_id: str,
    class_name: str,
    geometry_type: str,
    features: List[Dict[str, Any]],
    layer_type: str
) -> Dict[str, Union[bool, str]]:
    """
    添加样本服务
    
    Args:
        layer_id: 图层ID
        class_name: 样本类别名称
        geometry_type: 几何类型 ('Point' 或 'Polygon')
        features: 几何特征列表
        layer_type: 图层类型
        
    Returns:
        包含操作结果的字典
    """
    try:
        # 创建样本数据结构
        sample_data = {
            'class_name': class_name,
            'geometry_type': geometry_type,
            'features': features,
            'layer_type': layer_type
        }
        
        # 存储样本数据
        samples_dict[layer_id] = sample_data
        
        print(f"Sample_service.py - Added sample for layer {layer_id}: {sample_data}")
        
        return {
            'success': True,
            'message': f'Successfully added sample for class {class_name}'
        }
        
    except Exception as e:
        print(f"Sample_service.py - Error in add_sample_service: {str(e)}")
        raise Exception(f"Failed to add sample: {str(e)}")

def remove_sample_service(layer_id: str) -> Dict[str, Union[bool, str]]:
    """
    移除样本服务
    
    Args:
        layer_id: 图层ID
        
    Returns:
        包含操作结果的字典
    """
    try:
        if layer_id in samples_dict:
            # 移除样本数据
            # pop() 方法会从字典中移除指定键的项并返回其值
            removed_sample = samples_dict.pop(layer_id)
            print(f"Sample_service.py - Removed sample for layer {layer_id}")
            
            return {
                'success': True,
                'message': f'Successfully removed sample for class {removed_sample["class_name"]}'
            }
        else:
            return {
                'success': False,
                'message': f'No sample found for layer {layer_id}'
            }
            
    except Exception as e:
        print(f"Sample_service.py - Error in remove_sample_service: {str(e)}")
        raise Exception(f"Failed to remove sample: {str(e)}")

def get_all_samples() -> Dict[str, Dict[str, Any]]:
    """
    获取所有样本数据
    
    Returns:
        所有样本数据的字典
    """
    return samples_dict 