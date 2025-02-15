import { ElMessage } from 'element-plus'
import L from 'leaflet'
import { API_ROUTES } from '../api/routes'
import { layerChangeRemove, normalizeRange } from '../util/methods'

// 定义图标常量
export const MENU_ICONS = {
    EDIT: 'fas fa-edit',           // 编辑/重命名
    SETTINGS: 'fas fa-cog',        // 设置
    INFO: 'fas fa-info-circle',    // 信息
    DELETE: 'fas fa-trash',        // 删除
    STYLE: 'fas fa-palette',       // 样式
    SAMPLE: 'fas fa-tag',          // 样本
    STUDY_AREA: 'fas fa-draw-polygon', // 研究区
    STUDY_AREA_ACTIVE: 'fas fa-check',  // 已设为研究区域
    VISIBILITY: 'fas fa-eye',      // 可见性
    DOWNLOAD: 'fas fa-download',   // 下载
    UPLOAD: 'fas fa-upload',       // 上传
    LAYERS: 'fas fa-layer-group',  // 图层
    ZOOM: 'fas fa-search',         // 缩放
    CHECK: 'fas fa-check',         // 选中
    CLOSE: 'fas fa-times',         // 关闭
    SPINNER: 'fas fa-spinner fa-spin', // 加载中
    SAVE: 'fas fa-save',           // 保存
    REFRESH: 'fas fa-sync',        // 刷新
    FILTER: 'fas fa-filter',       // 过滤
    CHART: 'fas fa-chart-bar',     // 图表
    LOCATION: 'fas fa-map-marker-alt', // 位置
    SATELLITE: 'fas fa-satellite',   // 卫星
    SAMPLE_ACTIVE: 'fas fa-check',      // 已设为样本
    EXPORT: 'fas fa-cloud-upload-alt'  // 导出到云端
}

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
                geometry_type: layer.geometryType || 'Vector',
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

// 矢量图层样式相关方法
export const handleStyle = {
    // 打开矢量图层样式设置
    openVectorStyleSettings: (layer, currentVectorLayer, vectorStyle, showVectorStyleDialog) => {
        currentVectorLayer.value = layer;
        console.log('MapView.vue - openVectorStyleSettings - layer:', layer);

        if (layer.geometryType === 'Point') {
            vectorStyle.value = {
                color: layer.visParams.fillColor,
                weight: layer.visParams.radius / 3,
                opacity: layer.visParams.opacity,
                fillOpacity: layer.visParams.fillOpacity
            };
        } else if (layer.geometryType === 'Polygon') {
            vectorStyle.value = {
                color: layer.visParams.color,
                opacity: layer.visParams.opacity,
                fillOpacity: layer.visParams.fillOpacity,
                weight: layer.visParams.weight
            };
        } else {
            const style = layer.visParams || {};
            vectorStyle.value = {
                color: style.color,
                opacity: style.opacity
            };
        }
        console.log('MapView.vue - openVectorStyleSettings - vectorStyle:', vectorStyle.value);
        showVectorStyleDialog.value = true;
    },

    // 应用矢量图层样式
    applyVectorStyle: async (currentVectorLayer, vectorStyle, showVectorStyleDialog, map) => {
        try {
            if (!currentVectorLayer.value) return;

            console.log('MapView.vue - applyVectorStyle - currentVectorLayer:', currentVectorLayer.value);
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
            }
            else if (currentVectorLayer.value.geometryType === 'Polygon') {
                const style = {
                    color: vectorStyle.value.color,
                    weight: vectorStyle.value.weight,
                    opacity: vectorStyle.value.opacity,
                    fillOpacity: vectorStyle.value.fillOpacity
                };
                currentVectorLayer.value.leafletLayer.setStyle(style);
                currentVectorLayer.value.visParams = style;
            }
            else {
                // 转换颜色格式
                const colorInfo = toolManager.convertColor(vectorStyle.value.color);

                // 准备样式参数，只使用 Earth Engine 支持的参数
                const style_params = {
                    color: '#' + colorInfo.color,
                    opacity: parseFloat(vectorStyle.value.opacity)
                };

                console.log('Sending style params:', style_params);

                // 获取新的瓦片URL
                const response = await fetch(API_ROUTES.UPLOAD.ADD_VECTOR_ASSET, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        asset_id: currentVectorLayer.value.id,
                        style_params: style_params
                    })
                });

                const data = await response.json();
                if (!data.success) {
                    throw new Error(data.message);
                }

                // 移除旧图层
                if (currentVectorLayer.value.leafletLayer) {
                    map.value.removeLayer(currentVectorLayer.value.leafletLayer);
                }

                // 创建新图层并设置所有样式参数
                const newLayer = L.tileLayer(data.tileUrl, {
                    opacity: style_params.opacity,
                    maxZoom: 20,
                    maxNativeZoom: 20,
                    tileSize: 256,
                    updateWhenIdle: false,
                    updateWhenZooming: false,
                    keepBuffer: 2,
                    zIndex: currentVectorLayer.value.zIndex
                });

                // 更新图层引用和样式参数，保持完整的样式信息
                currentVectorLayer.value.leafletLayer = newLayer;
                currentVectorLayer.value.visParams = {
                    color: style_params.color,
                    opacity: style_params.opacity
                };

                // 添加新图层到地图
                if (currentVectorLayer.value.visible) {
                    newLayer.addTo(map.value);
                    newLayer.setZIndex(currentVectorLayer.value.zIndex);
                }
            }

            showVectorStyleDialog.value = false;
            ElMessage.success('样式更新成功');
        } catch (error) {
            console.error('Error updating vector style:', error);
            ElMessage.error('更新样式失败');
        }
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

// 栅格图层管理相关方法
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
                    icon: MENU_ICONS.SATELLITE,
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
                    max: mapData.overlayLayers[0].max,
                    type: mapData.type
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
                    zIndex: newLayer.zIndex,
                    interactive: false
                })
                newLayer.tileUrl = layerData.url

                // 4. 添加到地图和图层数组
                newLayer.leafletLayer.addTo(map.value)
                layers.value.push(newLayer)
                console.log('MapView.vue - addNewLayer - newLayer', newLayer)
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
                if (layer.isSample) {
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
            console.log('MapView.vue - renameLayer - layer:', layer)
            if (layer.type === 'manual' || layer.type === 'vector') {
                layer.name = newName.trim()
                ElMessage.success('图层重命名成功')
                return true
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
    },

    //更新图层顺序
    updateLayerOrder: (layers, map) => {
        layers.value.forEach((layer, index) => {
            if (layer.leafletLayer && layer.visible) {
                const zIndex = 1000 + index;
                layer.zIndex = zIndex;

                // 只有栅格图层才有 setZIndex 方法
                if (layer.type === 'manual' || layer.type === 'vector') {
                    // 对于矢量图层，需要重新添加到地图以更新顺序
                    if (map.value.hasLayer(layer.leafletLayer)) {
                        layer.leafletLayer.remove();
                        layer.leafletLayer.addTo(map.value);
                    }
                } else {
                    // 栅格图层可以直接设置 zIndex
                    layer.leafletLayer.setZIndex(zIndex);
                }
            }
        });
    },

    // 更新范围
    updateRangeBasedOnBands: async (currentLayer, vis, visParams, API_ROUTES) => {
        try {
            if (!currentLayer.value) return;

            // 添加加载状态到 Apply 按钮
            const applyButton = document.querySelector('.el-dialog__body .button-group .el-button--primary')
            if (applyButton) {
                applyButton.disabled = true
                applyButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 计算中...'
                console.log('MapView.vue - updateRangeBasedOnBands - applyButton:', applyButton.innerHTML)
            }
            console.log('MapView.vue - updateRangeBasedOnBands - vis:', vis);

            // 调用后端口计算统计值
            const response = await fetch(API_ROUTES.MAP.COMPUTE_STATS, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    layer_id: currentLayer.value.id,
                    bands: visParams.bands
                })
            });

            const result = await response.json();

            if (result.success) {
                // 使用范围标准化函数处理最大最小值
                const normalizedRange = normalizeRange(result.min, result.max);

                // 更新当前图层最大小值
                currentLayer.value.min = normalizedRange.min;
                currentLayer.value.max = normalizedRange.max;


                console.log('MapView.vue - updateRangeBasedOnBands - new range:', normalizedRange);
            } else {
                // 如果计算失败，使用传入的值
                // visParams.range = [vis.min, vis.max];
                currentLayer.value.min = vis.min;
                currentLayer.value.max = vis.max;
                console.warn('MapView.vue - Failed to compute stats, using provided values');
            }
            visParams.range = [vis.min, vis.max];
        } catch (error) {
            console.error('MapView.vue - Error updating range:', error);
            // 发生错误时使用传入的值
            visParams.range = [vis.min, vis.max];
            currentLayer.value.min = vis.min;
            currentLayer.value.max = vis.max;
        } finally {
            // 恢复按钮状态
            const applyButton = document.querySelector('.el-dialog__body .button-group .el-button--primary')
            if (applyButton) {
                applyButton.disabled = false
                applyButton.innerHTML = 'Apply'
            }
        }
    },

    // 应用可视化参数
    applyVisParams: async (map, currentLayer, visParams, showLayerSettings, bandMode, palettes, selectedPalette, layers, API_ROUTES) => {
        try {
            if (!currentLayer.value || !map) return;

            // 添加加载状态
            const applyButton = document.querySelector('.el-dialog__body .button-group .el-button--primary')
            if (applyButton) {
                applyButton.disabled = true
                applyButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 应用中...'
            }

            const updatedVisParams = {
                bands: visParams.bands,
                min: visParams.range[0],
                max: visParams.range[1],
                gamma: visParams.gamma,
            }

            // 如果是单波段，添加调色板
            if (bandMode.value === 1) {
                updatedVisParams.bands = [visParams.bands[0]]
                updatedVisParams.palette = palettes[selectedPalette.value]
                updatedVisParams.gamma = null
            }

            const response = await fetch(API_ROUTES.LAYER.UPDATE_VIS_PARAMS, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    satellite: currentLayer.value.satellite,
                    visParams: updatedVisParams,
                    layerId: currentLayer.value.id
                })
            })

            const data = await response.json()

            if (data.tileUrl) {
                const layer = layers.value.find(l => l.id === currentLayer.value.id)
                if (layer) {
                    // 修改图层移除逻辑
                    if (layer.leafletLayer && map.value.hasLayer(layer.leafletLayer)) {
                        layerChangeRemove(map.value, layer.leafletLayer);
                    }

                    // 创建新图层
                    const newLeafletLayer = L.tileLayer(data.tileUrl, {
                        opacity: currentLayer.value.opacity,
                        maxZoom: 20,
                        maxNativeZoom: 20,
                        tileSize: 256,
                        updateWhenIdle: false,
                        updateWhenZooming: false,
                        keepBuffer: 2,
                        zIndex: layer.zIndex
                    })

                    // 更新图层引用和参数
                    layer.leafletLayer = newLeafletLayer
                    layer.visParams = { ...updatedVisParams }

                    // 如果图层是可见的，则添加到地图
                    if (layer.visible) {
                        newLeafletLayer.addTo(map.value)
                        newLeafletLayer.setZIndex(1000 + layers.value.indexOf(layer))
                    }
                }
                showLayerSettings.value = false
            }
        } catch (error) {
            console.error('MapView.vue - Error updating vis params:', error)
            ElMessage.error('更新图层样式失败')
        } finally {
            // 恢复按钮状态
            const applyButton = document.querySelector('.el-dialog__body .button-group .el-button--primary')
            if (applyButton) {
                applyButton.disabled = false
                applyButton.innerHTML = 'Apply'
            }
        }
    }
};

// 底图管理相关方法
export const baseMapManager = {
    // 切换底图
    changeBaseMap: (map, baseLayer, baseMaps, selectedBaseMap, baseLayerVisible) => {
        // 正确移除旧底图
        if (baseLayer) {
            layerChangeRemove(map.value, baseLayer)
        }

        // 创建新底图
        const selectedMap = baseMaps.find(m => m.id === selectedBaseMap.value)
        if (selectedMap) {
            // 处理普通瓦片服务
            const newBaseLayer = L.tileLayer(selectedMap.url, {
                subdomains: selectedMap.subdomains || 'abc',
                attribution: selectedMap.attribution,
                maxZoom: 20,
                maxNativeZoom: 20
            })

            if (baseLayerVisible.value) {
                newBaseLayer.addTo(map.value)
                newBaseLayer.setZIndex(0)
            }

            return newBaseLayer  // 返回新创建的图层
        }
        return null
    }
};

// 导出图层管理
export const exportManager = {
    exportToCloud: async (layer, API_ROUTES, folder = 'EarthEngine_Exports', scale = 30) => {
        try {
            console.log('MapView.vue - exportToCloud - layer:', layer);

            const requestBody = {
                layer_id: layer.id,
                layer_name: layer.name,
                layer_type: layer.type,
                vis_params: layer.visParams,
                geometryType: layer.geometryType,
                folder: folder,
                scale: scale  // 添加分辨率参数
            };

            if (layer.type === 'manual') {
                if (layer.geometryType === 'Polygon') {
                    requestBody.features = [{
                        coordinates: layer.geometry.coordinates[0]
                    }];
                } else {
                    requestBody.features = layer.features;
                }
            }

            const response = await fetch(API_ROUTES.MAP.EXPORT_TO_CLOUD, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            if (data.success) {
                ElMessage.success('图层已成功导出到云端');
                return true;
            } else {
                throw new Error(data.message || '导出失败');
            }
        } catch (error) {
            console.error('Error exporting layer:', error);
            ElMessage.error(error.message || '导出图层失败');
            return false;
        }
    },
    exportToAsset: async (layer, API_ROUTES, assetId, description, scale=30) => {
        try {
            console.log('MapView.vue - exportToCloud - layer:', layer);

            const requestBody = {
                layer_id: layer.id,
                layer_name: layer.name,
                layer_type: layer.type,
                vis_params: layer.visParams,
                geometryType: layer.geometryType,
                asset_id: assetId,
                description: description,
                scale: scale  // 添加分辨率参数
            };

            if (layer.type === 'manual') {
                if (layer.geometryType === 'Polygon') {
                    requestBody.features = [{
                        coordinates: layer.geometry.coordinates[0]
                    }];
                } else {
                    requestBody.features = layer.features;
                }
            }

            const response = await fetch(API_ROUTES.MAP.EXPORT_TO_ASSET, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            if (data.success) {
                ElMessage.success('图层已成功导出到资产');
                return true;
            } else {
                throw new Error(data.message || '导出失败');
            }
        } catch (error) {
            console.error('Error exporting layer:', error);
            ElMessage.error(error.message || '导出图层失败');
            return false;
        }
    }
};


export const toolManager = {
    getPalettePreviewStyle: (colors) => {
        return {
            background: `linear-gradient(to right, ${colors.join(',')})`
        }
    },
    getSliderStep: () => {
        return 0.001;
    },
    formatSliderValue: (value) => {
        return value.toFixed(3);
    },
    debounce: (fn, delay) => {
        let timer = null;
        return function (...args) {
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => {
                fn.apply(this, args);
            }, delay);
        };
    },
    convertColor: (color) => {
        // 如果是 rgba 格式，转换为十六进制
        if (color.startsWith('rgba')) {
            const values = color.match(/[\d.]+/g);
            if (values.length >= 3) {
                const r = parseInt(values[0]);
                const g = parseInt(values[1]);
                const b = parseInt(values[2]);
                const a = parseFloat(values[3]);

                // 转换为十六进制，不包含 # 符号
                const hex = ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
                return {
                    color: hex,
                    opacity: a
                };
            }
        }
        // 如果是十六进制格式，移除 # 符号
        return {
            color: color.replace('#', ''),
            opacity: 1
        };
    },
    getPixelValue: async (e, isPixelToolActive, pixelValues) => {
        if (!isPixelToolActive) return;

        try {
            const response = await fetch(API_ROUTES.MAP.GET_PIXEL_VALUE, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: e.latlng.lat,
                    lng: e.latlng.lng
                })
            });

            const data = await response.json();
            if (data.success) {
                pixelValues.value = data.pixel_values;
            } else {
                ElMessage.error(data.message || '获取像素值失败');
            }
        } catch (error) {
            console.error('Error getting pixel values:', error);
            ElMessage.error('获取像素值失败');
        }
    },
    togglePixelTool: (isPixelToolActive, map, pixelValues) => {
        isPixelToolActive.value = !isPixelToolActive.value;

        if (isPixelToolActive.value) {
            map.value.getContainer().style.cursor = 'crosshair';
            // 添加点击事件监听器，传入所需参数
            map.value.on('click', (e) => toolManager.getPixelValue(e, isPixelToolActive, pixelValues));
        } else {
            map.value.off('click');
            map.value.getContainer().style.cursor = '';
            pixelValues.value = null;
        }
    },
    createShape: (event,layers,drawnItems,map,pointFeatures,pointLayerCounter) => {
        const layer = event.layer;
        drawnItems.value.addLayer(layer);

        let coordinates;
        let geometryType;

        // 根据类型处理坐标
        if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
            // 多边形处理保持不变
            coordinates = {
                type: 'Polygon',
                coordinates: [layer.getLatLngs()[0].map(latLng => [latLng.lng, latLng.lat])]
            };
            geometryType = 'Polygon';
            console.log('MapView.vue - initDrawControl - coordinates:', coordinates.coordinates);


            // 多边形仍然创建独立图层
            const newLayer = {
                id: `drawn_${Date.now()}`,
                name: '绘制区域',
                type: 'manual',
                visible: true,
                isStudyArea: false,
                opacity: 1,
                visParams: {
                    color: '#3388ff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.2,
                },
                geometry: coordinates,
                geometryType: geometryType,
                zIndex: 1000 + layers.value.length
            };

            const vectorLayer = L.geoJSON(coordinates, {
                style: newLayer.visParams,
                interactive: false
            });

            newLayer.leafletLayer = vectorLayer;
            layers.value.push(newLayer);
            vectorLayer.addTo(map.value);
        }
        else if (layer instanceof L.Marker) {
            coordinates = {
                type: 'Point',
                coordinates: [layer.getLatLng().lng, layer.getLatLng().lat]
            };

            // 查找或创建点图层
            let pointLayer = layers.value.find(l => l.id === `points_layer_${pointLayerCounter.value}`);
            if (!pointLayer) {
                // 创建新的点图层
                pointLayer = {
                    id: `points_layer_${pointLayerCounter.value}`,
                    name: `点集合 ${pointLayerCounter.value + 1}`,
                    icon: 'fas fa-map-marker-alt',
                    type: 'manual',
                    geometryType: 'Point',
                    visible: true,
                    opacity: 1,
                    features: [],
                    visParams: {
                        radius: 6,
                        fillColor: "#3388ff",
                        color: "#ffffff",
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.8
                    }
                };

                // 创建 Leaflet 图层
                pointLayer.leafletLayer = L.geoJSON({
                    type: 'FeatureCollection',
                    features: []
                }, {
                    pointToLayer: (feature, latlng) => {
                        return L.circleMarker(latlng, pointLayer.visParams);
                    }
                }).addTo(map.value);

                // 添加到图层列表
                layers.value.push(pointLayer);
            }

            // 添加新点到特征集合
            pointLayer.features.push(coordinates);
            pointFeatures.value = [...pointLayer.features];

            // 只添加新点，而不是重新创建整个图层
            pointLayer.leafletLayer.addData({
                type: 'Feature',
                geometry: coordinates,
                properties: {}
            });
        }
    },
    getPointLayer: (layers, e, map) => {
        // 提取更新图层的公共方法
        const updatePointLayer = (layer, features) => {
            map.value.removeLayer(layer.leafletLayer);
            layer.leafletLayer = L.geoJSON({
                type: 'FeatureCollection',
                features: features.map(point => ({
                    type: 'Feature',
                    geometry: point,
                    properties: {}
                }))
            }, {
                pointToLayer: (feature, latlng) => {
                    return L.circleMarker(latlng, layer.visParams);
                }
            });
            
            if (layer.visible) {
                layer.leafletLayer.addTo(map.value);
            }
        };

        const pointLayers = layers.value.filter(layer => 
            layer.type === 'manual' && layer.geometryType === 'Point'
        );

        pointLayers.forEach(pointLayer => {
            if (pointLayer.leafletLayer) {
                pointLayer.leafletLayer.eachLayer(marker => {
                    console.log(pointLayer);
                    if(pointLayer.visible){
                    const markerLatLng = marker.getLatLng();
                    const clickPoint = map.value.latLngToContainerPoint(e.latlng);
                    const markerPoint = map.value.latLngToContainerPoint(markerLatLng);
                    
                    const distance = clickPoint.distanceTo(markerPoint);
                    
                    if (distance <= pointLayer.visParams.radius + 2) {
                        const actionButton = L.popup({
                            closeButton: false,
                            className: 'point-action-popup'
                        })
                            .setLatLng(markerLatLng)
                            .setContent(`
                                <div class="point-action-container">
                                    <button class="point-move-btn">
                                        <i class="fas fa-arrows-alt"></i> 移动到其他图层
                                    </button>
                                    <button class="point-delete-btn">
                                        <i class="fas fa-trash"></i> 删除点位
                                    </button>                                   
                                </div>
                            `);
                        
                        actionButton.addTo(map.value);

                        setTimeout(() => {
                            // 处理删除操作
                            const deleteBtn = document.querySelector('.point-delete-btn');
                            if (deleteBtn) {
                                deleteBtn.onclick = () => {
                                    const pointIndex = pointLayer.features.findIndex(
                                        point => point.coordinates[0] === markerLatLng.lng 
                                            && point.coordinates[1] === markerLatLng.lat
                                    );
                                    
                                    if (pointIndex > -1 && !pointLayer.isSample) {
                                        pointLayer.features.splice(pointIndex, 1);
                                        updatePointLayer(pointLayer, pointLayer.features);
                                        map.value.closePopup(actionButton);
                                        
                                        if (pointLayer.features.length === 0) {
                                            ElMessage.warning('该点图层已无点位，建议删除图层');
                                        }
                                    } else {
                                        ElMessage.warning('该点位为样本点，无法删除');
                                        map.value.closePopup(actionButton);
                                    }
                                };
                            }

                            // 处理移动操作
                            const moveBtn = document.querySelector('.point-move-btn');
                            if (moveBtn) {
                                moveBtn.onclick = () => {
                                    const otherLayers = pointLayers.filter(layer => 
                                        layer.id !== pointLayer.id
                                    );

                                    if (otherLayers.length === 0) {
                                        ElMessage.warning('没有其他可用的点图层');
                                        return;
                                    }

                                    const layerSelectPopup = L.popup({
                                        closeButton: true,
                                        className: 'layer-select-popup'
                                    })
                                        .setLatLng(markerLatLng)
                                        .setContent(`
                                            <div class="layer-select-container">
                                                <h4>选择目标图层</h4>
                                                <div class="layer-list">
                                                    ${otherLayers.map(layer => `
                                                        <button class="layer-select-btn" data-layer-id="${layer.id}">
                                                            ${layer.name}
                                                        </button>
                                                    `).join('')}
                                                </div>
                                            </div>
                                        `);

                                    map.value.closePopup(actionButton);
                                    layerSelectPopup.addTo(map.value);

                                    setTimeout(() => {
                                        document.querySelectorAll('.layer-select-btn').forEach(btn => {
                                            btn.onclick = () => {
                                                const targetLayerId = btn.getAttribute('data-layer-id');
                                                const targetLayer = otherLayers.find(l => l.id === targetLayerId);
                                                
                                                if (targetLayer) {
                                                    const pointIndex = pointLayer.features.findIndex(
                                                        point => point.coordinates[0] === markerLatLng.lng 
                                                            && point.coordinates[1] === markerLatLng.lat
                                                    );
                                                    
                                                    if (pointIndex > -1) {
                                                        const point = pointLayer.features.splice(pointIndex, 1)[0];
                                                        
                                                        // 更新源图层和目标图层
                                                        updatePointLayer(pointLayer, pointLayer.features);
                                                        targetLayer.features.push(point);
                                                        targetLayer.leafletLayer.addData({
                                                            type: 'Feature',
                                                            geometry: point,
                                                            properties: {}
                                                        });

                                                        map.value.closePopup(layerSelectPopup);
                                                        ElMessage.success('点位已成功移动到新图层');
                                                    }
                                                }
                                            };
                                        });
                                    }, 0);
                                };
                            }
                        }, 0);
                    }
                }
                });
            }
        });
    },
    //拖动事件开始
    handleDragStart: (e, layer) => {
        e.dataTransfer.setData('text/plain', layer.id);
        e.target.classList.add('dragging');
    },

    handleDragEnd: (e) => {
        e.target.classList.remove('dragging');
    },

    handleDragOver: (e) => {
        e.preventDefault();
        const dragItem = e.target.closest('.layer-item');
        if (dragItem) {
            dragItem.classList.add('drag-over');
        }
    },

    handleDragLeave: (e) => {
        const dragItem = e.target.closest('.layer-item');
        if (dragItem) {
            dragItem.classList.remove('drag-over');
        }
    },

    handleDrop: async (e, targetLayer, layersRef) => {  // 添加 async
        e.preventDefault();
        const draggedLayerId = e.dataTransfer.getData('text/plain');
        const draggedLayer = layersRef.find(l => l.id === draggedLayerId);
        
        if (draggedLayer && targetLayer.id !== draggedLayerId) {
            try {
                // 获取源和目标索引
                const fromIndex = layersRef.findIndex(l => l.id === draggedLayerId);
                const toIndex = layersRef.findIndex(l => l.id === targetLayer.id);
                
                // 移除拖动的图层
                layersRef.splice(fromIndex, 1);
                // 插入到新位置
                layersRef.splice(toIndex, 0, draggedLayer);
                
                // 更新图层的 zIndex
                layersRef.forEach((layer, index) => {
                    if (layer.leafletLayer) {
                        layer.zIndex = 1000 + layersRef.length - index;
                        layer.leafletLayer.setZIndex(layer.zIndex);
                    }
                });

                // 发送请求到后端更新数据集顺序
                const response = await fetch(`${API_ROUTES.MAP.UPDATE_LAYER_ORDER}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        layers: layersRef.map(layer => ({
                            id: layer.id,
                            index: layer.zIndex
                        }))
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to update layer order');
                }
            } catch (error) {
                console.error('Error updating layer order:', error);
                ElMessage.error('更新图层顺序失败');
            }
        }
        
        // 移除所有拖拽相关的样式类
        document.querySelectorAll('.layer-item').forEach(item => {
            item.classList.remove('drag-over', 'dragging');
        });
    }
    //拖动事件结束
}
