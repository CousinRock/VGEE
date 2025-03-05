from .base_tool import BaseTool
import ee

class RasterOperatorTool(BaseTool):
    @staticmethod
    def raster_calculator_multi(layer_ids, expression, datasets, datasetsNames):
        """多图层计算"""
        try:
            variables = {}
            layer_mapping = {}
            
            for i, layer_id in enumerate(layer_ids, 1):
                if layer_id not in datasets:
                    raise ValueError(f'Invalid layer ID: {layer_id}')
                layer_name = datasetsNames.get(layer_id, f'Layer_{layer_id}')
                var_name = f'img{i}'  # 使用 img1, img2 等作为变量名
                variables[var_name] = datasets[layer_id]
                layer_mapping[layer_name] = var_name
            
            # 替换表达式中的图层名称
            modified_expr = expression
            for layer_name, var_name in layer_mapping.items():
                modified_expr = modified_expr.replace(f'{layer_name}.', f'{var_name}.')
            
            # 替换逻辑运算符
            modified_expr = modified_expr.replace('&&', 'and').replace('||', 'or')
            
            # 计算结果
            return ee.Image(0).expression(modified_expr, variables)
            
        except Exception as e:
            raise Exception(f"Error in multi-layer calculation: {str(e)}")

    @staticmethod
    def raster_calculator_all_bands(image, expression, selected_bands=None):
        """全波段计算
        Args:
            image: 输入影像
            expression: 计算表达式
            selected_bands: 字典，键为表达式，值为要应用该表达式的波段列表
                          例如: {'x*2': ['B1','B2','B3'], 'x/2': ['B5','B6','B7']}
        """
        try:
            if not selected_bands:
                # 如果没有指定波段组，使用原来的全波段计算逻辑
                band_names = image.bandNames()
                def process_band(band):
                    band = ee.String(band)
                    return ee.Image(0).expression(
                        expression,
                        {'x': image.select([band])}
                    ).rename([band])
                processed_bands = band_names.map(process_band)
                result = ee.ImageCollection.fromImages(processed_bands).mosaic()
                
            else:
                # 对每组波段应用不同的表达式
                result = image.select([])  # 创建一个空的影像作为基础
                
                for expr, bands in selected_bands.items():
                    # 处理当前表达式的所有波段
                    print('Tool_routes.py - raster_calculator_all_bands-expr:', expr)
                    for band in bands:
                        # 对每个波段应用表达式并添加到结果影像中
                        calculated = ee.Image(0).expression(
                            expr,
                            {'x': image.select([band])}
                        ).rename([band])
                        result = result.addBands(calculated)
            
            print('Tool_routes.py - raster_calculator_all_bands-result:', result.bandNames().getInfo())
            return result
            
        except Exception as e:
            raise Exception(f"Error in all-bands calculation: {str(e)}")

    @staticmethod
    def raster_calculator_single(image, expression):
        """单波段计算"""
        try:
            band_refs = {}
            
            # 获取波段名称并构建 band_refs
            band_names = image.bandNames().getInfo()
            for band in band_names:
                band_refs[band] = image.select([band])
            
            # 计算结果
            modified_expr = expression.replace('&&', 'and').replace('||', 'or')
            return ee.Image(0).expression(modified_expr, band_refs)
            
        except Exception as e:
            raise Exception(f"Error in single-band calculation: {str(e)}")
        
    @staticmethod
    def img_mosaic(imageCollection):
        """影像拼接"""
        try:
            # 获取所有图像的边界并合并
            geometry = imageCollection.geometry()
            
            # 执行拼接并设置边界
            mosaic_result = imageCollection.mosaic()
            
            # 裁剪到合并后的边界范围
            mosaic_result = mosaic_result.clip(geometry)
            
            # 确保结果包含投影信息
            projection = imageCollection.first().projection()
            mosaic_result = mosaic_result.setDefaultProjection(projection)
            
            return mosaic_result
            
        except Exception as e:
            raise Exception(f"Error in mosaic: {str(e)}")

    @staticmethod
    def img_clip(image, geometry):
        """影像裁剪"""
        try:
            clip_geometry = ee.Geometry(geometry)
            
            # 裁剪到指定边界
            clipped = image.clip(clip_geometry)
            
            # 确保结果包含投影信息
            projection = image.projection()
            clipped = clipped.setDefaultProjection(projection)
            
            return clipped
            
        except Exception as e:
            raise Exception(f"Error in clip: {str(e)}")

    @staticmethod
    def Otsu(image,scale,maxArray,minDis):
        '''
        最大类间方差法:返回一个阈值

        image:传入的单波段图像
        '''
        def Otsu1(histogram):
            #各组的频数
            counts = ee.Array(ee.Dictionary(histogram).get('histogram')) 
            #各组的值
            means = ee.Array(ee.Dictionary(histogram).get('bucketMeans'))
            #组数
            size = means.length().get([0])
            #总像元数量
            total = counts.reduce(ee.Reducer.sum(),[0]).get([0])
            #所有组的数之和
            sums = means.multiply(counts).reduce(ee.Reducer.sum(),[0]).get([0])
            #整幅影像的均值
            mean = sums.divide(total)
            
            #与组数相同长度的索引
            indices = ee.List.sequence(1, size)
            #穷举法计算类内方差
            def Cal(i):
                aCounts = counts.slice(0,0,i)
                aCount = aCounts.reduce(ee.Reducer.sum(),[0]).get([0])
                aMeans = means.slice(0,0,i)
                
                #类别A均值
                aMean = aMeans.multiply(aCounts).reduce(ee.Reducer.sum(), [0]).get([0]).divide(aCount)
                
                bCount = total.subtract(aCount)
                
                bMean = sums.subtract(aCount.multiply(aMean)).divide(bCount)
                
                #类间方差公式
                return aCount.multiply(aMean.subtract(mean).pow(2)).add(
                    bCount.multiply(bMean.subtract(mean).pow(2)))
            bss = indices.map(Cal)
            
            #排序选出最适阈值
            return means.sort(bss).get([-1])

        histogram = image.reduceRegion(
            reducer = ee.Reducer.histogram(maxArray, minDis),# 自行修改合适的最大组数，最小组距
            geometry = image.geometry(),
            scale = scale,
            bestEffort = True
        )
        
        # print("频数分布", histogram)
        
        return Otsu1(histogram.get(histogram.keys().get(0)))
