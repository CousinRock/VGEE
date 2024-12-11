# 遥感影像处理系统

一个基于 Google Earth Engine 平台，使用 Vue 3 和 Flask 的遥感影像处理系统，集成了 Earth Engine API，提供了影像浏览、处理和分析功能。

## 功能特点

### 🌍 数据源支持
- Landsat 8 卫星数据
- 支持多时相影像处理

### 🛠 预处理工具
- 影像除云
  - 基于QA波段的云检测和去除
  - 支持批量处理多景影像
- 影像填补
  - 利用时间序列数据进行缺失数据填补
  - 自动检测波段一致性
- 直方图均衡化
  - 支持多波段处理
  - 自适应直方图均衡

### 📊 指数计算
- 植被指数
  - NDVI (归一化植被指数)
  - EVI (增强型植被指数)
  - SAVI (土壤调节植被指数)
- 水体指数
  - NDWI (归一化水体指数)
  - MNDWI (改进的归一化水体指数)
- 建筑指数
  - NDBI (归一化建筑指数)
- 其他指数
  - BSI (裸土指数)

### 🎯 分类工具
- 无监督分类
  - K-means聚类
  - 支持自定义聚类数量
  - 结果可视化
- 监督分类（开发中）

## 技术栈

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- Element Plus - UI组件库
- Leaflet.js - 交互式地图库
- Font Awesome - 图标库

### 后端
- Flask - Python Web框架
- Earth Engine Python API - GEE接口
- Flask-CORS - 跨域资源共享

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
vgee/conda activate vgee
pip