import { ElMessage } from 'element-plus'
import L from 'leaflet'
import { API_ROUTES } from '../../api/routes'

// 样本相关方法
export const handleSample = {
    // 切换样本状态
    toggleSample: async (layer, showSampleDialog, currentSampleLayer) => {
        if (layer.isSample) {
            await handleSample.cancelSample(layer);
        } else {
            currentSampleLayer.value = layer;
            showSampleDialog.value = true;
        }
    },

    // 确认设置样本
    confirmSetSample: async (sampleForm, currentSampleLayer, showSampleDialog) => {
        if (!sampleForm.value.className.trim()) {
            ElMessage.warning('请输入样本类别');
            return;
        }

        try {
            const layer = currentSampleLayer.value;
            const requestBody = {
                layer_id: layer.id,
                class_name: sampleForm.value.className,
                geometry_type: layer.geometryType,
                features: layer.geometryType === 'Point' ? layer.features : [layer.geometry],
                type: layer.type
            };

            const response = await fetch(API_ROUTES.MAP.ADD_SAMPLE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            if (data.success) {
                layer.isSample = true;
                ElMessage.success(`已将${layer.name}设置为${sampleForm.value.className}类样本`);
                showSampleDialog.value = false;
                sampleForm.value.className = '';
            }
        } catch (error) {
            console.error('Error setting sample:', error);
            ElMessage.error('设置样本失败');
        }
    },

    // 取消样本
    cancelSample: async (layer) => {
        try {
            const response = await fetch(API_ROUTES.MAP.REMOVE_SAMPLE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    layer_id: layer.id
                })
            });

            const data = await response.json();
            if (data.success) {
                layer.isSample = false;
                ElMessage.success(`已取消${layer.name}的样本设置`);
            }
        } catch (error) {
            console.error('Error canceling sample:', error);
            ElMessage.error('取消样本失败');
        }
    }
};

// 研究区域相关方法
export const handleStudyArea = {
    toggleStudyArea: async (layer) => {
        try {
            // 切换研究区域状态
            layer.isStudyArea = !layer.isStudyArea;

            // 准备请求参数
            const endpoint = layer.isStudyArea ? 
                API_ROUTES.MAP.FILTER_BY_GEOMETRY : API_ROUTES.MAP.REMOVE_GEOMETRY;

            const requestBody = {
                asset_id: layer.id,
                type: layer.type,
                geometry: layer.geometry
            };

            // 发送请求
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            if (data.success) {
                ElMessage.success(`已${layer.isStudyArea ? '设置' : '取消'}${layer.name}${layer.isStudyArea ? '为' : ''}研究区域${layer.isStudyArea ? '' : '设置'}`);
            }
        } catch (error) {
            console.error('Error toggling study area:', error);
            ElMessage.error('设置研究区域失败');
        }
    }
};

// 图层样式相关方法
export const handleStyle = {
    // 打开矢量图层样式设置
    openVectorStyleSettings: (layer, currentVectorLayer, vectorStyle, showVectorStyleDialog) => {
        currentVectorLayer.value = layer;

        if (layer.geometryType === 'Point') {
            vectorStyle.value = {
                color: layer.visParams.fillColor,
                weight: layer.visParams.radius / 3,
                opacity: layer.visParams.opacity,
                fillOpacity: layer.visParams.fillOpacity
            };
        } else {
            const style = layer.leafletLayer.options.style || {};
            vectorStyle.value = {
                color: style.color || '#3388ff',
                weight: style.weight || 2,
                opacity: style.opacity || 1,
                fillOpacity: style.fillOpacity || 0.2
            };
        }

        showVectorStyleDialog.value = true;
    },

    // 应用矢量图层样式
    applyVectorStyle: (currentVectorLayer, vectorStyle, showVectorStyleDialog, map) => {
        if (!currentVectorLayer.value) return;

        if (currentVectorLayer.value.geometryType === 'Point') {
            currentVectorLayer.value.visParams = {
                radius: vectorStyle.value.weight * 3,
                fillColor: vectorStyle.value.color,
                color: "#ffffff",
                weight: 2,
                opacity: vectorStyle.value.opacity,
                fillOpacity: vectorStyle.value.fillOpacity
            };

            // 更新点图层
            handleStyle.updatePointLayer(currentVectorLayer.value, map);
        } else {
            const style = {
                color: vectorStyle.value.color,
                weight: vectorStyle.value.weight,
                opacity: vectorStyle.value.opacity,
                fillOpacity: vectorStyle.value.fillOpacity
            };
            currentVectorLayer.value.leafletLayer.setStyle(style);
            currentVectorLayer.value.visParams = style;
        }

        showVectorStyleDialog.value = false;
        ElMessage.success('样式已更新');
    },

    // 更新点图层
    updatePointLayer: (layer, map) => {
        map.removeLayer(layer.leafletLayer);
        layer.leafletLayer = L.geoJSON({
            type: 'FeatureCollection',
            features: layer.features.map(point => ({
                type: 'Feature',
                geometry: point,
                properties: {}
            }))
        }, {
            pointToLayer: (feature, latlng) => {
                return L.circleMarker(latlng, layer.visParams);
            }
        }).addTo(map);
    }
}; 

// 添加获取调色板预览样的方法
export const getPalettePreviewStyle = (colors) => {
    return {
        background: `linear-gradient(to right, ${colors.join(',')})`
    }
}

// 取滑块步长和范围
export const getSliderStep = (satelliteType) => {
    if (!satelliteType) return 0.1;

    switch (satelliteType) {
        case 'SENTINEL-2':
            return 100;  // Sentinel-2 反射率数据范围较大，用100作为步长
        case 'MODIS-NDVI':
            return 100;  // MODIS NDVI 数据范围在 -2000 到 10000
        case 'LANDSAT-8':
        case 'LANDSAT-7':
        case 'LANDSAT-5':
            return 0.001;  // Landsat TOA 反射率数据范围在 0-1
        default:
            return 0.001;
    }
}

// 格式化显示
export const formatSliderValue = (value) => {
    return value.toFixed(3);
}

// 添加防抖函数,防止缩放移动时图层卡死
export const debounce = (fn, delay) => {
    let timer = null;
    return function (...args) {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => {
            fn.apply(this, args);
        }, delay);
    };
};

// 图层管理相关方法
export const layerManager = {
    // 添加新图层
    addNewLayer: async (layerName, mapData, layers, map, API_ROUTES) => {
        try {
            if (!mapData?.overlayLayers?.length) {
                ElMessage.warning('未找符合条件的影像数据')
                return
            }

            // 1. 预取波段信息并缓存
            const response = await fetch(`${API_ROUTES.LAYER.GET_LAYER_INFO}?id=${mapData.overlayLayers[0].id}&satellite=${mapData.satellite}`)
            const layerInfo = await response.json()

            // 2. 为每个图层创建新的图层对象
            mapData.overlayLayers.forEach(layerData => {
                const newLayer = {
                    id: layerData.id,
                    name: layerName,
                    icon: 'fas fa-satellite',
                    visible: true,
                    opacity: 1,
                    leafletLayer: null,
                    zIndex: 1000 + layers.value.length,
                    satellite: mapData.satellite || 'LANDSAT',
                    bandInfo: layerInfo.bands,
                    visParams: {
                        bands: mapData.visParams.bands,
                        min: mapData.visParams.min,
                        max: mapData.visParams.max,
                        gamma: mapData.visParams.gamma
                    },
                    min: mapData.overlayLayers[0].min,
                    max: mapData.overlayLayers[0].max
                }

                // 3. 创建 Leaflet 图层
                newLayer.leafletLayer = L.tileLayer(layerData.url, {
                    opacity: newLayer.opacity,
                    maxZoom: 20,
                    maxNativeZoom: 20,
                    tileSize: 256,
                    updateWhenIdle: false,
                    updateWhenZooming: false,
                    keepBuffer: 2,
                    zIndex: newLayer.zIndex
                })

                // 4. 添加到地图和图层数组
                newLayer.leafletLayer.addTo(map.value)
                layers.value.push(newLayer)
            })
        } catch (error) {
            console.error('Error adding layer:', error)
            ElMessage.error('添加图层失败')
        }
    },

    // 移除图层
    removeLayer: async (layerId, layers, map, API_ROUTES) => {
        try {
            const layer = layers.value.find(l => l.id === layerId)
            if (!layer) return

            if (layer.type === 'vector' || layer.type === 'manual') {
                if (layer.isStudyArea) {
                    ElMessage.error('该图层仍在被用作研究区，无法移除')
                    return
                }
                if(layer.isSample) {
                    ElMessage.error('该图层仍在被用作样本点，无法移除')
                    return
                }
                map.value.removeLayer(layer.leafletLayer)
            } else {
                const response = await fetch(API_ROUTES.MAP.REMOVE_LAYER, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ layer_id: layerId })
                })
                const result = await response.json()
                if (!result.success) {
                    throw new Error(result.message)
                }
                map.value.removeLayer(layer.leafletLayer)
            }

            const index = layers.value.findIndex(l => l.id === layerId)
            if (index > -1) {
                layers.value.splice(index, 1)
            }
        } catch (error) {
            console.error('Error removing layer:', error)
            ElMessage.error('移除图层失败')
        }
    },

    // 重命名图层
    renameLayer: async (layer, newName, API_ROUTES) => {
        try {
            if (!newName.trim()) {
                ElMessage.warning('图层名称不能为空')
                return false
            }

            const response = await fetch(API_ROUTES.MAP.RENAME_LAYER, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    layer_id: layer.id,
                    new_name: newName.trim()
                })
            })

            const data = await response.json()
            if (data.success) {
                layer.name = newName.trim()
                ElMessage.success('图层重命名成功')
                return true
            } else {
                throw new Error(data.message)
            }
        } catch (error) {
            console.error('Error renaming layer:', error)
            ElMessage.error(error.message || '重命名失败')
            return false
        }
    }
}
