import { API_ROUTES } from '../../api/routes'
import { ElMessage } from 'element-plus'
import { TOOLS_CONFIG } from '../../config/tools-config'

// 修改 loadAssets 方法
export const onLoadAssets = async (folder = null, isLoadingAssets, assetsList) => {
    try {
        isLoadingAssets.value = true
        const url = new URL(API_ROUTES.UPLOAD.GET_ASSETS)
        if (folder) {
            url.searchParams.append('folder', folder)
        }

        const response = await fetch(url)
        const data = await response.json()

        if (!data.success) {
            ElMessage.error(data.message || '获取资产列表失败')
            return
        }

        assetsList.value = data.assets
        console.log('upload.js - onLoadAssets - assets:', data.assets)
    } catch (error) {
        console.error('upload.js - Error loading assets:', error)
        ElMessage.error('获取资产列表失败')
    } finally {
        isLoadingAssets.value = false
    }
}

// 修改资产选择处理方法
export const onHandleAssetSelect = async (data, selectedAsset) => {
    try {
        // 如果是文件夹，不进行选择
        if (data.type === 'FOLDER') {
            return
        }

        // 只更新选中状态，不关闭对话框
        selectedAsset.value = data
        console.log('upload.js - onHandleAssetSelect - selected asset:', data)
    } catch (error) {
        console.error('upload.js - Error selecting asset:', error)
        ElMessage.error('选择资产失败')
    }
}

// 修改确认选择方法
export const onConfirmAssetSelect = async (selectedAsset, showAssetsDialog, isLoadingAssets, mapView) => {
    try {
        if (!selectedAsset.value) {
            ElMessage.warning('请选择一个资产')
            return
        }

        // 设置加载状态
        isLoadingAssets.value = true

        console.log('upload.js - onConfirmAssetSelect - selectedAsset:', selectedAsset.value)
        // 根据资产类型处理
        if (selectedAsset.value.type === 'TABLE') {
            // 处理矢量数据
            const loadingMessage = ElMessage({
                message: '正在添加矢量图层...',
                type: 'info',
                duration: 0
            })
            const success = await handleVectorAsset(selectedAsset.value, mapView)
            loadingMessage.close()  // 只关闭加载消息
            if (success) {
                ElMessage.success(`已添加矢量图层: ${selectedAsset.value.name}`)
            }
        } else if (selectedAsset.value.type === 'IMAGE') {
            // 处理栅格影像
            const loadingMessage = ElMessage({
                message: '正在添加栅格图层...',
                type: 'info',
                duration: 0
            })
            const success = await handleImageAsset(selectedAsset.value, mapView)
            loadingMessage.close()  // 只关闭加载消息
            if (success) {
                ElMessage.success(`已添加栅格图层: ${selectedAsset.value.name}`)
            }
        }

        showAssetsDialog.value = false
    } catch (error) {
        console.error('upload.js - Error confirming asset selection:', error)
        ElMessage.error('添加图层失败')
    } finally {
        // 清除加载状态
        isLoadingAssets.value = false
    }
}


// 添加矢量数据相关方法
const handleVectorAsset = async (selectedAsset, mapView) => {
    try {
        const response = await fetch(`${API_ROUTES.UPLOAD.ADD_VECTOR_ASSET}`, {
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
        console.log('upload.js - handleVectorAsset - data:', data);
        
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
            const bounds = L.latLngBounds([
                [data.bounds[0][1], data.bounds[0][0]], // 西南角
                [data.bounds[2][1], data.bounds[2][0]]  // 东北角
            ])
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
const handleImageAsset = async (selectedAsset, mapView) => {
    try {
        // 获取栅格数据
        const response = await fetch(`${API_ROUTES.UPLOAD.ADD_IMAGE_ASSET}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                asset_id: selectedAsset.id,
                layerName: selectedAsset.name
            })
        })

        const data = await response.json()
        console.log('upload.js - handleImageAsset - data:', data);
        
        if (!data.success) {
            throw new Error(data.message)
        }

        // 创建新图层对象
        const newLayer = {
            id: data.id,
            name: selectedAsset.name,
            type: data.type,
            visible: true,
            opacity: 1,
            leafletLayer: null,
            zIndex: 1000 + mapView.layers.length,
            visParams: data.visParams,
            bandInfo: data.bandInfo
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
        console.log('upload.js - handleImageAsset - newLayer:', newLayer);
        
        mapView.layers.push(newLayer)
        imageLayer.addTo(mapView.map)

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
        console.error('Error adding image asset:', error)
        ElMessage.error('添加栅格图层失败')
        return false
    }
}

// 修改为通用的时间序列提交方法
export const onSubmitTimeseries = async (form, mapView, showTimeseriesDialog, isSubmitting, toolId) => {
    if (!form.value.startDate || !form.value.endDate) {
        ElMessage.warning('请选择时间范围')
        return
    }

    try {
        isSubmitting.value = true
        
        // 从工具配置中获取对应的工具配置
        const toolConfig = TOOLS_CONFIG.getToolById(toolId)
        if (!toolConfig || !toolConfig.endpoint) {
            throw new Error('Invalid tool configuration')
        }

        // 使用工具配置中的 processParams 处理参数
        const params = toolConfig.processParams({
            startDate: form.value.startDate,
            endDate: form.value.endDate,
            cloudCover: form.value.cloudCover,
            frequency: form.value.frequency,
            interval: form.value.interval || 1
        })
        
        const response = await fetch(toolConfig.endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        })
        
        const data = await response.json()
        console.log(`upload.js - onSubmitTimeseries - ${toolConfig.label} data:`, data)
        
        if (data.success) {
            ElMessage.success(data.message)
            showTimeseriesDialog.value = false

            // 添加影像到地图
            if (data.images && Array.isArray(data.images)) {
                data.images.forEach(imageData => {
                    // 创建新图层对象
                    const newLayer = {
                        id: imageData.id,
                        name: imageData.name,
                        type: imageData.type,
                        bandInfo: imageData.bandInfo,
                        date: imageData.date,
                        visible: true,
                        opacity: 1,
                        leafletLayer: null,
                        zIndex: 1000 + mapView.layers.length,
                        visParams: imageData.visParams
                    }

                    // 创建 Leaflet 瓦片图层
                    const imageLayer = L.tileLayer(imageData.tileUrl, {
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
                })

                // 使用返回的边界信息进行定位
                console.log('upload.js - onSubmitLandsatTimeseries - data.bounds:', data.bounds);
                if (data.bounds && data.bounds[0]) {
                    const coordinates = data.bounds[0];  // 获取第一个多边形的坐标
                    const bounds = L.latLngBounds([
                        [coordinates[0][1], coordinates[0][0]], // 西南角
                        [coordinates[2][1], coordinates[2][0]]  // 东北角
                    ]);
                    mapView.map.fitBounds(bounds, {
                        padding: [50, 50],
                        maxZoom: 13
                    });
                }
            }
            return true
        } else {
            ElMessage.error(data.message)
            return false
        }
    } catch (error) {
        console.error(`Error submitting ${toolConfig?.label || ''} timeseries:`, error)
        ElMessage.error('添加时间序列失败')
        return false
    } finally {
        isSubmitting.value = false
    }
}