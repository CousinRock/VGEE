# 遥感影像处理系统

一个基于 Google Earth Engine 平台，使用 Vue 3 和 Flask 的遥感影像处理系统。系统提供了丰富的遥感影像处理和分析功能，支持多源遥感数据的处理和分析。
![image](images/demo1.jpg)

## 主要功能

### 数据源支持
- Landsat 系列 (5/7/8/9)

### 预处理工具
- 影像除云
- 影像填补
- 直方图均值化
- 栅格计算器

### 指数计算
- 植被指数 (NDVI)
- 增强植被指数 (EVI)
- 土壤植被指数 (SAVI)
- 水体指数 (NDWI)
- 改进水体指数 (MNDWI)
- 建筑指数 (NDBI)
- 裸土指数 (BSI)

### 分类工具
- K-means 聚类
- 随机森林分类

### 矢量工具
- 矢量数据导入
- 样本采集
- 研究区绘制
- 矢量样式设置

### 数据管理
- 图层管理
- 波段组合
- 显示参数调整
- 图层导出

###DEMO
![image](images/addLayer.gif)

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

## 配置说明

1. 复制配置文件模板：
从Google Cloud 获取服务账号凭证，下载json文件到backend/config目录下


## Docker 部署

3. 构建并启动服务：
```bash
# 构建镜像
docker-compose build -no-cache

# 启动服务
docker-compose up
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