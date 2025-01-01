import ee
import json

def init_earth_engine():
    """初始化 Earth Engine"""
    # service_account_file = 'service-account-file.json'
    # with open(service_account_file, 'r') as file:
    #     service_account_info = json.load(file)
    # ee.Authenticate()
    
    # ee.Initialize(project=service_account_info.get('project_id')) 
    
    service_account_file = 'service-account-file.json'
    
    # 读取服务账户信息
    with open(service_account_file, 'r') as file:
        service_account_info = json.load(file)

    # 从服务账户信息中获取client_email
    service_account_email = service_account_info['client_email']
    
    # 使用服务账户文件初始化 Earth Engine
    credentials = ee.ServiceAccountCredentials(service_account_email, service_account_file)
    
    # 初始化 Earth Engine
    ee.Initialize(credentials, project=service_account_info.get('project_id'))