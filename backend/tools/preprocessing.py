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

