![image](images/demo.png)
# 遥感影像处理系统

一个基于 Google Earth Engine 平台，使用 Vue 3 和 Flask 的遥感影像处理系统，集成了 Earth Engine API，提供了影像浏览、处理和分析功能。

## 功能特点

- 多源遥感数据支持
  - Landsat 系列 (5/7/8/9)
  - Sentinel-2
  - MODIS
  - ASTER
  - GOES-16

- 影像处理工具
  - 遥感指数计算 (NDVI, NDWI, EVI等)
  - K-means聚类分析
  - 云检测与去除
  - 影像填补
  - 波段组合调整
  - 直方图拉伸

- 交互式地图操作
  - 图层管理
  - 绘制工具
  - 透明度调节
  - 多种底图切换

## 技术栈

### 前端
- Vue 3
- Element Plus
- Leaflet
- Axios
- Font Awesome

### 后端
- Flask
- Google Earth Engine Python API
- NumPy
- Flask-CORS

## 安装说明

### 前端安装
```bash
cd frontend
npm install
npm run serve
```

### 后端安装
```bash
cd backend
conda activate vgee/vgee
pip install -r requirements.txt
```

### Earth Engine 认证
1. 申请 Google Earth Engine 账号
2. 安装 earthengine-api
3. 运行认证
```bash
earthengine authenticate
```

## 使用说明

1. 启动后端服务
```bash
cd backend
flask run/python app.py
```

2. 启动前端服务
```bash
cd frontend
npm run serve
```

## 主要功能使用

### 数据加载
1. 选择卫星数据源
2. 设置时间范围
3. 调整云量阈值
4. 输入图层名称
5. 点击添加图层

### 影像处理
1. 选择目标图层
2. 选择处理工具
3. 设置处理参数

### 可视化调整
1. 点击图层设置
2. 调整波段组合
3. 设置显示范围
4. 调整对比度和亮度

## 注意事项

- 确保已安装所有依赖
- 需要有效的 Google Earth Engine 账号
- 处理大范围数据时可能需要较长时间

## 贡献指南

欢迎提交 Issue 和 Pull Request

## 联系方式

- 作者：Renjie Wu
