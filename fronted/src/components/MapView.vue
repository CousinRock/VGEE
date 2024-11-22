<template>
    <div class="map-container">
        <div id="map"></div>

        <!-- 地图工具栏 -->
        <div class="map-tools">
            <div class="tool-group">
                <div class="tool-button" @click="toggleLayerControl" :class="{ active: showLayerControl }" title="图层">
                    <i class="fas fa-layer-group"></i>
                </div>
            </div>

            <!-- 图层控制面板 -->
            <div class="layer-control" v-if="showLayerControl">
                <div class="layer-item">
                    <div class="layer-header">
                        <input type="checkbox" v-model="baseLayerVisible" id="baseLayer">
                        <label for="baseLayer">
                            <i class="fas fa-map"></i>
                            <span>底图</span>
                        </label>
                        <button class="layer-settings" @click="showBaseMapSettings = true">
                            <i class="fas fa-cog"></i>
                        </button>
                    </div>
                </div>

                <!-- 动态图列表 -->
                <div class="layer-item" v-for="layer in layers" :key="layer.id">
                    <div class="layer-header">
                        <input type="checkbox" v-model="layer.visible" :id="layer.id">
                        <label :for="layer.id">
                            <i :class="layer.icon"></i>
                            <span>{{ layer.name }}</span>
                        </label>
                        <div class="layer-actions">
                            <button class="layer-settings" @click="openLayerSettings(layer)">
                                <i class="fas fa-cog"></i>
                            </button>
                            <button class="remove-layer" @click="removeLayer(layer.id, layer.name)">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <input type="range" v-model="layer.opacity" min="0" max="1" step="0.1" class="opacity-slider"
                        v-if="layer.visible">
                </div>
            </div>
        </div>

        <!-- 添加底图设置对话框 -->
        <el-dialog v-model="showBaseMapSettings" title="底图设置" width="300px">
            <div class="basemap-settings">
                <div class="setting-item">
                    <label>底图类型</label>
                    <el-select v-model="selectedBaseMap" @change="changeBaseMap">
                        <el-option v-for="map in baseMaps" :key="map.id" :label="map.name" :value="map.id" />
                    </el-select>
                </div>
            </div>
        </el-dialog>

        <!-- 修改图层设置对话框 -->
        <el-dialog v-model="showLayerSettings" title="图层设置" width="500px">
            <div class="layer-settings-content" v-if="currentLayer">
                <!-- 波段显示模式选择 -->
                <div class="band-mode-selector">
                    <el-radio-group v-model="bandMode">
                        <el-radio :value="1">1 band (Grayscale)</el-radio>
                        <el-radio :value="3">3 bands (RGB)</el-radio>
                    </el-radio-group>
                </div>

                <!-- 波段选择区域 -->
                <div class="band-selection" v-if="bandMode === 1">
                    <div class="band-select">
                        <label>Band</label>
                        <el-select v-model="visParams.bands[0]">
                            <el-option v-for="band in availableBands" :key="band" :label="band" :value="band" />
                        </el-select>
                    </div>

                    <!-- 只在单波段模式下显示调色板选择器 -->
                    <div class="palette-select" style="margin-top: 10px;">
                        <label>Color Palette</label>
                        <el-select v-model="selectedPalette" style="width: 100%;">
                            <el-option label="Default" value="default">
                                <div class="palette-preview default"></div>
                                <span>Default</span>
                            </el-option>
                            <el-option label="Grayscale" value="grayscale">
                                <div class="palette-preview grayscale"></div>
                                <span>Grayscale</span>
                            </el-option>
                            <el-option label="Red to Green" value="RdYlGn">
                                <div class="palette-preview rdylgn"></div>
                                <span>Red to Green</span>
                            </el-option>
                            <el-option label="Blue to Red" value="RdYlBu">
                                <div class="palette-preview rdylbu"></div>
                                <span>Blue to Red</span>
                            </el-option>
                            <el-option label="Spectral" value="Spectral">
                                <div class="palette-preview spectral"></div>
                                <span>Spectral</span>
                            </el-option>
                        </el-select>
                    </div>
                </div>

                <!-- 多波段选择区域 -->
                <div class="band-selection" v-else>
                    <!-- 原有的RGB波段选择保持不变 -->
                    <div class="band-select">
                        <label>vis-red</label>
                        <el-select v-model="visParams.bands[0]">
                            <el-option v-for="band in availableBands" :key="band" :label="band" :value="band" />
                        </el-select>
                    </div>
                    <div class="band-select">
                        <label>vis-green</label>
                        <el-select v-model="visParams.bands[1]">
                            <el-option v-for="band in availableBands" :key="band" :label="band" :value="band" />
                        </el-select>
                    </div>
                    <div class="band-select">
                        <label>vis-blue</label>
                        <el-select v-model="visParams.bands[2]">
                            <el-option v-for="band in availableBands" :key="band" :label="band" :value="band" />
                        </el-select>
                    </div>
                </div>

                <!-- 拉伸方式选择 -->
                <div class="stretch-selection">
                    <label>Stretch:</label>
                    <el-select v-model="stretchType" style="width: 100%">
                        <el-option label="None" value="none" />
                        <el-option label="Custom" value="custom" />
                        <el-option label="Standard Deviation" value="std" />
                        <el-option label="Histogram Equalization" value="hist" />
                    </el-select>
                </div>

                <!-- 数值范围设置 -->
                <div class="range-setting">
                    <label>Range:</label>
                    <el-slider v-model="visParams.range" range
                        :min="currentLayer.bandInfo ? Math.min(...Object.values(currentLayer.bandInfo.bandStats).map(s => s.min)) : 0"
                        :max="currentLayer.bandInfo ? Math.max(...Object.values(currentLayer.bandInfo.bandStats).map(s => s.max)) : 100"
                        :step="getSliderStep(currentLayer.value?.satellite)"
                        :format-tooltip="val => formatSliderValue(val)" />
                    <div class="range-values">
                        {{ formatSliderValue(visParams.range[0]) }} – {{ formatSliderValue(visParams.range[1]) }}
                    </div>
                </div>

                <!-- 不透明度设置 -->
                <div class="opacity-setting">
                    <label>Opacity:</label>
                    <el-slider v-model="currentLayer.opacity" :min="0" :max="1" :step="0.01"
                        :format-tooltip="val => (val * 100).toFixed(0) + '%'" />
                    <div class="opacity-value">{{ (currentLayer.opacity * 100).toFixed(0) }}%</div>
                </div>

                <!-- Gamma值设置 -->
                <div class="gamma-setting">
                    <label>Gamma:</label>
                    <el-slider v-model="visParams.gamma" :min="0.1" :max="2.0" :step="0.1"
                        :format-tooltip="val => val.toFixed(1)" />
                    <div class="gamma-value">{{ visParams.gamma.toFixed(1) }}</div>
                </div>

                <!-- 按钮区域 -->
                <div class="button-group">
                    <el-button @click="importSettings">Import</el-button>
                    <el-button type="primary" @click="applyVisParams">Apply</el-button>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick, reactive, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import '@fortawesome/fontawesome-free/css/all.css'

const props = defineProps({
    mapData: {
        type: Object,
        default: () => ({})
    }
})

// 状态变量
const layers = ref([])
const showLayerControl = ref(false)
const baseLayerVisible = ref(true)
const showBaseMapSettings = ref(false)
const showLayerSettings = ref(false)
const selectedBaseMap = ref('satellite')
const currentLayer = ref(null)
const availableBands = ref([])
const bandStats = ref({})
const bandMode = ref(3)
const stretchType = ref('custom')
const visParams = reactive({
    bands: ['B4', 'B3', 'B2'],
    range: [0, 100],
    min: 0,
    max: 0.3,
    gamma: 1.4
})

let map = null
let baseLayer = null

// 添加调色板状态
const selectedPalette = ref('default')

// 调色板映射
const palettes = {
    default: ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
        '74A901', '66A000', '529400', '3E8601', '207401', '056201',
        '004C00', '023B01', '012E01', '011D01', '011301'],
    grayscale: ['black', 'white'],
    RdYlGn: ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#ffffbf',
        '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850'],
    RdYlBu: ['#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf',
        '#e0f3f8', '#abd9e9', '#74add1', '#4575b4'],
    Spectral: ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b',
        '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2']
}

// 切换图层控制面板显示
const toggleLayerControl = () => {
    showLayerControl.value = !showLayerControl.value
}

// 添加新图层
const addNewLayer = async (layerName, mapData) => {
    try {
        if (!mapData?.overlayLayers?.length) {
            alert('未找到符合条件的影像数据')
            return
        }

        // 预先获取波段信息并缓存
        const response = await fetch(`http://localhost:5000/layer-info?satellite=${mapData.satellite}`)
        const layerInfo = await response.json()
        console.log('Layer info:', layerInfo)

        // 根据卫星类型设置默认波段组合
        let defaultBands
        switch (mapData.satellite) {
            case 'LANDSAT':
                defaultBands = ['B4', 'B3', 'B2']  // Landsat 自然色
                break
            case 'SENTINEL':
                defaultBands = ['B4', 'B3', 'B2']  // Sentinel-2 自然色
                break
            case 'MODIS':
                defaultBands = ['NDVI']  // MODIS 默认显示 NDVI
                break
            default:
                defaultBands = layerInfo.bands.slice(0, 3)  // 默认使用前三个波段
        }

        mapData.overlayLayers.forEach(layerData => {
            const newLayer = {
                id: `layer-${Date.now()}`,
                name: layerName,
                icon: 'fas fa-satellite',
                visible: true,
                opacity: 1,
                leafletLayer: null,
                zIndex: 1000 + layers.value.length,
                satellite: mapData.satellite || 'LANDSAT',
                // 缓存波段信息
                bandInfo: layerInfo,
                visParams: {
                    bands: defaultBands,  // 使用根据卫星类型确定的默认波段
                    min: bandStats.value[defaultBands[0]]?.min || 0,
                    max: bandStats.value[defaultBands[0]]?.max || 1,
                    gamma: 1.4
                }
            }

            // 创建Leaflet图层
            newLayer.leafletLayer = L.tileLayer(layerData.url, {
                opacity: newLayer.opacity,
                maxZoom: 20,
                maxNativeZoom: 20,
                tileSize: 256,
                updateWhenIdle: false,
                updateWhenZooming: false,
                keepBuffer: 2,
                zIndex: newLayer.zIndex,
                crs: map.options.crs  // 使用与地图相同的CRS
            })

            newLayer.leafletLayer.addTo(map)
            layers.value.push(newLayer)
        })

        updateLayerOrder()
    } catch (error) {
        console.error('Error adding layer:', error)
        alert('添加图层失败，请重试')
    }
}

// 移除选定的图层
const removeLayer = (layerId, layerName) => {
    console.log('remove layer:', layerName);

    if (!map) return;

    let mapLayers = Object.values(map._layers);

    mapLayers.forEach((mapLayer) => {
        // 检查是否是我们要删除的图层且不是底图
        //确保删除的是瓦片图层的实例
        if (mapLayer instanceof L.TileLayer &&
            mapLayer !== baseLayer &&
            mapLayer._leaflet_id === layers.value.find(l => l.id === layerId)?.leafletLayer._leaflet_id) {
            // 禁用动画
            mapLayer.options.zoomAnimation = false;
            // 移除图层
            map.removeLayer(mapLayer);
        }
    });

    // 从数组中移除图层
    const layerIndex = layers.value.findIndex(l => l.id === layerId);
    if (layerIndex > -1) {
        layers.value.splice(layerIndex, 1);
    }
};


// 获取滑块步长
const getSliderStep = (satelliteType) => {
    if (!satelliteType) return 0.1;

    switch (satelliteType) {
        case 'LANDSAT':
            return 0.001;  // Landsat 数据范围通常在 0-1 ，需要���精细的控制
        case 'SENTINEL':
            return 1;      // Sentinel 数据范围较大，使用整数步长
        case 'MODIS':
            return 1;      // MODIS 数据也使用整数步长
        default:
            return 0.1;
    }
};

// 格式化显示值
const formatSliderValue = (value) => {
    if (!currentLayer.value) return value.toFixed(1);

    switch (currentLayer.value.satellite) {
        case 'LANDSAT':
            return value.toFixed(3);  // Landsat 显示3位小数
        case 'SENTINEL':
        case 'MODIS':
            return value.toFixed(0);  // Sentinel 和 MODIS 显示整数
        default:
            return value.toFixed(1);
    }
};

// 监听图层变化
watch(layers, (newLayers) => {
    if (!map) return;

    nextTick(() => {
        newLayers.forEach(layer => {
            if (layer.leafletLayer) {
                layer.leafletLayer.setOpacity(layer.opacity)

                if (layer.visible) {
                    // 如果图层应该可见，直接使用 layer.leafletLayer
                    if (!map.hasLayer(layer.leafletLayer)) {
                        layer.leafletLayer.addTo(map)
                    }
                    layer.leafletLayer.setZIndex(1000 + newLayers.indexOf(layer))
                } else {
                    // 如果图层应该隐藏，遍历查找并移除
                    let mapLayers = Object.values(map._layers);
                    mapLayers.forEach((mapLayer) => {
                        if (mapLayer instanceof L.TileLayer &&
                            mapLayer !== baseLayer &&
                            mapLayer._leaflet_id === layer.leafletLayer._leaflet_id) {
                            map.removeLayer(mapLayer)
                        }
                    });
                }
            }
        })
    })
}, { deep: true })

// 听底图可见
watch(baseLayerVisible, (newValue) => {
    nextTick(() => {
        if (baseLayer) {
            if (newValue) {
                baseLayer.addTo(map)
                baseLayer.setZIndex(0)
            } else {
                baseLayer.remove()
            }
        }
    })
})

// 初始化地图
onMounted(async () => {
    try {
        const response = await fetch(`http://localhost:5000/map-data`)
        const mapData = await response.json()

        map = L.map('map', {
            center: mapData.center,
            zoom: mapData.zoom,
            zoomAnimation: true,
            fadeAnimation: true,
            preferCanvas: true,
            wheelDebounceTime: 150,
            wheelPxPerZoomLevel: 120,
            // 添加投影相关配置
            crs: L.CRS.EPSG3857,  // 明确指定投影系统
            continuousWorld: true, // 确保连续的世界地图
            worldCopyJump: true,   // 允许在经度方向环
            maxBounds: L.latLngBounds(L.latLng(-85.06, -180), L.latLng(85.06, 180)), // 限制范围
            minZoom: 1,
            maxZoom: 20
        })

        // 修改底图配置
        const changeBaseMap = () => {
            if (baseLayer) {
                map.removeLayer(baseLayer)
            }
            const selectedMap = baseMaps.find(m => m.id === selectedBaseMap.value)
            if (selectedMap) {
                baseLayer = L.tileLayer(selectedMap.url, {
                    subdomains: selectedMap.subdomains || 'abc',
                    attribution: selectedMap.attribution,
                    maxZoom: 20,
                    maxNativeZoom: 20,
                    tileSize: 256,
                    zIndex: 0,
                    // 添加投影相关配置
                    continuousWorld: true,
                    noWrap: false,
                    bounds: L.latLngBounds(L.latLng(-85.06, -180), L.latLng(85.06, 180)),
                    crs: L.CRS.EPSG3857
                })

                if (baseLayerVisible.value) {
                    baseLayer.addTo(map)
                }
            }
        }

        // 优化缩放事件处理
        let zoomAnimationInProgress = false

        map.on('zoomstart', () => {
            zoomAnimationInProgress = true

            // 确保地图投影系统在缩放过程中保持稳定
            if (map && map.options.crs) {
                const currentZoom = map.getZoom()
                const scale = map.options.crs.scale(currentZoom)
                if (!scale) {
                    console.warn('Invalid zoom scale')
                    return
                }
            }

            layers.value.forEach(layer => {
                if (layer.leafletLayer && layer.visible) {
                    layer.leafletLayer.options.zoomAnimation = false
                    if (typeof layer.leafletLayer._removeAllTiles === 'function') {
                        layer.leafletLayer._removeAllTiles()
                    }
                }
            })
        })

        map.on('zoomend', () => {
            // 使用 setTimeout 确保在动画完全结束后再启用新的瓦片加载
            setTimeout(() => {
                zoomAnimationInProgress = false

                layers.value.forEach(layer => {
                    if (layer.leafletLayer && layer.visible) {

                        layer.leafletLayer.options.zoomAnimation = true
                        // 重新请求瓦片
                        layer.leafletLayer.redraw()
                    }
                })
            }, 250) // 添加适当的延迟
        })

        // 添加移动开始事件处理
        map.on('movestart', () => {
            if (!zoomAnimationInProgress) {
                layers.value.forEach(layer => {
                    if (layer.leafletLayer && layer.visible) {
                        layer.leafletLayer.options.zoomAnimation = false
                    }
                })
            }
        })

        // 添加移动结束事件处理
        map.on('moveend', () => {
            if (!zoomAnimationInProgress) {
                layers.value.forEach(layer => {
                    if (layer.leafletLayer && layer.visible) {
                        layer.leafletLayer.options.zoomAnimation = true
                    }
                })
            }
        })

        // 初始化底图
        changeBaseMap()

    } catch (error) {
        console.error('Error loading map:', error)
    }
})

// 更新图层顺序
const updateLayerOrder = () => {
    layers.value.forEach((layer, index) => {

        if (layer.leafletLayer && layer.visible) {
            const zIndex = 1000 + index
            layer.leafletLayer.setZIndex(zIndex)
        }
    })
}

// 监听图层可见性变化
watch(() => layers.value.map(l => l.visible), () => {
    nextTick(updateLayerOrder)
}, { deep: true })

// 暴露方法给父组件
defineExpose({
    addNewLayer
})

// 添加底图配置
const baseMaps = [
    {
        id: 'osm',
        name: 'OpenStreetMap',
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '© OpenStreetMap contributors'
    },
    {
        id: 'satellite',
        name: '卫星影像',
        url: 'http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '© Google'
    },
    {
        id: 'terrain',
        name: '地形图',
        url: 'http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '© Google'
    }
]

// 修改打开图层设置方法
const openLayerSettings = (layer) => {
    try {
        if (!layer.bandInfo) {
            console.error('No band info available')
            return
        }

        // 使用缓存的波段信息
        availableBands.value = layer.bandInfo.bands
        bandStats.value = layer.bandInfo.bandStats

        // 设置波段模式
        bandMode.value = layer.visParams.bands.length === 1 ? 1 : 3

        // 根据当前选择的波段设置范围
        updateRangeBasedOnBands(layer.visParams.bands, layer.satellite)

        // 更新 visParams
        Object.assign(visParams, {
            bands: [...layer.visParams.bands],
            min: visParams.range[0],
            max: visParams.range[1],
            gamma: layer.visParams.gamma || 1.4
        })

        // 初始化调色板选择
        selectedPalette.value = 'default'

        currentLayer.value = layer
        showLayerSettings.value = true
    } catch (error) {
        console.error('Error opening layer settings:', error)
    }
}

// 添加一个函数来更新范围设置
const updateRangeBasedOnBands = (selectedBands, satelliteType) => {
    if (!bandStats.value) return

    // 获取所选波段的最小和最大值
    let minVal = Infinity
    let maxVal = -Infinity

    selectedBands.forEach(band => {
        if (bandStats.value[band]) {
            minVal = Math.min(minVal, bandStats.value[band].min)
            maxVal = Math.max(maxVal, bandStats.value[band].max)
        }
    })

    // 如果没有找到统计信息，使用默认值
    if (minVal === Infinity || maxVal === -Infinity) {
        switch (satelliteType) {
            case 'LANDSAT':
                minVal = 0
                maxVal = 0.4
                break
            case 'SENTINEL':
                minVal = 0
                maxVal = 3000
                break
            case 'MODIS':
                minVal = -2000
                maxVal = 10000
                break
            default:
                minVal = 0
                maxVal = 100
        }
    }

    // 更新滑块的范围
    visParams.range = [minVal, maxVal]
}

// 应用可视化参数
const applyVisParams = async () => {
    try {
        if (!currentLayer.value || !map) return;

        const updatedVisParams = {
            bands: visParams.bands,
            min: visParams.range[0],
            max: visParams.range[1],
            gamma: visParams.gamma
        }

        // 如果是单波段，添加调色板
        if (bandMode.value === 1) {
            updatedVisParams.palette = palettes[selectedPalette.value]
        }

        const response = await fetch('http://localhost:5000/update-vis-params', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                satellite: currentLayer.value.satellite,
                visParams: updatedVisParams
            })
        })

        const data = await response.json()

        if (data.tileUrl) {
            const layer = layers.value.find(l => l.id === currentLayer.value.id)
            if (layer) {
                // 先移除旧图层
                if (layer.leafletLayer) {
                    let mapLayers = Object.values(map._layers);

                    mapLayers.forEach((mapLayer) => {
                        // 检查是否是我们要删除的图层且不是底图
                        // 确保删除的是瓦片图层的实例且是当前正在修改的图层
                        if (mapLayer instanceof L.TileLayer &&
                            mapLayer !== baseLayer &&
                            mapLayer._url === layer.leafletLayer._url) {  // 通过URL匹配确保是同一个图层

                            // 禁用动画
                            mapLayer.options.zoomAnimation = false;
                            // 移除图层
                            map.removeLayer(mapLayer);
                        }
                    });
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
                    newLeafletLayer.addTo(map)
                    newLeafletLayer.setZIndex(1000 + layers.value.indexOf(layer))
                }
            }
            showLayerSettings.value = false
        }
    } catch (error) {
        console.error('Error updating vis params:', error)
    }
}

// 修改波段变化的监听
watch(() => visParams.bands, (newBands) => {
    if (!currentLayer.value || !currentLayer.value.bandInfo) return
    updateRangeBasedOnBands(newBands, currentLayer.value.satellite)
}, { deep: true })

// 在 script setup 中添加 importSettings 函数
const importSettings = () => {
    // TODO: 实现导入设置功能
    console.log('Import settings clicked')
}

// 修改组件卸载时的清理代码
onUnmounted(() => {
    // 确保所有图层都被正确清理
    layers.value.forEach(layer => {
        if (layer.leafletLayer) {
            try {
                // 禁用动画
                layer.leafletLayer.options.zoomAnimation = false

                // 移除所有事件监听
                layer.leafletLayer.off()

                // 清除所有瓦片
                if (typeof layer.leafletLayer._removeAllTiles === 'function') {
                    layer.leafletLayer._removeAllTiles()
                }

                // 从地图中移除
                if (map && map.hasLayer(layer.leafletLayer)) {
                    map.removeLayer(layer.leafletLayer)
                }

                layer.leafletLayer = null
            } catch (error) {
                console.error('Error cleaning up layer:', error)
            }
        }
    })

    // 清理底图
    if (baseLayer) {
        try {
            baseLayer.options.zoomAnimation = false
            baseLayer.off()
            if (typeof baseLayer._removeAllTiles === 'function') {
                baseLayer._removeAllTiles()
            }
            if (map && map.hasLayer(baseLayer)) {
                map.removeLayer(baseLayer)
            }
            baseLayer = null
        } catch (error) {
            console.error('Error cleaning up base layer:', error)
        }
    }

    // 移除地图事件监听
    if (map) {
        map.off()
        map.remove()
        map = null
    }
})
</script>

<style src="../styles/map-view.css"></style>
