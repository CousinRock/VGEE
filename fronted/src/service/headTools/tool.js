import { ElMessage } from 'element-plus'
import L from 'leaflet'
import { API_ROUTES } from '../../api/routes'
import { TOOLS_CONFIG } from '../../config/tools-config'

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
    console.log('Tool.js - updateMapLayer - layerResult', layerResult)
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
        layer.tileUrl = layerResult.tileUrl
        layer.satellite = layer.satellite || 'LANDSAT'  // 保持卫星信息

        console.log('Tool.js - updateMapLayer - updated layer:', layer)

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
            name: layerResult.name || `${originalLayer?.name || 'Unknown'} (Processed)`,
            icon: 'fas fa-layer-group',
            visible: true,
            opacity: 1,
            leafletLayer: null,
            zIndex: 1000 + mapView.layers.length,
            type: layerResult.type,
            tileUrl: layerResult.tileUrl
        }

        // 根据图层类型添加不同的属性
        if (layerResult.type === 'vector') {
            // 矢量图层的属性
            newLayer.visParams = layerResult.visParams || {
                color: '#ff0000',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.3
            }
            newLayer.geometryType = layerResult.geometryType

            // 创建 GeoJSON 数据
            const geojsonData = {
                type: "FeatureCollection",
                features: layerResult.coordinates.map(coords => ({
                    type: "Feature",
                    geometry: {
                        type: "Polygon",
                        coordinates: [coords]  // 每个坐标数组代表一个多边形
                    },
                    properties: {}
                }))
            };

            console.log('Tool.js - updateMapLayer - geojsonData:', geojsonData);

            // 创建 GeoJSON 图层
            newLayer.leafletLayer = L.geoJSON(geojsonData, {
                style: newLayer.visParams
            });
        } else {
            // 栅格图层的属性
            newLayer.bandInfo = layerResult.bandInfo
            newLayer.visParams = {
                bands: layerResult.bandInfo?.length > 3
                    ? layerResult.bandInfo.slice(0, 3)
                    : layerResult.bandInfo,
                min: layerResult.visParams?.min,
                max: layerResult.visParams?.max,
                gamma: layerResult.visParams?.gamma || 1.4
            }
            newLayer.satellite = originalLayer?.satellite || 'LANDSAT'

            // 创建栅格图层
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
        }

        if (mapView.map) {
            newLayer.leafletLayer.addTo(mapView.map)
            newLayer.leafletLayer.setZIndex(newLayer.zIndex)
        }

        mapView.layers.push(newLayer)
    }
}

// 统一的工具处理函数
export const processLayerSelect = async (selectedLayers, currentTool, mapView, params, isProcessing) => {
    const toolConfig = TOOLS_CONFIG.getToolById(currentTool.id)
    if (!toolConfig) {
        throw new Error('未知的工具类型')
    }

    try {
        isProcessing.value = true

        // 验证参数
        if (toolConfig.validate) {
            toolConfig.validate(params)
        }

        // 构建请求数据
        const requestData = toolConfig.processParams(selectedLayers, mapView, params)

        // 发送请求
        const response = await fetch(toolConfig.endpoint, {
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

        // 处理结果
        if (toolConfig.processResult) {
            await toolConfig.processResult(data, mapView)
        } else {
            // 默认处理逻辑
            for (const result of data.results) {
                await updateMapLayer(result, mapView)
            }
        }

        ElMessage.success(data.message || '处理完成')
        return true
    } catch (error) {
        console.error('Error processing tool:', error)
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