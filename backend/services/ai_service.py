from samgeo import SamGeo
from samgeo.text_sam import LangSAM
import torch
import numpy as np

def segment_img(url):
    try:
        # 初始化 LangSAM (不使用 device 参数)
        sam = LangSAM()
        
        # 设置分割参数
        text_prompt = "house"  # 可以根据需要修改提示词
        box_threshold = 0.24
        text_threshold = 0.24
        
        # 执行分割
        sam.predict(url, text_prompt, box_threshold=box_threshold, text_threshold=text_threshold)
        masks, boxes, phrases, logits = sam.masks, sam.boxes, sam.phrases, sam.logits
        
        # 处理结果为可序列化的格式
        return {
            'success': True,
            'masks': masks.tolist() if isinstance(masks, (np.ndarray, torch.Tensor)) else masks,
            'boxes': boxes.tolist() if isinstance(boxes, (np.ndarray, torch.Tensor)) else boxes,
            'phrases': phrases,
            'logits': logits.tolist() if isinstance(logits, (np.ndarray, torch.Tensor)) else logits,
            'text_prompt': text_prompt
        }
        
    except Exception as e:
        print(f"Error in segment_img: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


