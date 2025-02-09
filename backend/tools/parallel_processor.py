from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class ParallelProcessor:
    @staticmethod
    def process_layers(layer_ids, process_func, max_workers=4, **kwargs):
        """
        通用的并行处理函数
        
        Args:
            layer_ids: 要处理的图层ID列表
            process_func: 处理单个图层的函数
            max_workers: 最大线程数
            **kwargs: 传递给 process_func 的其他参数
            
        Returns:
            list: 处理结果列表
        """
        results = []
        with ThreadPoolExecutor(max_workers=min(len(layer_ids), max_workers)) as executor:
            future_to_layer = {
                executor.submit(process_func, layer_id, **kwargs): layer_id 
                for layer_id in layer_ids
            }
            
            for future in as_completed(future_to_layer):
                result = future.result()
                if result is not None:
                    results.append(result)
                    
        return results 