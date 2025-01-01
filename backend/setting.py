import ee
import json
import os
import glob

def init_earth_engine():
    """初始化 Earth Engine"""
    try:
        # 获取 config 目录下的所有 json 文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(current_dir, 'config')
        json_files = glob.glob(os.path.join(config_dir, '*.json'))
        
        if not json_files:
            raise Exception(
                "No JSON files found in config directory. "
                "Please copy service-account-file.example.json to "
                "service-account-file.json and update with your credentials."
            )
            
        # 尝试每个 JSON 文件直到找到有效的服务账号文件
        for json_file in json_files:
            try:
                with open(json_file, 'r') as file:
                    service_account_info = json.load(file)
                    
                # 验证是否是服务账号文件
                if service_account_info.get('type') == 'service_account' and 'client_email' in service_account_info:
                    print(f"Found service account file: {os.path.basename(json_file)}")
                    
                    # 使用服务账户文件初始化 Earth Engine
                    credentials = ee.ServiceAccountCredentials(
                        service_account_info['client_email'],
                        json_file
                    )
                    
                    # 初始化 Earth Engine
                    ee.Initialize(credentials, project=service_account_info.get('project_id'))
                    print("Earth Engine initialized successfully")
                    return
                    
            except Exception as e:
                print(f"Skipping {json_file}: {str(e)}")
                continue
                
        raise Exception("No valid service account file found in config directory")
        
    except Exception as e:
        print(f"Error initializing Earth Engine: {str(e)}")
        raise