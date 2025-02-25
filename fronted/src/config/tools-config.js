import { API_ROUTES } from '../api/routes'

// 先定义 TOOL_IDS
export const TOOL_IDS = {
    // 文件菜单
    FILE: 'file',
    UPLOAD: {
        ROOT: 'upload-vector',
        ASSET: 'upload-asset',
        LANDSAT_TIMESERIES: 'upload-landsat-timeseries',
        SENTINEL2_TIMESERIES: 'upload-sentinel2-timeseries'
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
    LOCATION: {
        ROOT: 'location'
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
        CALCULATOR: 'raster-calculator',
        MOSAIC: 'mosaic',
        CLIP: 'clip',
        STATISTICS: 'statistics'
    },
    TERRAIN_OPERATION: {
        ROOT: 'terrain-operation',
        TERRAIN: 'terrain'
    },


    // AI工具菜单
    AI_TOOLS: 'ai-tools',
    SEGMENT: {
        ROOT: 'segment',
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
        label: 'File',
        children: {
            uploadVector: {
                id: TOOL_IDS.UPLOAD.ROOT,
                label: 'Add Data',
                children: {
                    Assets: {
                        id: TOOL_IDS.UPLOAD.ASSET,
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
                    },
                    landsatTimeseries: {
                        id: TOOL_IDS.UPLOAD.LANDSAT_TIMESERIES,
                        label: 'Landsat Timeseries',
                        requireLayers: false,
                        endpoint: API_ROUTES.UPLOAD.ADD_LANDSAT_TIMESERIES,
                        processParams: (params) => ({
                            dataset_type: 'landsat',
                            ...params
                        }),
                        defaultParams: {
                            startDate: '',
                            endDate: ''
                        }
                    },
                    sentinelTimeseries: {
                        id: TOOL_IDS.UPLOAD.SENTINEL2_TIMESERIES,
                        label: 'Sentinel Timeseries',
                        requireLayers: false,
                        endpoint: API_ROUTES.UPLOAD.ADD_SENTINEL_TIMESERIES,
                        processParams: (params) => ({
                            dataset_type: 'sentinel',
                            ...params
                        }),
                        defaultParams: {
                            startDate: '',
                            endDate: ''
                        }
                    }
                }
            },
            searchData: {
                id: TOOL_IDS.SEARCH.ROOT,
                label: 'Search Data',
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
                        label: 'Input ID',
                        icon: 'fas fa-search',
                        requireLayers: false,
                        description: 'Search data by ID',
                        processParams: (id) => ({
                            dataset_id: id
                        }),
                        validate: (id) => {
                            if (!id) {
                                throw new Error('Please input dataset ID')
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
        label: 'Tools',
        children: {
            preprocessing: {
                id: TOOL_IDS.PREPROCESSING.ROOT,
                label: 'Preprocessing Tools',
                children: {
                    cloudRemoval: {
                        id: TOOL_IDS.PREPROCESSING.CLOUD_REMOVAL,
                        label: 'Cloud Removal',
                        icon: 'fas fa-cloud-sun',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CLOUD_REMOVAL,
                        description: 'Remove clouds from images',
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
                        label: 'Image Filling',
                        icon: 'fas fa-fill-drip',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.IMAGE_FILLING,
                        description: 'Fill missing data in images',
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
                        label: 'Image Bands Rename',
                        icon: 'fas fa-palette',
                        component: 'RenameBands',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.RENAME_BANDS,
                        description: 'Rename image bands',
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
                        label: 'Histogram Equalization',
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
                label: 'Index Calculation',
                children: {
                    ndvi: {
                        id: TOOL_IDS.INDICES.NDVI,
                        label: 'NDVI',
                        icon: 'fas fa-leaf',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: 'Normalized Difference Vegetation Index, used to assess vegetation coverage and growth',
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
                        label: 'EVI',
                        icon: 'fas fa-seedling',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: 'Enhanced Vegetation Index, used to assess vegetation coverage and growth',
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
                        label: 'SAVI',
                        icon: 'fas fa-mountain',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: 'Soil Adjusted Vegetation Index, considering the influence of soil background',
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
                        label: 'NDWI',
                        icon: 'fas fa-water',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: 'Normalized Difference Water Index, used to extract water information',
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
                        label: 'MNDWI',
                        icon: 'fas fa-tint',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: 'Improved Normalized Difference Water Index, better distinguish water and buildings',
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
                        label: 'NDBI',
                        icon: 'fas fa-building',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: 'Normalized Difference Built-up Index, used to extract built-up areas',
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
                        label: 'BSI',
                        icon: 'fas fa-globe',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CALCULATE_INDEX,
                        description: 'Bare Soil Index, used to identify bare soil areas',
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
                label: 'Classification Tools',
                children: {
                    kmeans: {
                        id: TOOL_IDS.CLASSIFICATION.KMEANS,
                        label: 'K-means Clustering',
                        icon: 'fas fa-brain',
                        component: 'MacLeaClassify',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.KMEANS_CLUSTERING,
                        description: 'Use K-means algorithm for unsupervised classification',
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
                        label: 'Random Forest',
                        icon: 'fas fa-brain',
                        component: 'MacLeaClassify',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.RANDOM_FOREST,
                        description: 'Use Random Forest algorithm for supervised classification',
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
                        label: 'Support Vector Machine',
                        icon: 'fas fa-brain',
                        component: 'MacLeaClassify',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.SVM,
                        description: 'Use Support Vector Machine algorithm for supervised classification',
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
                label: 'Raster Operation',
                children: {
                    rasterCalculator: {
                        id: TOOL_IDS.RASTER_OPERATION.CALCULATOR,
                        label: 'Raster Calculator',
                        icon: 'fas fa-calculator',
                        component: 'RasterCalculator',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.RASTER_CALCULATOR,
                        description: 'Perform raster algebra operations',
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
                            mode: params.mode,
                            resultMode: params.resultMode,
                            newBandName: params.newBandName
                        }),
                        validate: (params) => {
                            if (!params?.expression) {
                                throw new Error('请输入计算表达式')
                            }
                            return true
                        }
                    },
                    mosaic: {
                        id: TOOL_IDS.RASTER_OPERATION.MOSAIC,
                        label: 'Mosaic',
                        icon: 'fas fa-image',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.MOSAIC,
                        description: 'Mosaic multiple images into a large image',
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
                    clip: {
                        id: TOOL_IDS.RASTER_OPERATION.CLIP,
                        label: 'Clip',
                        icon: 'fas fa-crop-alt',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.CLIP,
                        description: 'Use vector boundaries to clip images',
                        processParams: (selectedLayers, mapView, params) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            geometry: params?.clipLayer?.geometry || params?.clipLayer?.features?.[0]?.geometry || params?.clipLayer
                        })
                    },
                    statistics: {
                        id: TOOL_IDS.RASTER_OPERATION.STATISTICS,
                        label: 'Raster Statistics',
                        icon: 'fas fa-chart-bar',
                        component: 'RasterStatistics',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.STATISTICS,
                        description: 'Statistics the pixel values and area of raster data',
                        keepWindowOpen: true,
                        processParams: (selectedLayers, mapView, params) => ({
                            layer_ids: selectedLayers,
                            vis_params: mapView.layers
                                .filter(l => selectedLayers.includes(l.id))
                                .map(l => ({
                                    id: l.id,
                                    visParams: l.visParams
                                })),
                            params: params
                        }),
                        processResult: (data, mapView, refs) => {
                            if (refs?.rasterStatisticsRef) {
                                refs.rasterStatisticsRef.setResult(data.results)
                            }
                        }
                    }
                }
            },
            terrainOperation: {
                id: TOOL_IDS.TERRAIN_OPERATION.ROOT,
                label: 'Terrain Tools',
                children: {
                    terrain: {
                        id: TOOL_IDS.TERRAIN_OPERATION.TERRAIN,
                        label: 'Terrain',
                        icon: 'fas fa-mountain',
                        requireLayers: true,
                        endpoint: API_ROUTES.TOOLS.TERRAIN,
                        description: 'Calculate terrain',
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
            location: {
                id: TOOL_IDS.LOCATION.ROOT,
                label: 'Location Search',
                children: {
                    localize: {
                        id: TOOL_IDS.LOCATION.LOCALIZE,
                        label: 'Localize',
                        icon: 'fas fa-map-marker-alt',
                        component: 'LocationSearch',
                        requireLayers: false
                    }
                }
            }
        }
    },
    aiTools: {
        id: TOOL_IDS.AI_TOOLS,
        label: 'AI Tools',
        icon: 'fas fa-robot',
        children: {
            Segment: {
                id: TOOL_IDS.SEGMENT.ROOT,
                label: 'SAM',
                children: {
                    textSegment: {

                        id: TOOL_IDS.SEGMENT.TEXT_SEGMENT,
                        label: 'text prompt segment',
                        icon: 'fas fa-brain',
                        requireLayers: true,
                        endpoint: API_ROUTES.AI.TEXT_SEGMENT,
                        description: 'Use SAM model for geographic spatial segmentation',


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
                        id: TOOL_IDS.SEGMENT.POINT_SEGMENT,
                        label: 'point prompt segment',
                        icon: 'fas fa-map-marker-alt',
                        requireLayers: true,
                        endpoint: API_ROUTES.AI.POINT_SEGMENT,
                        description: 'Use point prompt for geographic spatial segmentation',
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
        label: 'Help',
        children: {
            about: {
                id: TOOL_IDS.HELP_ITEMS.ABOUT,
                label: 'About',
                icon: 'fas fa-info-circle'
            },
            docs: {
                id: TOOL_IDS.HELP_ITEMS.DOCS,
                label: 'Docs',
                icon: 'fas fa-book'
            },
            tutorial: {
                id: TOOL_IDS.HELP_ITEMS.TUTORIAL,
                label: 'Tutorial',
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