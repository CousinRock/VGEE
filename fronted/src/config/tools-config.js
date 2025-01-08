export const menuItems = [
    {
        id: 'file',
        label: '文件',
        children: [
            {
                id: 'upload-vector',
                label: '上传矢量',
                children: [
                    { id: 'upload-vector-local', label: 'Local' },
                    { id: 'upload-vector-assets', label: 'Assets' }
                ]
            },
            {
                id: 'search-data',
                label: '搜索数据',
                children: [
                    { id: 'search-data-landsat', label: 'Landsat' },
                    { id: 'search-data-sentinel', label: 'Sentinel' },
                    { id: 'search-data-modis', label: 'MODIS' },
                    { id: 'search-data-viirs', label: 'VIIRS' },
                    { id: 'search-data-glofas', label: 'Glofas' },
                ]
            }
        ]
    },
    {
        id: 'tools',
        label: '工具箱',
        children: [
            {
                id: 'preprocessing',
                label: '预处理工具',
                children: [
                    { id: 'cloud-removal', label: '影像除云', icon: 'fas fa-cloud-sun' },
                    { id: 'image-filling', label: '影像填补', icon: 'fas fa-fill-drip' },
                    { id: 'histogram-equalization', label: '直方图均值化', icon: 'fas fa-chart-line' },
                    { 
                        id: 'raster-calculator', 
                        label: '栅格计算器', 
                        icon: 'fas fa-calculator',
                        description: '对影像波段进行数学运算'
                    },
                ]
            },
            {
                id: 'indices',
                label: '指数计算',
                children: [
                    {
                        id: 'ndvi',
                        label: '植被指数(NDVI)',
                        icon: 'fas fa-leaf',
                        description: '归一化植被指数，用于评估植被覆盖和生长状况'
                    },
                    {
                        id: 'evi',
                        label: '增强植被指数(EVI)',
                        icon: 'fas fa-seedling',
                        description: '增强型植被指数'
                    },
                    {
                        id: 'savi',
                        label: '土壤植被指数(SAVI)',
                        icon: 'fas fa-mountain',
                        description: '土壤调节植被指数，考虑了土壤背景的影响'
                    },
                    {
                        id: 'ndwi',
                        label: '水体指数(NDWI)',
                        icon: 'fas fa-water',
                        description: '归一化水体指数，用于提取水体信息'
                    },
                    {
                        id: 'mndwi',
                        label: '改进水体指数(MNDWI)',
                        icon: 'fas fa-tint',
                        description: '改进的归一化水体指数，更好地区分水体和建筑物'
                    },
                    {
                        id: 'ndbi',
                        label: '建筑指数(NDBI)',
                        icon: 'fas fa-building',
                        description: '归一化建筑指数，用于提取建筑区域'
                    },
                    {
                        id: 'bsi',
                        label: '裸土指数(BSI)',
                        icon: 'fas fa-globe',
                        description: '裸土指数，用于识别裸露土壤区域'
                    }
                ]
            },
            {
                id: 'classification',
                label: '分类工具',
                children: [
                    {
                        id: 'kmeans',
                        label: 'K-means聚类',
                        icon: 'fas fa-brain',
                        description: '使用K-means算法对影像进行无监督分类'
                    },
                    { id: 'random-forest', label: '随机森林分类', icon: 'fas fa-brain' }
                ]
            },
        ]
    },
    {
        id: 'help',
        label: '帮助',
        children: [
            { id: 'about', label: '关于', icon: 'fas fa-info-circle' },
            { id: 'docs', label: '文档', icon: 'fas fa-book' },
            { id: 'tutorial', label: '教程', icon: 'fas fa-graduation-cap' }
        ]
    }
] 