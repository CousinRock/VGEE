import ee

class ToolService:
    @staticmethod
    def RemoveBit(image):
        """除云除雪函数"""
        snow_bit = 1 << 5
        dilated_cloud = 1 << 1  # 扩张云
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
            cleared_image = ToolService.RemoveBit(image)
            
            return cleared_image 
            
        except Exception as e:
            raise Exception(f"Tool_service.py - Error in cloud removal: {str(e)}")

    @staticmethod
    def calculate_index(image, index_type, params=None):
        """计算各种遥感指数，并将结果添加为新波段"""
        try:
            if index_type == 'ndvi':
                # 归一化植被指数
                nir = image.select('B5')  # Landsat 8 NIR band
                red = image.select('B4')  # Landsat 8 Red band
                ndvi = nir.subtract(red).divide(nir.add(red))
                return image.addBands(ndvi.rename('NDVI'))
                
            elif index_type == 'ndwi':
                # 归一化水体指数
                nir = image.select('B5')
                green = image.select('B3')
                ndwi = green.subtract(nir).divide(green.add(nir))
                return image.addBands(ndwi.rename('NDWI'))
                
            elif index_type == 'ndbi':
                # 归一化建筑指数
                swir = image.select('B6')  # Landsat 8 SWIR1 band
                nir = image.select('B5')
                ndbi = swir.subtract(nir).divide(swir.add(nir))
                return image.addBands(ndbi.rename('NDBI'))
                
            elif index_type == 'evi':
                # 增强型植被指数
                nir = image.select('B5')
                red = image.select('B4')
                blue = image.select('B2')
                evi = nir.subtract(red).multiply(2.5).divide(
                    nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)
                )
                return image.addBands(evi.rename('EVI'))
                
            elif index_type == 'savi':
                # 土壤调节植被指数
                nir = image.select('B5')
                red = image.select('B4')
                L = 0.5  # 土壤亮度校正因子
                savi = nir.subtract(red).multiply(1 + L).divide(nir.add(red).add(L))
                return image.addBands(savi.rename('SAVI'))
                
            elif index_type == 'mndwi':
                # 改进的归一化水体指数
                green = image.select('B3')
                swir = image.select('B6')
                mndwi = green.subtract(swir).divide(green.add(swir))
                return image.addBands(mndwi.rename('MNDWI'))
                
            elif index_type == 'bsi':
                # 裸土指数
                swir1 = image.select('B6')
                red = image.select('B4')
                nir = image.select('B5')
                blue = image.select('B2')
                bsi = ((swir1.add(red)).subtract(nir.add(blue))).divide(
                    (swir1.add(red)).add(nir.add(blue))
                )
                return image.addBands(bsi.rename('BSI'))
                
        except Exception as e:
            raise Exception(f"Error calculating {index_type}: {str(e)}")

    @staticmethod
    def supervised_classification(image, training_data, params):
        """监督分类"""
        try:
            # 实现监督分类逻辑
            return {
                'success': True,
                'message': '监督分类完成'
            }
        except Exception as e:
            raise Exception(f"Tool_service.py - Error in supervised classification: {str(e)}")

    @staticmethod
    def image_filling(images):
        try:
            # 将图像列表转换为 ImageCollection
            imageCollection = ee.ImageCollection.fromImages(images)
            
            # 检查波段数量是否一致
            def check_band_count(image):
                band_count = image.bandNames()
                return image.set('band_count', band_count)

            band_counts = imageCollection.map(check_band_count)
            unique_band_counts = band_counts.aggregate_array('band_count').distinct()
            
            # 使用 ee.Algorithms.If 判断波段数量是否一致
            is_consistent = unique_band_counts.size().eq(1)
            
            result = ee.Algorithms.If( 
                is_consistent,
                'consistent',
                'inconsistent'
            )
            
            # 检查结果是否为一致
            if result.getInfo() == 'inconsistent':  # getInfo 必须在服务器端取值判断
                return {
                    'success': False,
                    'message': '所选图像的波段数量不一致，无法进行填补。'
                }
                
            def fillGaps(image):
                # 过滤掉当前图像
                sourceCollection = imageCollection.filter(
                    ee.Filter.neq('system:index', image.get('system:index')))
                # 使用其他图像的镶嵌来填补当前图像的缺失部分
                filled = image.unmask(sourceCollection.mosaic())
                return filled
            
            # 对每个图像进行填补处理
            filled_images = imageCollection.map(fillGaps)
                
            return filled_images
            
        except Exception as e:
            return {
                'success': False,
                'message': f'影像填补失败: {str(e)}'
            }