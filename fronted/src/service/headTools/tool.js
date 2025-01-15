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
    console.log('Tool.js - updateMapLayer - layer', layer)

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
            zIndex: layer.zIndex,
            type: layer.type
        })

        // 更新图层引用和信息
        layer.leafletLayer = newLeafletLayer
        layer.bandInfo = layerResult.bandInfo
        layer.visParams = layerResult.visParams || {
            bands: layerResult.bandInfo.slice(0, 3),
            min: 0,
            max: 0.3,
            gamma: 1.4
        }
        layer.satellite = layer.satellite || 'LANDSAT'  // 保持卫星信息

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
            bandInfo: layerResult.bandInfo,  // 保存完整的波段信息
            visParams: {
                // 如果有超过3个波段，默认显示前3个波段
                bands: layerResult.bandInfo.length > 3 
                    ? layerResult.bandInfo.slice(0, 3) 
                    : layerResult.bandInfo,
                min: layerResult.visParams.min,
                max: layerResult.visParams.max,
                gamma: layerResult.visParams.gamma || 1.4
            },
            zIndex: 1000 + mapView.layers.length,
            satellite: originalLayer?.satellite || 'LANDSAT',
            type: layerResult.type
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
        // console.log('Tool.js - processLayerSelect - selectedLayerName', selectedLayerName)
        switch (currentTool.id) {
            case 'cloud-removal':
                endpoint = API_ROUTES.TOOLS.CLOUD_REMOVAL
                requestData = createRequestData(selectedLayerName, mapView.layers)
                break
            case 'kmeans':
                endpoint = API_ROUTES.TOOLS.KMEANS_CLUSTERING
                requestData = {
                    ...createRequestData(selectedLayerName, mapView.layers),
                    cluster_counts: params
                }
                break
            case 'random-forest':
                endpoint = API_ROUTES.TOOLS.RANDOM_FOREST
                requestData = {
                    ...createRequestData(selectedLayerName, mapView.layers),
                    rf_params: params
                }
                break
            case 'svm':
                endpoint = API_ROUTES.TOOLS.SVM
                requestData = {
                    ...createRequestData(selectedLayerName, mapView.layers),
                    svm_params: params
                }
                console.log('Tool.js - processLayerSelect - requestData', requestData)
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
                console.log('Tool.js - processLayerSelect - layer', mapView.layers.find(l => l.id === selectedLayerName[0].id))
                endpoint = API_ROUTES.TOOLS.RASTER_CALCULATOR
                requestData = {
                    ...createRequestData(selectedLayerName, mapView.layers),
                    expression: params
                }
                break
            case 'image-bands-rename':
                endpoint = API_ROUTES.TOOLS.RENAME_BANDS
                requestData = {
                    ...createRequestData(selectedLayerName, mapView.layers),
                    bands: params  // 波段映射对象
                }
                break
            case 'clay':
                endpoint = API_ROUTES.AI.SEGMENT
                requestData = {
                    ...createRequestData(selectedLayerName, mapView.layers),
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
        ElMessage.error(error.message || '处理失败')
        return false
    } finally {
        isProcessing.value = false
    }
}

//获取图层波段
export const getLayerBands = (mapView, layerId) => {
    const layer = mapView.layers.find(l => l.id === layerId)
    return layer?.bandInfo || []
}

// 获取所选图层的共同波段
export const getCommonBands = (layerBands) => {
    console.log('Tools.vue - getCommonBands - layerBands', layerBands);
    
    // 提取所有图层的波段名
    const allBands = Object.values(layerBands).map(bands => new Set(bands));

    // 使用 reduce 方法找出所有集合的交集
    const commonBands = [...allBands.reduce((acc, curr) => {
        return new Set([...acc].filter(band => curr.has(band)));
    })];

    console.log('共同波段:', commonBands);
    return commonBands;
}

