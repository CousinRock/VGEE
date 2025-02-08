import { API_ROUTES } from '../api/routes'

// 先定义 TOOL_IDS
export const TOOL_IDS = {
    // 文件菜单
    FILE: 'file',
    UPLOAD: {
        ROOT: 'upload-vector',
        VECTOR: 'upload-vector-assets'
    },
    SEARCH: {
        ROOT: 'search-data',
        LANDSAT: 'search-data-landsat',
        SENTINEL: 'search-data-sentinel',
        MODIS: 'search-data-modis',
        VIIRS: 'search-data-viirs',
        DEM: 'search-data-dem',
        ID: 'search-data-id'
    },

    // 工具箱菜单
    TOOLS: 'tools',
    PREPROCESSING: {
        ROOT: 'preprocessing',
        CLOUD_REMOVAL: 'cloud-removal',
        IMAGE_FILLING: 'image-filling',
        IMAGE_BANDS_RENAME: 'image-bands-rename',
        HISTOGRAM_EQUALIZATION: 'histogram-equalization'
    },
    INDICES: {
        ROOT: 'indices',
        NDVI: 'ndvi',
        EVI: 'evi',
        SAVI: 'savi',
        NDWI: 'ndwi',
        MNDWI: 'mndwi',
        NDBI: 'ndbi',
        BSI: 'bsi'
    },
    CLASSIFICATION: {
        ROOT: 'classification',
        KMEANS: 'kmeans',
        RANDOM_FOREST: 'random-forest',
        SVM: 'svm'
    },
    RASTER_OPERATION: {
        ROOT: 'raster-operation',
        CALCULATOR: 'raster-calculator'
    },

    // // AI工具菜单
    AI_TOOLS: 'ai-tools',
    AI: {
        SEGMENT_ROOT: 'segment',
        TEXT_SEGMENT: 'text_prompt',
        POINT_SEGMENT: 'point_prompt'
    },

    // 帮助菜单
    HELP: 'help',
    HELP_ITEMS: {
        ABOUT: 'about',
        DOCS: 'docs',
        TUTORIAL: 'tutorial'
    },
}

// 然后导出配置对象
export const TOOLS_CONFIG = {
    TOOL_IDS,  // 包含工具ID常量

    // 菜单配置
    file: {
        id: TOOL_IDS.FILE,
        label: '文件',
        children: {
            uploadVector: {
                id: TOOL_IDS.UPLOAD.ROOT,
                label: '上传数据',
                children: {
                    uploadVectorAssets: {
                        id: TOOL_IDS.UPLOAD.VECTOR,
                        label: 'Assets',
                        requireLayers: false,
                        endpoint: API_ROUTES.UPLOAD.ADD_VECTOR_ASSET,
                        processParams: (file, params) => {
                            const formData = new FormData()
                            formData.append('file', file)
                            if (params) {
                                Object.entries(params).forEach(([key, value]) => {
                                    formData.append(key, value)
                                })
                            }
                            return formData
                        }
                    }
                }
            },
            searchData: {
                id: TOOL_IDS.SEARCH.ROOT,
                label: '搜索数据',
                children: {
                    landsat: {
                        id: TOOL_IDS.SEARCH.LANDSAT,
                        label: 'Landsat',
                        icon: 'fas fa-satellite',
                        requireLayers: false,
                        description: '搜索Landsat卫星数据',
                        processParams: (params) => ({
                            dataset_type: 'landsat',
                            ...params
                        }),
                        defaultParams: {
                            startDate: '',
                            endDate: '',
                            cloudCover: 20,
                            region: null
                        }
                    },
                    sentinel: {
                        id: TOOL_IDS.SEARCH.SENTINEL,
                        label: 'Sentinel',
                        icon: 'fas fa-satellite',
                        requireLayers: false,
                        description: '搜索Sentinel卫星数据',
                        processParams: (params) => ({
                            dataset_type: 'sentinel',
                            ...params
                        }),
                        defaultParams: {
                            startDate: '',
                            endDate: '',
                            cloudCover: 20,
                            region: null
                        }
                    },
                    modis: {
                        id: TOOL_IDS.SEARCH.MODIS,
                        label: 'MODIS',
                        icon: 'fas fa-satellite',
                        requireLayers: false,
                        description: '搜索MODIS卫星数据',
                        processParams: (params) => ({
                            dataset_type: 'modis',
                            ...params
                        }),
                        defaultParams: {
                            startDate: '',
                            endDate: '',
                            region: null
                        }
                    },
                    viirs: {
                        id: TOOL_IDS.SEARCH.VIIRS,
                        label: 'VIIRS',
                        icon: 'fas fa-satellite',
                        requireLayers: false,
                        description: '搜索VIIRS卫星数据',
                        processParams: (params) => ({
                            dataset_type: 'viirs',
                            ...params
                        }),
                        defaultParams: {
                            startDate: '',
                            endDate: '',
                            region: null
                        }
                    },
                    dem: {
                        id: TOOL_IDS.SEARCH.DEM,
                        label: 'DEM',
                        icon: 'fas fa-mountain',
                        requireLayers: false,
                        description: '搜索DEM高程数据',
                        processParams: (params) => ({
                            dataset_type: 'dem',
                            ...params
                        }),
                        defaultParams: {
                            region: null,
                            resolution: 30
                        }
                    },
                    id: {
                        id: TOOL_IDS.SEARCH.ID,
                        label: '输入id',
                        icon: 'fas fa-search',
                        requireLayers: false,
                        description: '通过ID搜索数据',
                        processParams: (id) => ({
                            dataset_id: id
                        }),
                        validate: (id) => {
                            if (!id) {
                                throw new Error('请输入数据集ID')
                            }
                            return true
                        }
                    }
                }
            }
        }
    },
    tools: {
        id: TOOL_IDS.TOOLS,
        label: '工具箱',
        children: {
            preprocessing: {
                id: TOOL_IDS.PREPROCESSING.ROOT,
                label: '预处理工具',
                children: {
                    cloudRemoval: {
                        id: TOOL_IDS.PREPROCESSING.CLOUD_REMOVAL,
                        label: '影像除云',
                        icon: 'fas fa-cloud-sun',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CLOUD_REMOVAL,
                        description: '去除影像中的云层',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                }))
                        })
                    },
                    imageFilling: {
                        id: TOOL_IDS.PREPROCESSING.IMAGE_FILLING,
                        label: '影像填补',
                        icon: 'fas fa-fill-drip',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.IMAGE_FILLING,
                        description: '填补影像中的缺失数据',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                }))
                        })
                    },
                    imageBandsRename: {
                        id: TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME,
                        label: '影像波段重命名',
                        icon: 'fas fa-palette',
                        component: 'RenameBands',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.RENAME_BANDS,
                        description: '重命名影像波段',
                        processParams: (selectedLayers, mapView, params) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            bands: params
                        })
                    },
                    histogramEqualization: {
                        id: TOOL_IDS.PREPROCESSING.HISTOGRAM_EQUALIZATION,
                        label: '直方图均值化',
                        icon: 'fas fa-chart-line',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.HISTOGRAM_EQUALIZATION,
                        description: '对影像进行直方图均衡化处理',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                }))
                        })
                    }
                }
            },
            indices: {
                id: TOOL_IDS.INDICES.ROOT,
                label: '指数计算',
                children: {
                    ndvi: {
                        id: TOOL_IDS.INDICES.NDVI,
                        label: '植被指数(NDVI)',
                        icon: 'fas fa-leaf',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: '归一化植被指数，用于评估植被覆盖和生长状况',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            index_type: 'ndvi'
                        })
                    },
                    evi: {
                        id: TOOL_IDS.INDICES.EVI,
                        label: '增强植被指数(EVI)',
                        icon: 'fas fa-seedling',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: '增强型植被指数',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            index_type: 'evi'
                        })
                    },
                    savi: {
                        id: TOOL_IDS.INDICES.SAVI,
                        label: '土壤植被指数(SAVI)',
                        icon: 'fas fa-mountain',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: '土壤调节植被指数，考虑了土壤背景的影响',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            index_type: 'savi'
                        })
                    },
                    ndwi: {
                        id: TOOL_IDS.INDICES.NDWI,
                        label: '水体指数(NDWI)',
                        icon: 'fas fa-water',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: '归一化水体指数，用于提取水体信息',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            index_type: 'ndwi'
                        })
                    },
                    mndwi: {
                        id: TOOL_IDS.INDICES.MNDWI,
                        label: '改进水体指数(MNDWI)',
                        icon: 'fas fa-tint',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: '改进的归一化水体指数，更好地区分水体和建筑物',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            index_type: 'mndwi'
                        })
                    },
                    ndbi: {
                        id: TOOL_IDS.INDICES.NDBI,
                        label: '建筑指数(NDBI)',
                        icon: 'fas fa-building',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: '归一化建筑指数，用于提取建筑区域',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            index_type: 'ndbi'
                        })
                    },
                    bsi: {
                        id: TOOL_IDS.INDICES.BSI,
                        label: '裸土指数(BSI)',
                        icon: 'fas fa-globe',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: '裸土指数，用于识别裸露土壤区域',
                        processParams: (selectedLayers, mapView) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            index_type: 'bsi'
                        })
                    }
                }
            },
            classification: {
                id: TOOL_IDS.CLASSIFICATION.ROOT,
                label: '分类工具',
                children: {
                    kmeans: {
                        id: TOOL_IDS.CLASSIFICATION.KMEANS,
                        label: 'K-means聚类',
                        icon: 'fas fa-brain',
                        component: 'MacLeaClassify',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.KMEANS_CLUSTERING,
                        description: '使用K-means算法进行无监督分类',
                        defaultParams: {
                            clusterCount: 5
                        },
                        processParams: (selectedLayers, mapView, params) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            cluster_counts: params
                        })
                    },
                    randomForest: {
                        id: TOOL_IDS.CLASSIFICATION.RANDOM_FOREST,
                        label: '随机森林',
                        icon: 'fas fa-brain',
                        component: 'MacLeaClassify',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.RANDOM_FOREST,
                        description: '使用随机森林算法进行监督分类',
                        defaultParams: {
                            numberOfTrees: 50,
                            trainRatio: 0.7
                        },
                        processParams: (selectedLayers, mapView, params) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            rf_params: params
                        })
                    },
                    svm: {
                        id: TOOL_IDS.CLASSIFICATION.SVM,
                        label: '支持向量机',
                        icon: 'fas fa-brain',
                        component: 'MacLeaClassify',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.SVM,
                        description: '使用支持向量机算法进行监督分类',
                        defaultParams: {
                            kernel: 'RBF',
                            trainRatio: 0.7
                        },
                        processParams: (selectedLayers, mapView, params) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            svm_params: params
                        })
                    }
                }
            },
            rasterOperation: {
                id: TOOL_IDS.RASTER_OPERATION.ROOT,
                label: '栅格运算',
                children: {
                    rasterCalculator: {
                        id: TOOL_IDS.RASTER_OPERATION.CALCULATOR,
                        label: '栅格计算器',
                        icon: 'fas fa-calculator',
                        component: 'RasterCalculator',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.RASTER_CALCULATOR,
                        description: '进行栅格代数运算',
                        defaultParams: {
                            calculatorMode: 'single',
                            calculatorExpression: ''
                        },
                        processParams: (selectedLayers, mapView, params) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            expression: params.expression,
                            mode: params.mode
                        }),
                        validate: (params) => {
                            if (!params?.expression) {
                                throw new Error('请输入计算表达式')
                            }
                            return true
                        }
                    }
                }
            }
        }
    },
    aiTools: {
        id: TOOL_IDS.AI_TOOLS,
        label: 'AI工具',
        icon: 'fas fa-robot',
        children: {
            Segment: {
                id: TOOL_IDS.AI.SEGMENT_ROOT,
                label: 'Segment',
                children: {
                    textSegment: {
                        id: TOOL_IDS.AI.TEXT_SEGMENT,
                        label: 'text prompt segment',
                        icon: 'fas fa-brain',
                        requireLayers: true,
                        endpoint: API_ROUTES.AI.TEXT_SEGMENT,
                        description: '使用SAM模型进行地理空间分割',

                        processParams: (selectedLayers, mapView, params) => {
                            // 获取所有选中图层的显示参数
                            const layerVisParams = selectedLayers.reduce((acc, layerId) => {
                                const layer = mapView.layers.find(l => l.id === layerId)
                                console.log('layer', layer);

                                if (layer) {
                                    acc[layerId] = {
                                        min: layer.visParams.min,
                                        max: layer.visParams.max
                                    }
                                }
                                return acc
                            }, {})

                            return {
                                layer_ids: selectedLayers,
                                visParams: layerVisParams,  // 每个图层的显示参数
                                params: params  // AI工具的参数
                            }
                        }
                    },
                    pointSegment: {
                        id: TOOL_IDS.AI.POINT_SEGMENT,
                        label: 'point prompt segment',
                        icon: 'fas fa-map-marker-alt',
                        requireLayers: true,
                        endpoint: API_ROUTES.AI.POINT_SEGMENT,
                        description: '使用点提示进行地理空间分割',
                        processParams: (selectedLayers, mapView) => {
                            // 获取所有选中图层的显示参数
                            const layerVisParams = selectedLayers.reduce((acc, layerId) => {
                                const layer = mapView.layers.find(l => l.id === layerId)
                                if (layer) {
                                    acc[layerId] = {
                                        min: layer.visParams.min,
                                        max: layer.visParams.max
                                    }
                                }
                                return acc
                            }, {})

                            return {
                                layer_ids: selectedLayers,
                                visParams: layerVisParams,  // 每个图层的显示参数
                            }
                        }
                    }
                }
            },
        }
    },
    help: {
        id: TOOL_IDS.HELP,
        label: '帮助',
        children: {
            about: {
                id: TOOL_IDS.HELP_ITEMS.ABOUT,
                label: '关于',
                icon: 'fas fa-info-circle'
            },
            docs: {
                id: TOOL_IDS.HELP_ITEMS.DOCS,
                label: '文档',
                icon: 'fas fa-book'
            },
            tutorial: {
                id: TOOL_IDS.HELP_ITEMS.TUTORIAL,
                label: '教程',
                icon: 'fas fa-graduation-cap'
            }
        }
    },

    // 辅助方法
    getToolById(id) {
        // console.log('getToolById-id', id)
        const findTool = (obj) => {
            // console.log('findTool-obj', obj)
            if (obj.id === id) return obj
            if (obj.children) {
                for (const child of Object.values(obj.children)) {
                    const found = findTool(child)
                    if (found) return found
                }
            }
            return null
        }

        for (const section of Object.values(this)) {
            console.log('section', section)
            if (typeof section === 'object') {
                const found = findTool(section)
                if (found) return found
            }
        }
        return null
    },

    // 获取菜单项数组
    getMenuItems() {
        const convertToArray = (obj) => {
            if (!obj) return []
            return Object.values(obj).map(item => ({
                ...item,
                children: item.children ? convertToArray(item.children) : undefined
            }))
        }

        return convertToArray({
            file: this.file,
            tools: this.tools,
            aiTools: this.aiTools,
            help: this.help
        })
    }
} 