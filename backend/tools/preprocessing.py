from .base_tool import BaseTool
import ee

class PreprocessingTool(BaseTool):
    @staticmethod
    def RemoveBitLandsat(image):
        """Landsat 除云除雪函数"""
        dilated_cloud = 1 << 1
        cloud_shadow_bit_mask = 1 << 4
        clouds_bit_mask = 1 << 3
        
        qa = image.select("QA_PIXEL").toInt()
        mask = (
            qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0)
            .And(qa.bitwiseAnd(clouds_bit_mask).eq(0))
            .And(qa.bitwiseAnd(dilated_cloud).eq(0))
        )
        return image.updateMask(mask)

    @staticmethod
    def RemoveBitSentinel(image):
        """Sentinel-2 除云函数"""
        qa = image.select('QA60').toInt()
        
        # Bits 10 and 11 are clouds and cirrus
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11
        
        mask = (
            qa.bitwiseAnd(cloud_bit_mask).eq(0)
            .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
        )
        
        return image.updateMask(mask)

    @staticmethod
    def cloud_removal(image):
        """影像除云处理"""
        try:
            # 使用 ee.Algorithms.If 在服务端判断影像类型
            return ee.Algorithms.If(
                image.bandNames().contains('QA60'),
                PreprocessingTool.RemoveBitSentinel(image),
                PreprocessingTool.RemoveBitLandsat(image)
            )
        except Exception as e:
            raise Exception(f"Error in cloud removal: {str(e)}")

    @staticmethod
    def histogram_equalization(image):
        """直方图均衡化处理"""
        try:
            def equalize_band(band):
                histogram = image.select(band).reduceRegion(
                    reducer=ee.Reducer.histogram(maxBuckets=256),
                    geometry=image.geometry(),
                    scale=30,
                    maxPixels=1e13
                ).get(band)

                histogram = ee.Dictionary(histogram)
                bucket_means = ee.Array(histogram.get('bucketMeans'))
                counts = ee.Array(histogram.get('histogram'))

                valid_counts = counts.gt(0)
                valid_bucket_means = bucket_means.mask(valid_counts)
                valid_counts_masked = counts.mask(valid_counts)

                cdf = valid_counts_masked.accum(0)
                cdf_min = cdf.get([0])
                cdf_max = cdf.get([-1])

                has_enough_values = cdf_max.subtract(cdf_min).gt(0)

                return ee.Algorithms.If(
                    has_enough_values,
                    image.select(band).interpolate(
                        valid_bucket_means.toList(),
                        cdf.subtract(cdf_min)
                            .divide(cdf_max.subtract(cdf_min))
                            .multiply(255)
                            .toList()
                    ),
                    image.select(band)
                )

            bands = image.bandNames()
            equalized_bands = bands.map(lambda band: equalize_band(ee.String(band)))
            equalized_image = ee.ImageCollection.fromImages(equalized_bands).toBands()
            
            return equalized_image.rename(bands)
            
        except Exception as e:
            print(f"Error in histogram equalization: {str(e)}")
            raise Exception(f"Error in histogram equalization: {str(e)}")

    @staticmethod
    def image_filling(image, collection=None):
        """
        填补图像中的缺失值
        :param image: 需要填补的图像
        :param collection: 用于填补的图像集合
        :return: 填补后的图像
        """
        try:
            # 如果没有提供图像集合，直接返回原图像
            if collection is None:
                return image
            # 从集合中排除当前图像
            source_collection = collection.filter(
                ee.Filter.neq('system:index', image.get('system:index'))
            )
            
            # 使用其他图像的镶嵌来填补当前图像的缺失值
            filled_image = image.unmask(source_collection.mosaic())
            
            return filled_image

        except Exception as e:
            print(f"Error in image_filling: {str(e)}")
            raise e

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

