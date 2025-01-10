from flask import Blueprint, jsonify, request
from services.map_service import save_dataset
import ee

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
        print('Tool_routes.py - add_vector_asset-style_params:', style_params)
        
        # 获取矢量数据
        vector_asset = ee.FeatureCollection(asset_id)
        
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

        save_dataset(asset_id, image_asset, layerName)

        # 获取边界信息
        bounds = image_asset.geometry().bounds().getInfo()
        
        return jsonify({
            'success': True,
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