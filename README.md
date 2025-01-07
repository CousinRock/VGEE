# 遥感影像处理系统

一个基于 Google Earth Engine 平台，使用 Vue 3 和 Flask 的遥感影像处理系统。系统提供了丰富的遥感影像处理和分析功能，支持多源遥感数据的处理和分析。
![image](images/demo1.jpg)

## 主要功能

### 数据源支持
- Landsat 系列 (5/7/8/9)
- Sentinel-2 系列 (MSI)

### DEMO
### 添加图层
![image](images/addLayer.gif)
### 影像处理
![image](images/process.gif)

## 技术栈

### 前端
- Vue 3
- Leaflet

### 后端
- Flask
- Google Earth Engine Python API
- Flask-CORS

## 安装说明

### 前端安装
```bash
cd frontend
npm install
npm run dev
```

### 后端安装
```bash
cd backend
conda activate vgee/vgee(Windows下将bin文件夹添加到环境变量中)
pip install -r requirements.txt
python app.py
```

## Vercel部署（推荐）
- 前端地址：https://vgee-wrjwrjwrjwrjwrjs-projects.vercel.app/
- 下载后端代码，在backend文件夹中进行
- 创建conda环境：conda create --name VGEE python=3.13 -y
- 激活conda环境：conda activate VGEE/VGEE(Windows下将bin文件夹添加到环境变量中)
- 安装依赖：pip install -r requirements.txt
- 创建名为project的文本文件，将GEE项目地址填入，并放到backend/config文件夹中
- 启动服务：python app.py


## Docker 部署（不推荐，目前无法解决服务账号导出影像问题）

## 配置说明

1. 复制配置文件模板：
从Google Cloud 获取服务账号凭证，下载json文件到backend/config目录下

2. 构建并启动服务：
```bash
# 构建镜像
docker-compose build --no-cache
如果构建失败，尝试手动拉取镜像：docker pull python:3.11-slim

# 启动服务
docker-compose up
```
## Docker 安装
Windows下安装Docker Desktop
- 参考：[here](https://blog.csdn.net/qq_60750453/article/details/128636298)
- 镜像使用参考：[here](https://blog.csdn.net/weixin_50160384/article/details/139861337)

## Google服务账号申请[here](https://console.cloud.google.com)
```bash
1、选择IAM和管理,给主账号添加权限：
- Earth Engine Apps Publisher
- Earth Engine Resource Admin
- Earth Engine Resource Viewer
- Earth Engine Resource Writer
- Service Usage Consumer

2、选择服务账号，如果没有就创建服务账号，创建好之后点击右边三个点选择管理密钥，创建密钥，下载json文件到backend/config目录下
```
服务启动后：
- 前端访问地址：http://localhost:8080
- 后端访问地址：http://localhost:5000

## 注意事项

- 需要有效的 Google Earth Engine 服务账号
- 确保服务账号具有足够的权限
- 大范围数据处理可能需要较长时间

## 作者
Renjie Wu
