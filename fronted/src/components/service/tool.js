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

        // 更新图层引用
        layer.leafletLayer = newLeafletLayer

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

// 添加矢量数据相关方法
export const handleVectorAsset = async (selectedAsset, mapView) => {
    try {
        // 获取矢量数据
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
            visParams: {
                color: '#3388ff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.2
            },
            zIndex: 1000 + mapView.layers.length
        }

        // 创建 Leaflet 图层
        const vectorLayer = L.geoJSON(data.features, {
            style: newLayer.visParams
        })

        // 添加到地图
        newLayer.leafletLayer = vectorLayer
        mapView.layers.push(newLayer)
        vectorLayer.addTo(mapView.map)

        // 定位到矢量图层的范围
        const bounds = vectorLayer.getBounds()
        if (bounds.isValid()) {
            // 添加一些padding，使图层不会紧贴边缘
            mapView.map.fitBounds(bounds, {
                padding: [50, 50],
                maxZoom: 13  // 限制最大缩放级别，避免缩放过近
            })
        }

        return true
    } catch (error) {
        console.error('Error adding vector asset:', error)
        ElMessage.error('添加矢量图层失败')
        return false
    }
}

// 添加研究区域相关方法
export const toggleStudyArea = async (layer) => {
    try {
        if (layer.isStudyArea) {
            // 取消研究区域
            await fetch(API_ROUTES.MAP.REMOVE_GEOMETRY, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    asset_id: layer.id
                })
            })
            layer.isStudyArea = false
            ElMessage.success('已取消研究区域设置')
        } else {
            // 设置为研究区域
            await fetch(API_ROUTES.MAP.FILTER_BY_GEOMETRY, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    asset_id: layer.id,
                    type: 'vector'
                })
            })
            layer.isStudyArea = true
            ElMessage.success('已设置为研究区域')
        }
        return true
    } catch (error) {
        console.error('Error toggling study area:', error)
        ElMessage.error('设置研究区域失败')
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
