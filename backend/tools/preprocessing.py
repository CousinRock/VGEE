from .base_tool import BaseTool
import ee

class PreprocessingTool(BaseTool):
    @staticmethod
    def RemoveBit(image):
        """除云除雪函数"""
        snow_bit = 1 << 5
        dilated_cloud = 1 << 1
        cloud_shadow_bit_mask = 1 << 4
        clouds_bit_mask = 1 << 3
        
        qa = image.select("QA_PIXEL").toInt()
        mask = (
            qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0)
            .And(qa.bitwiseAnd(clouds_bit_mask).eq(0))
            .And(qa.bitwiseAnd(snow_bit).eq(0))
            .And(qa.bitwiseAnd(dilated_cloud).eq(0))
        )
        return image.updateMask(mask)

    @staticmethod
    def cloud_removal(image):
        """影像除云处理"""
        try:
            return PreprocessingTool.RemoveBit(image)
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
    def image_filling(image):
        """图像填补处理"""
        try:
            # 实现图像填补逻辑
            return image
            
        except Exception as e:
            raise Exception(f"Error in image filling: {str(e)}")
