import { ElMessage } from 'element-plus'
import L from 'leaflet'
import { API_ROUTES } from '../../api/routes'

// 获取可用图层的通用方法
export const getAvailableLayers = async () => {
    try {
        const response = await fetch(API_ROUTES.TOOLS.GET_LAYERS)
        const data = await response.json()

        if (!data.success) {
            ElMessage.error('获取图层失败')
            return null
        }

        if (!data.layers || data.layers.length === 0) {
            ElMessage.warning('没有可用的图层')
            return null
        }

        return data.layers
    } catch (error) {
        console.error('Error getting layers:', error)
        ElMessage.error('获取图层失败')
        return null
    }
}

// 创建通用的请求数据构建函数
export const createRequestData = (selectedIds, layers) => {
    return {
        layer_ids: selectedIds,
        vis_params: layers
            .filter(l => selectedIds.includes(l.id))
            .map(l => ({
                id: l.id,
                visParams: l.visParams
            }))
    }
}

// 更新地图图层
export const updateMapLayer = async (layerResult, mapView) => {
    // 查找现有图层
    const layer = mapView.layers.find(l => l.id === layerResult.layer_id)
    console.log('Tool.js - updateMapLayer - layerResult', layerResult)

    if (layer) {
        // 更新现有图层
        if (layer.leafletLayer && mapView.map._layers) {
            let mapLayers = Object.values(mapView.map._layers)
            mapLayers.forEach((mapLayer) => {
                if (mapLayer instanceof L.TileLayer &&
                    mapLayer._url === layer.leafletLayer._url) {
                    mapLayer.options.zoomAnimation = false
                    mapView.map.removeLayer(mapLayer)
                }
            })
        }

        // 创建新图层
        const newLeafletLayer = L.tileLayer(layerResult.tileUrl, {
            opacity: layer.opacity,
            maxZoom: 20,
            maxNativeZoom: 20,
            tileSize: 256,
            updateWhenIdle: false,
            updateWhenZooming: false,
            keepBuffer: 2,
            zIndex: layer.zIndex
        })

        // 更新图层引用和波段信息
        layer.leafletLayer = newLeafletLayer
        layer.bandInfo = layerResult.bandInfo  // 更新波段信息

        console.log('Tool.js - updateMapLayer - updated layer:', layer)

        if (layer.visible) {
            newLeafletLayer.addTo(mapView.map)
            newLeafletLayer.setZIndex(layer.zIndex)
        }
    } else {
        // 处理新图层
        const [originalId] = layerResult.layer_id.split('_')
        console.log('Tool.js - updateMapLayer - originalId', originalId)
        const originalLayer = mapView.layers.find(l => l.id === originalId)

        const newLayer = {
            id: layerResult.layer_id,
            name: layerResult.name || `${originalLayer?.name || 'Unknown'} (Processed)`,
            icon: 'fas fa-layer-group',
            visible: true,
            opacity: 1,
            leafletLayer: null,
            bandInfo: layerResult.bandInfo,
            visParams: {
                bands: layerResult.bandInfo,
                min: layerResult.visParams.min,
                max: layerResult.visParams.max,
                gamma: layerResult.visParams.gamma || 1.4
            },
            zIndex: 1000 + mapView.layers.length,
            satellite: originalLayer?.satellite || 'LANDSAT',
        }

        newLayer.leafletLayer = L.tileLayer(layerResult.tileUrl, {
            opacity: newLayer.opacity,
            maxZoom: 20,
            maxNativeZoom: 20,
            tileSize: 256,
            updateWhenIdle: false,
            updateWhenZooming: false,
            keepBuffer: 2,
            zIndex: newLayer.zIndex
        })

        if (mapView.map) {
            newLayer.leafletLayer.addTo(mapView.map)
        }

        mapView.layers.push(newLayer)
    }
}

// 处理图层选择
export const processLayerSelect = async (selectedLayerName, currentTool, mapView, params, isProcessing) => {
    if (selectedLayerName.length === 0) {
        ElMessage.warning('请选择至少一个图层')
        return false
    }

    try {
        isProcessing.value = true
        let endpoint = ''
        let requestData = {}

        switch (currentTool.id) {
            case 'cloud-removal':
                endpoint = API_ROUTES.TOOLS.CLOUD_REMOVAL
                requestData = createRequestData(selectedLayerName, mapView.layers)
                break
            case 'kmeans':
                endpoint = API_ROUTES.TOOLS.KMEANS_CLUSTERING
                requestData = {
                    layer_ids: selectedLayerName,
                    cluster_counts: params,
                    vis_params: selectedLayerName.map(id => ({
                        id: id,
                        visParams: mapView.layers.find(l => l.id === id)?.visParams
                    }))
                }
                break
            case 'random-forest':
                endpoint = API_ROUTES.TOOLS.RANDOM_FOREST
                requestData = {
                    layer_ids: selectedLayerName,
                    rf_params: {
                        numberOfTrees: params.numberOfTrees,
                        trainRatio: params.trainRatio
                    },
                    vis_params: selectedLayerName.map(id => ({
                        id: id,
                        visParams: mapView.layers.find(l => l.id === id)?.visParams
                    }))
                }
                break
            case 'image-filling':
                endpoint = API_ROUTES.TOOLS.IMAGE_FILLING
                requestData = createRequestData(selectedLayerName, mapView.layers)
                break
            case 'ndvi':
            case 'ndwi':
            case 'ndbi':
            case 'evi':
            case 'savi':
            case 'mndwi':
            case 'bsi':
                endpoint = API_ROUTES.TOOLS.CALCULATE_INDEX
                requestData = {
                    ...createRequestData(selectedLayerName, mapView.layers),
                    index_type: currentTool.id
                }
                break
            case 'histogram-equalization':
                endpoint = API_ROUTES.TOOLS.HISTOGRAM_EQUALIZATION
                requestData = createRequestData(selectedLayerName, mapView.layers)
                break
            case 'raster-calculator':
                endpoint = API_ROUTES.TOOLS.RASTER_CALCULATOR
                requestData = {
                    layer_ids: selectedLayerName,
                    expression: params,
                    vis_params: selectedLayerName.map(id => ({
                        id: id,
                        visParams: mapView.layers.find(l => l.id === id)?.visParams
                    }))
                }
                break
            default:
                throw new Error('未知的工具类型')
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })

        const data = await response.json()
        
        if (!data.success) {
            throw new Error(data.message || '处理失败')
        }

        // 更新地图图层
        for (const result of data.results) {
            await updateMapLayer(result, mapView)
        }

        ElMessage.success(data.message || '处理完成')
        return true

    } catch (error) {
        console.error('Error processing layers:', error)
        ElMessage.error('处理失败')
        return false
    } finally {
        isProcessing.value = false
    }
}

// 添加矢量数据相关方法
export const handleVectorAsset = async (selectedAsset, mapView) => {
    try {
        const response = await fetch(`${API_ROUTES.TOOLS.ADD_VECTOR_ASSET}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ asset_id: selectedAsset.id })
        })

        const data = await response.json()
        if (!data.success) {
            throw new Error(data.message)
        }

        // 创建新图层对象
        const newLayer = {
            id: selectedAsset.id,
            name: selectedAsset.name,
            type: 'vector',
            visible: true,
            opacity: 1,
            visParams: data.visParams,
            zIndex: 1000 + mapView.layers.length
        }

        // 创建 Leaflet 瓦片图层
        const vectorLayer = L.tileLayer(data.tileUrl, {
            opacity: newLayer.opacity,
            maxZoom: 20,
            maxNativeZoom: 20,
            tileSize: 256,
            updateWhenIdle: false,
            updateWhenZooming: false,
            keepBuffer: 2,
            zIndex: newLayer.zIndex
        })

        // 添加到地图
        newLayer.leafletLayer = vectorLayer
        mapView.layers.push(newLayer)
        vectorLayer.addTo(mapView.map)

        // 使用返回的边界信息进行定位
        if (data.bounds) {
            // 转换坐标格式为 Leaflet 所需的格式
            const bounds = L.latLngBounds([
                [data.bounds[0][1], data.bounds[0][0]], // 西南角
                [data.bounds[2][1], data.bounds[2][0]]  // 东北角
            ])
            
            // 定位到边界范围
            mapView.map.fitBounds(bounds, {
                padding: [50, 50],
                maxZoom: 13
            })
        }

        return true
    } catch (error) {
        console.error('Error adding vector asset:', error)
        ElMessage.error('添加矢量图层失败')
        return false
    }
}

// 添加栅格影像相关方法
export const handleImageAsset = async (selectedAsset, mapView) => {
    try {
        // 获取栅格数据
        const response = await fetch(`${API_ROUTES.TOOLS.ADD_IMAGE_ASSET}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ asset_id: selectedAsset.id })
        })

        const data = await response.json()
        if (!data.success) {
            throw new Error(data.message)
        }

        // 创建新图层对象
        const newLayer = {
            id: selectedAsset.id,
            name: selectedAsset.name,
            type: 'raster',
            visible: true,
            opacity: 1,
            leafletLayer: null,
            zIndex: 1000 + mapView.layers.length,
            visParams: {
                bands: ['B4', 'B3', 'B2'],
                min: 0,
                max: 3000,
                gamma: 1.4
            }
        }

        // 创建 Leaflet 瓦片图层
        const imageLayer = L.tileLayer(data.tileUrl, {
            opacity: newLayer.opacity,
            maxZoom: 20,
            maxNativeZoom: 20,
            tileSize: 256,
            updateWhenIdle: false,
            updateWhenZooming: false,
            keepBuffer: 2,
            zIndex: newLayer.zIndex
        })

        // 添加到地图
        newLayer.leafletLayer = imageLayer
        mapView.layers.push(newLayer)
        imageLayer.addTo(mapView.map)

        return true
    } catch (error) {
        console.error('Error adding image asset:', error)
        ElMessage.error('添加栅格图层失败')
        return false
    }
}

// 添加栅格计算器相关函数
export const calculatorTools = {
    /**
     * 插入波段引用到表达式中
     * @param {string} expression - 当前表达式
     * @param {string} band - 要插入的波段名称（如 'B4', 'B5' 等）
     * @returns {string} 更新后的表达式
     */
    insertBand: (expression, band) => {
        return expression + band
    },

    /**
     * 插入运算符到表达式中，确保运算符前后有空格
     * @param {string} expression - 当前表达式
     * @param {string} operator - 要插入的运算符（如 '+', '-', '*', '/' 等）
     * @returns {string} 更新后的表达式
     */
    insertOperator: (expression, operator) => {
        return expression + ` ${operator} `
    },

    /**
     * 插入数学函数到表达式中
     * @param {string} expression - 当前表达式
     * @param {string} func - 要插入的函数名称
     * @returns {string} 更新后的表达式
     * @description 支持的函数：
     * - sqrt: 平方根
     * - pow: 幂运算
     * - exp: 指数函数
     * - log: 对数函数
     * - abs: 绝对值
     */
    insertFunction: (expression, func) => {
        switch(func) {
            case 'sqrt':
                return expression + 'sqrt('
            case 'pow':
                return expression + 'pow('
            case 'exp':
                return expression + 'exp('
            case 'log':
                return expression + 'log('
            case 'abs':
                return expression + 'abs('
            default:
                return expression
        }
    },

    /**
     * 清除整个表达式
     * @returns {string} 空字符串
     */
    clearExpression: () => {
        return ''
    },

    /**
     * 智能回退操作
     * @param {string} expression - 当前表达式
     * @returns {string} 更新后的表达式
     * @description 
     * - 如果最后输入的是波段引用（如 'B4'），则删除整个波段引用
     * - 否则删除最后一个字符
     */
    backspace: (expression) => {
        expression = expression.trim()
        if (expression.match(/B[0-9]+$/)) {
            // 如果是波段引用，删除整个波段引用
            const lastIndex = expression.lastIndexOf("B")
            if (lastIndex !== -1) {
                return expression.substring(0, lastIndex).trim()
            }
        }
        // 删除最后一个字符
        return expression.slice(0, -1).trim()
    },

    /**
     * 获取指定图层的波段信息
     * @param {Object} mapView - 地图视图对象
     * @param {string} layerId - 图层ID
     * @returns {Array} 波段名称数组
     * @description 从地图视图中获取指定图层的波段信息，如果找不到则返回空数组
     */
    getLayerBands: (mapView, layerId) => {
        const layer = mapView.layers.find(l => l.id === layerId)
        return layer?.bandInfo || []
    }
}
