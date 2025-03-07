from flask import Blueprint, jsonify, request
from services.map_service import save_dataset,get_dataset
from routes.map_routes import get_study_areas
import ee
import time
import datetime
from tools.parallel_processor import ParallelProcessor
from services.common import date_sequence

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/get-assets', methods=['GET'])
def get_assets():
    try:
        # 从 GEE 认证中获取用户信息
        credentials = ee.data.getAssetRoots()
        if not credentials:
            raise Exception("未找到 GEE 认证信息")
        print('Tool_routes.py - get_assets-credentials:', credentials)
            
        # 获取所有根文件夹的资产
        formatted_assets = []
        for cred in credentials:
            root_folder = cred['id']
            print('Tool_routes.py - get_assets-root_folder:', root_folder)
            
            try:
                # 列出该根文件夹下的所有资产
                assets = ee.data.listAssets({'parent': root_folder})
                
                # 格式化该文件夹下的资产
                folder_assets = []
                for asset in assets['assets']:
                    asset_info = {
                        'id': asset['id'],
                        'name': asset['id'].split('/')[-1],
                        'type': asset['type'],
                        'path': asset['id'],
                        'title': asset.get('title', ''),
                        'description': asset.get('description', ''),
                        'tags': asset.get('tags', [])
                    }
                    
                    # 如果是文件夹，递归获取子资产
                    if asset['type'] == 'FOLDER':
                        try:
                            sub_assets = ee.data.listAssets({'parent': asset['id']})
                            asset_info['children'] = [{
                                'id': sub['id'],
                                'name': sub['id'].split('/')[-1],
                                'type': sub['type'],
                                'path': sub['id'],
                                'title': sub.get('title', ''),
                                'description': sub.get('description', '')
                            } for sub in sub_assets['assets']]
                        except Exception as sub_error:
                            print(f"Error listing sub-assets for {asset['id']}: {str(sub_error)}")
                            asset_info['children'] = []
                    
                    folder_assets.append(asset_info)
                
                # 创建根文件夹节点
                root_info = {
                    'id': root_folder,
                    'name': root_folder.split('/')[-1],
                    'type': 'FOLDER',
                    'path': root_folder,
                    'children': folder_assets
                }
                
                formatted_assets.append(root_info)
                
            except Exception as folder_error:
                print(f"Error accessing folder {root_folder}: {str(folder_error)}")
                continue
            
        return jsonify({
            'success': True,
            'assets': formatted_assets
        })
        
    except Exception as e:
        print(f"Error in get_assets: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@upload_bp.route('/add-vector-asset', methods=['POST'])
def add_vector_asset():
    try:
        data = request.json
        asset_id = data.get('asset_id')
        style_params = data.get('style_params', {
            'color': '#4a80f5',
            'width': 2,
            'opacity': 1,
            'fillOpacity': 0.5
        })
        layer_name = data.get('layer_name','')
        print('Tool_routes.py - add_vector_asset-data:', data)
        
        layer = get_dataset(asset_id)
        if layer:
            vector_asset = layer
        else:
            # 获取矢量数据
            vector_asset = ee.FeatureCollection(asset_id)
            save_dataset(asset_id,vector_asset,layer_name)
        
        # 准备 Earth Engine 样式参数
        # Earth Engine 只支持 color 和 opacity 的设置
        ee_style_params = {
            'color': style_params['color'].replace('#', ''),
            'opacity': float(style_params['opacity'])
        }
        
        # 使用传入的样式参数获取瓦片 URL
        map_id = vector_asset.getMapId(ee_style_params)
        
        # 获取边界信息
        bounds = vector_asset.geometry().bounds().getInfo()
        
        return jsonify({
            'success': True,
            'tileUrl': map_id['tile_fetcher'].url_format,
            'bounds': bounds['coordinates'][0],
            'visParams': style_params  # 返回原始样式参数
        })
        
    except Exception as e:
        print(f"Error in add_vector_asset: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@upload_bp.route('/add-image-asset', methods=['POST'])
def add_image_asset():
    try:
        data = request.json
        asset_id = data.get('asset_id')
        layerName = data.get('layerName')
        
        
        # 获取影像数据
        image_asset = ee.Image(asset_id)
        
        bandNames = image_asset.bandNames().getInfo()
        print('Tool_routes.py - add_image_asset-bandNames:',bandNames)
        # 获取可视化参数
        vis_params = {
            'bands': bandNames[:3],
            'min': 0,
            'max': 3000,
            'gamma': 1.4
        }
        
        # 获取瓦片URL
        map_id = image_asset.getMapId(vis_params)
        id = f'{asset_id}_{int(time.time())}'
        save_dataset(id, image_asset, layerName)

        # 获取边界信息
        bounds = image_asset.geometry().bounds().getInfo()
        
        return jsonify({
            'success': True,
            'id':id,
            'tileUrl': map_id['tile_fetcher'].url_format,
            'bandInfo': bandNames,
            'visParams': vis_params,
            'type':'Raster',
            'bounds': bounds['coordinates'][0]
        })
        
    except Exception as e:
        print(f"Error in add_image_asset: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@upload_bp.route('/add-landsat-timeseries', methods=['POST'])
def add_landsat_timeseries():
    # Make a dummy image for missing years.
    bands = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']
    bandNames = ee.List(bands)
    fillerValues = ee.List.repeat(0, bandNames.size())
    dummyImg = ee.Image.constant(fillerValues).rename(bandNames).selfMask().int16()
    try:
        data = request.json
        start_date = data.get('startDate')  # 格式: "YYYY-MM-DD"
        end_date = data.get('endDate')    # 格式: "YYYY-MM-DD"
        cloud_cover = data.get('cloudCover', 20)
        frequency = data.get('frequency', 'year')
        interval = data.get('interval', 1)
        apply_fmask = data.get('apply_fmask', False)  # 获取除云参数
        print('Tool_routes.py - add_image_asset-data:', data)

        # 获取年份
        start_year = int(start_date.split('-')[0])
        end_year = int(end_date.split('-')[0])
        
        # 获取月日
        start_month = int(start_date.split('-')[1])
        start_day = int(start_date.split('-')[2])
        end_month = int(end_date.split('-')[1])
        end_day = int(end_date.split('-')[2])
        def days_between(d1, d2):
            d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
            d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
            return abs((d2 - d1).days)

        n_days = days_between(
            f"{start_year}-{start_month:02d}-{start_day:02d}",
            f"{start_year}-{end_month:02d}-{end_day:02d}"
        )
        print('Tool_routes.py - add_landsat_timeseries-n_days:', n_days)

        # 获取研究区域
        roi = get_study_areas()
        if roi == [] :
            roi = ee.Geometry.Polygon(
                [
                    [
                        [-115.471773, 35.892718],
                        [-115.471773, 36.409454],
                        [-114.271283, 36.409454],
                        [-114.271283, 35.892718],
                        [-115.471773, 35.892718],
                    ]
                ],
                None,
                False,
            )
        else:
            roi = ee.Geometry.MultiPolygon([area['coordinates'] for area in roi])

        # 获取 Landsat 影像集合
        l9_collection = ee.ImageCollection('LANDSAT/LC09/C02/T1_TOA')
        l8_collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
        l7_collection = ee.ImageCollection('LANDSAT/LE07/C02/T1_TOA')
        l5_collection = ee.ImageCollection('LANDSAT/LT05/C02/T1_TOA')
        l4_collection = ee.ImageCollection('LANDSAT/LT04/C02/T1_TOA')

        # 过滤条件
        def filter_collection(collection, start_date, end_date):
            return collection.filterBounds(roi) \
                           .filterDate(start_date, end_date) \
                           .filter(ee.Filter.lt('CLOUD_COVER', cloud_cover))

        # 重命名 Landsat 影像的波段名称
        def rename_TM_ETM(image):
            return image.select(
                ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'QA_PIXEL'],
                bands
            )

        def rename_OLI(image):
            return image.select(
                ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'QA_PIXEL'],
                bands
            )

        def fmask(image):
            # see https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2
            # Bit 0 - Fill
            # Bit 1 - Dilated Cloud
            # Bit 2 - Cirrus
            # Bit 3 - Cloud
            # Bit 4 - Cloud Shadow
            # dilated_cloud = 1 << 1
            # cloud_shadow_bit_mask = 1 << 4
            # clouds_bit_mask = 1 << 3
            
            # qa = image.select("QA_PIXEL").toInt()
            # mask = (
            #     qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0)
            #     .And(qa.bitwiseAnd(clouds_bit_mask).eq(0))
            #     .And(qa.bitwiseAnd(dilated_cloud).eq(0))
            # )
            qaMask = image.select("QA_PIXEL").bitwiseAnd(int("11111", 2)).eq(0)
            # Replace the original bands with the scaled ones and apply the masks.
            return image.updateMask(qaMask)
        
        # Define function to prepare OLI images.
        def prepOli(img):
            orig = img
            if apply_fmask:
                img = fmask(img)
            img = rename_OLI(img)
            return ee.Image(img.copyProperties(orig, orig.propertyNames())).resample(
                "bicubic"
            )
        def prepEtm(img):
            orig = img
            if apply_fmask:
                img = fmask(img)
            img = rename_TM_ETM(img)
            return ee.Image(img.copyProperties(orig, orig.propertyNames())).resample(
                "bicubic"
            )
        # 创建年度合成影像
        def getAnnualComp(year):
            # 构建日期
            startDate = ee.Date.fromYMD(
                ee.Number(year), ee.Number(start_month), ee.Number(start_day)
            )
            endDate = startDate.advance(ee.Number(n_days), "day")

            # 过滤每个传感器的数据
            l9_filtered = filter_collection(l9_collection, startDate, endDate).map(prepOli)
            l8_filtered = filter_collection(l8_collection, startDate, endDate).map(prepOli)
            l7_filtered = filter_collection(l7_collection, startDate, endDate).map(prepEtm)
            l5_filtered = filter_collection(l5_collection, startDate, endDate).map(prepEtm)
            l4_filtered = filter_collection(l4_collection, startDate, endDate).map(prepEtm)

            # 合并所有集合
            merged = ee.ImageCollection(l9_filtered) \
                .merge(l8_filtered) \
                .merge(l7_filtered) \
                .merge(l5_filtered) \
                .merge(l4_filtered)

            # 计算中值合成
            composite = merged.median()
            nBands = composite.bandNames().size()
            composite = ee.Image(ee.Algorithms.If(nBands, composite, dummyImg))
            
            # 设置属性
            return composite.set({
                'system:time_start':startDate.millis(),
                'year': year
            })
        # 创建月度合成影像
        def getMonthlyComp(startDate):
            startDate = ee.Date(startDate)
            endDate = startDate.advance(1, "month")

             # 过滤每个传感器的数据
            l9_filtered = filter_collection(l9_collection, startDate, endDate).map(rename_OLI)
            l8_filtered = filter_collection(l8_collection, startDate, endDate).map(rename_OLI)
            l7_filtered = filter_collection(l7_collection, startDate, endDate).map(rename_TM_ETM)
            l5_filtered = filter_collection(l5_collection, startDate, endDate).map(rename_TM_ETM)
            l4_filtered = filter_collection(l4_collection, startDate, endDate).map(rename_TM_ETM)

            # 合并所有集合
            merged = ee.ImageCollection(l9_filtered) \
                .merge(l8_filtered) \
                .merge(l7_filtered) \
                .merge(l5_filtered) \
                .merge(l4_filtered)

            monthImg = merged.median()
            nBands = monthImg.bandNames().size()
            monthImg = ee.Image(ee.Algorithms.If(nBands, monthImg, dummyImg))
            return monthImg.set(
                {
                    "system:time_start": startDate.millis(),
                    "nBands": nBands,
                    "system:date": ee.Date(startDate).format('YYYY-MM-dd'),
                }
            )

        if frequency == "year":
            # 生成年度序列
            years = ee.List.sequence(start_year, end_year, interval)
            composites = years.map(getAnnualComp)
        elif frequency == "month":
            months = date_sequence(
                f"{start_year}-{start_month:02d}-{start_day:02d}",
                f"{end_year}-{end_month:02d}-{end_day:02d}",
                "month",
                'YYYY-MM-dd',
                interval,
            )
            composites = months.map(getMonthlyComp)
        
        # 创建影像集合
        collection = ee.ImageCollection.fromImages(composites)
        
        # 获取集合大小
        collection_size = collection.size().getInfo()
        print('Tool_routes.py - add_landsat_timeseries-collection_size:',collection_size)

        if collection_size == 0:
            raise ValueError("未找到符合条件的影像")

        # 设置可视化参数
        vis_params = {
            'bands': bands[2::-1],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        }

        # 获取边界信息
        bounds = roi.getInfo()
        print('Tool_routes.py - add_landsat_timeseries-bounds:',bounds)

        def process_year(date_str, **kwargs):
            """处理影像的函数"""
            try:
                collection = kwargs.get('collection')
                roi = kwargs.get('roi')
                vis_params = kwargs.get('vis_params')
                
                if frequency == 'year':
                    # 过滤特定年份的影像
                    year = int(date_str)
                    images_collection = collection.filter(ee.Filter.eq('year', year))
                    name = f"Landsat {year}"
                    collection_id = f"landsat_{year}_{int(time.time())}"
                    save_name = f"Landsat_{year}"
                else:  # month
                    # 过滤特定日期的影像
                    images_collection = collection.filter(ee.Filter.eq('system:date', date_str))
                    name = f"Landsat {date_str}"
                    collection_id = f"landsat_{date_str}_{int(time.time())}"
                    save_name = f"Landsat_{date_str}"

                filtered_image = images_collection.median().clip(roi).set('date', date_str)
                
                # 获取地图ID
                map_id = filtered_image.getMapId(vis_params)
                
                # 保存数据集
                save_dataset(collection_id, filtered_image, save_name)
                
                return {
                    'date': date_str,
                    'tileUrl': map_id['tile_fetcher'].url_format,
                    'id': collection_id,
                    'name': name,
                    'bandInfo': bands,
                    'visParams': vis_params,
                    'type': 'Raster'
                }
            except Exception as e:
                print(f"Error processing date {date_str}: {str(e)}")
                return None

        # 使用并行处理器处理影像
        if frequency == "year":
            dates = years.getInfo()  # 年份列表
        else:  # month
            dates = months.getInfo()  # 月份日期列表

        annual_images = ParallelProcessor.process_layers(
            layer_ids=dates,
            process_func=process_year,
            max_workers=4,
            collection=collection,
            roi=roi,
            vis_params=vis_params
        )

        # 过滤掉 None 值
        annual_images = [img for img in annual_images if img is not None]

        if not annual_images:
            raise ValueError("未找到符合条件的影像")

        return jsonify({
            'success': True,
            'message': f'找到 {len(annual_images)} 幅影像',
            'bounds': bounds['coordinates'][0],
            'collectionSize': len(annual_images),
            'images': annual_images,
            'type': 'Raster'
        })

    except Exception as e:
        print(f"Error in add_landsat_timeseries: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@upload_bp.route('/add-sentinel-timeseries', methods=['POST'])
def add_sentinel_timeseries():
     # Make a dummy image for missing years.
    bands = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'QA60']
    bandNames = ee.List(bands)
    fillerValues = ee.List.repeat(0, bandNames.size())
    dummyImg = ee.Image.constant(fillerValues).rename(bandNames).selfMask().int16()
    try:
        data = request.json
        start_date = data.get('startDate')  # 格式: "YYYY-MM-DD"
        end_date = data.get('endDate')    # 格式: "YYYY-MM-DD"
        cloud_cover = data.get('cloudCover', 20)
        frequency = data.get('frequency', 'year')
        interval = data.get('interval', 1)
        apply_fmask = data.get('apply_fmask', False)  # 获取除云参数

        # 获取年份
        start_year = int(start_date.split('-')[0])
        end_year = int(end_date.split('-')[0])
        
        # 获取月日
        start_month = int(start_date.split('-')[1])
        start_day = int(start_date.split('-')[2])
        end_month = int(end_date.split('-')[1])
        end_day = int(end_date.split('-')[2])
        def days_between(d1, d2):
            d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
            d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
            return abs((d2 - d1).days)

        n_days = days_between(
            f"{start_year}-{start_month:02d}-{start_day:02d}",
            f"{start_year}-{end_month:02d}-{end_day:02d}"
        )
        print('Tool_routes.py - add_landsat_timeseries-n_days:', n_days)

        # 获取研究区域
        roi = get_study_areas()
        if roi == [] :
            roi = ee.Geometry.Polygon(
                [
                    [
                        [-115.471773, 35.892718],
                        [-115.471773, 36.409454],
                        [-114.271283, 36.409454],
                        [-114.271283, 35.892718],
                        [-115.471773, 35.892718],
                    ]
                ],
                None,
                False,
            )
        else:
            roi = ee.Geometry.MultiPolygon([area['coordinates'] for area in roi])

        # 获取 Landsat 影像集合
        s2_collection = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')

        # 过滤条件
        def filter_collection(collection, start_date, end_date):
            return collection.filterBounds(roi) \
                           .filterDate(start_date, end_date) \
                           .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))

        # 重命名 sentinel2 影像的波段名称
        def rename(image):
            return image.select(
                ['B2', 'B3', 'B4', 'B8', 'B11', 'B12', 'QA60'],
                bands
            )
        
        def fmask(image):
            qa = image.select('QA60').toInt()
        
            # Bits 10 and 11 are clouds and cirrus
            cloud_bit_mask = 1 << 10
            cirrus_bit_mask = 1 << 11
            
            
            mask = (
                qa.bitwiseAnd(cloud_bit_mask).eq(0)
                .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
            )
            return image.updateMask(mask).divide(10000)

        def prep(image):
            orig = image
            if apply_fmask:
                image = fmask(image)
            image = rename(image)
            return ee.Image(image.copyProperties(orig, orig.propertyNames())).resample(
                "bicubic"
            )
        
        # 创建年度合成影像
        def getAnnualComp(year):
            # 构建日期
            startDate = ee.Date.fromYMD(
                ee.Number(year), ee.Number(start_month), ee.Number(start_day)
            )
            endDate = startDate.advance(ee.Number(n_days), "day")

            # 过滤每个传感器的数据
            merged = filter_collection(s2_collection, startDate, endDate).map(prep)

            # 计算中值合成
            composite = merged.median()
            nBands = composite.bandNames().size()
            composite = ee.Image(ee.Algorithms.If(nBands, composite, dummyImg))
            
            # 设置属性
            return composite.set({
                'system:time_start':startDate.millis(),
                'year': year
            })
        # 创建月度合成影像
        def getMonthlyComp(startDate):
            startDate = ee.Date(startDate)
            endDate = startDate.advance(1, "month")

             # 过滤每个传感器的数据
            merged = filter_collection(s2_collection, startDate, endDate).map(rename)

            monthImg = merged.median()
            nBands = monthImg.bandNames().size()
            monthImg = ee.Image(ee.Algorithms.If(nBands, monthImg, dummyImg))
            return monthImg.set(
                {
                    "system:time_start": startDate.millis(),
                    "nBands": nBands,
                    "system:date": ee.Date(startDate).format('YYYY-MM-dd'),
                }
            )

        if frequency == "year":
            # 生成年度序列
            years = ee.List.sequence(start_year, end_year, interval)
            composites = years.map(getAnnualComp)
        elif frequency == "month":
            months = date_sequence(
                f"{start_year}-{start_month:02d}-{start_day:02d}",
                f"{end_year}-{end_month:02d}-{end_day:02d}",
                "month",
                'YYYY-MM-dd',
                interval,
            )
            composites = months.map(getMonthlyComp)
        
        # 创建影像集合
        collection = ee.ImageCollection.fromImages(composites)
        
        # 获取集合大小
        collection_size = collection.size().getInfo()
        print('Tool_routes.py - add_landsat_timeseries-collection_size:',collection_size)

        if collection_size == 0:
            raise ValueError("未找到符合条件的影像")

        # 设置可视化参数
        vis_params = {
            'bands': bands[2::-1],
            'min': 0,
            'max': 1,
            'gamma': 1.4
        }

        # 获取边界信息
        bounds = roi.getInfo()
        print('Tool_routes.py - add_landsat_timeseries-bounds:',bounds)

        def process_year(date_str, **kwargs):
            """处理影像的函数"""
            try:
                collection = kwargs.get('collection')
                roi = kwargs.get('roi')
                vis_params = kwargs.get('vis_params')
                
                if frequency == 'year':
                    # 过滤特定年份的影像
                    year = int(date_str)
                    images_collection = collection.filter(ee.Filter.eq('year', year))
                    name = f"Sentinel2 {year}"
                    collection_id = f"sentinel2_{year}_{int(time.time())}"
                    save_name = f"Sentinel2_{year}"
                else:  # month
                    # 过滤特定日期的影像
                    images_collection = collection.filter(ee.Filter.eq('system:date', date_str))
                    name = f"Sentinel2 {date_str}"
                    collection_id = f"sentinel2_{date_str}_{int(time.time())}"
                    save_name = f"Sentinel2_{date_str}"

                filtered_image = images_collection.median().clip(roi).set('date', date_str)
                
                # 获取地图ID
                map_id = filtered_image.getMapId(vis_params)
                
                # 保存数据集
                save_dataset(collection_id, filtered_image, save_name)
                
                return {
                    'date': date_str,
                    'tileUrl': map_id['tile_fetcher'].url_format,
                    'id': collection_id,
                    'name': name,
                    'bandInfo': bands,
                    'visParams': vis_params,
                    'type': 'Raster'
                }
            except Exception as e:
                print(f"Error processing date {date_str}: {str(e)}")
                return None

        # 使用并行处理器处理影像
        if frequency == "year":
            dates = years.getInfo()  # 年份列表
        else:  # month
            dates = months.getInfo()  # 月份日期列表

        annual_images = ParallelProcessor.process_layers(
            layer_ids=dates,
            process_func=process_year,
            max_workers=4,
            collection=collection,
            roi=roi,
            vis_params=vis_params
        )

        # 过滤掉 None 值
        annual_images = [img for img in annual_images if img is not None]

        if not annual_images:
            raise ValueError("未找到符合条件的影像")

        return jsonify({
            'success': True,
            'message': f'找到 {len(annual_images)} 幅影像',
            'bounds': bounds['coordinates'][0],
            'collectionSize': len(annual_images),
            'images': annual_images,
            'type': 'Raster'
        })

    except Exception as e:
        print(f"Error in add_landsat_timeseries: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@upload_bp.route('/delete-asset', methods=['POST'])
def delete_asset():
    try:
        data = request.json
        asset_id = data.get('asset_id')
        print('upload_routes.py - delete_asset-data:', data)
        
        if not asset_id:
            raise ValueError("未提供资产ID")

        def delete_asset_recursive(asset_path):
            try:
                # 获取资产信息
                asset_info = ee.data.getAsset(asset_path)
                asset_type = asset_info['type']
                print(f"Deleting asset: {asset_path}, type: {asset_type}")

                # 如果是文件夹，递归删除子资产
                if asset_type == 'FOLDER':
                    children = ee.data.listAssets({'parent': asset_path})
                    if 'assets' in children and children['assets']:
                        for child in children['assets']:
                            delete_asset_recursive(child['id'])
                
                # 删除当前资产
                ee.data.deleteAsset(asset_path)
                print(f"Successfully deleted: {asset_path}")
                
            except Exception as e:
                print(f"Error deleting {asset_path}: {str(e)}")
                raise e

        # 递归删除资产及其子资产
        delete_asset_recursive(asset_id)
        
        return jsonify({
            'success': True,
            'message': '资产已成功删除'
        })
        
    except Exception as e:
        print(f"Error in delete_asset: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

