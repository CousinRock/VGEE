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
