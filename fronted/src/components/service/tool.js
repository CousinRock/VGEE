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

        // 更新图层引用
        layer.leafletLayer = newLeafletLayer

        if (layer.visible) {
            newLeafletLayer.addTo(mapView.map)
            newLeafletLayer.setZIndex(layer.zIndex)
        }
    } else {
        // 处理新图层
        const [originalId] = layerResult.layer_id.split('_')
        const originalLayer = mapView.layers.find(l => l.id === originalId)

        const newLayer = {
            id: layerResult.layer_id,
            name: `${originalLayer?.name || 'Unknown'} (Processed)`,
            icon: 'fas fa-layer-group',
            visible: true,
            opacity: 1,
            leafletLayer: null,
            bandInfo: layerResult.bandInfo,
            visParams: {
                bands: layerResult.bandInfo,
                min: layerResult.visParams.min,
                max: layerResult.visParams.max
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
export const processLayerSelect = async (selectedLayerName, currentTool, mapView, clusterCounts, isProcessing) => {
    if (selectedLayerName.length === 0) {
        ElMessage.warning('请选择至少一个图层')
        return false
    }

    try {
        isProcessing.value = true
        let endpoint = ''
        let requestData = {}

        switch (currentTool.id) {
            case 'kmeans':
                endpoint = API_ROUTES.TOOLS.KMEANS_CLUSTERING
                requestData = {
                    ...createRequestData(selectedLayerName, mapView.layers),
                    cluster_counts: clusterCounts
                }
                break
            case 'cloud-removal':
                endpoint = API_ROUTES.TOOLS.CLOUD_REMOVAL
                requestData = createRequestData(selectedLayerName, mapView.layers)
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
            default:
                throw new Error('未知的工具类型')
        }

        const result = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })

        const data = await result.json()
        if (data.success) {
            const results = Array.isArray(data.results) ? data.results : [{
                layer_id: selectedLayerName[0],
                tileUrl: data.tileUrl,
                bandInfo: data.bandInfo
            }]

            for (const layerResult of results) {
                const layer = mapView.layers.find(l => l.id === layerResult.layer_id)
                if (layer) {
                    const response = await fetch(`${API_ROUTES.LAYER.GET_LAYER_INFO}?id=${layer.id}&satellite=${layer.satellite}`)
                    const layerInfo = await response.json()
                    if (layerInfo.success) {
                        layer.bandInfo = layerInfo.bands
                    }
                }
                await updateMapLayer(layerResult, mapView)
            }

            ElMessage.success(data.message)
            return true
        } else {
            ElMessage.error(data.message || '处理失败')
            return false
        }
    } catch (error) {
        console.error('Error processing layers:', error)
        ElMessage.error('处理失败')
        return false
    } finally {
        isProcessing.value = false
    }
}
