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
                        :min="currentLayer.bandInfo ? currentLayer.min : 0"
                        :max="currentLayer.bandInfo ? currentLayer.max : 100"
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
import 'leaflet-draw'
import 'leaflet-draw/dist/leaflet.draw.css'

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
var index = 1

const map = ref(null)
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

// 添加绘制控制相关的状态
const drawnItems = ref(null)
const drawControl = ref(null)

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

        console.log('MapView.vue - addNewLayer - mapData:', mapData.overlayLayers[0].id);
        // 1. 预取波段信息并缓存
        const response = await fetch(`http://localhost:5000/layer-info?id=${mapData.overlayLayers[0].id}&satellite=${mapData.satellite}`)
        const layerInfo = await response.json()
        console.log('MapView.vue - addNewLayer - layerInfo:', layerInfo);

        // 2. 根据卫星类型设置默认波段组合
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

        // 3. 为每个图层创建新的图层对象
        mapData.overlayLayers.forEach(layerData => {
            const newLayer = {
                id: `layer-${index}-${layerInfo.satellite}`,
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

            // 4. 创建 Leaflet 图层
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

            // 5. 添加到地图和图层数组
            newLayer.leafletLayer.addTo(map.value)
            layers.value.push(newLayer)
            console.log('MapView.vue - newLayer.visParams:', newLayer.visParams);
        })

        index += 1

        // 6. 更新图层顺序
        updateLayerOrder()
    } catch (error) {
        console.error('MapView.vue - Error adding layer:', error)
        alert('添加图层失败，请重试')
    }
}

// 移除选定的图层
const removeLayer =async (layerId, layerName) => {
    console.log('MapView.vue - remove layer:', layerName);
    console.log('MapView.vue - layerId:', layerId);

    if (!map) return;

    try {
        // 先调用后端移除数据集中的图层
        const response = await fetch('http://localhost:5000/remove-layer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                layer_id: layerId
            })
        });

        const result = await response.json();
        if (!result.success) {
            console.error('MapView.vue - Failed to remove layer from dataset:', result.message);
            ElMessage.warning('从数据集移除图层失败，但会继续移除显示图层');
        }

        // 继续移除地图上的图层
        let mapLayers = Object.values(map.value._layers);

        mapLayers.forEach((mapLayer) => {
            // 检查是否是我们要删的图层且不是底图
            //确保删除的是瓦片图层的实例
            if (mapLayer instanceof L.TileLayer &&
                mapLayer !== baseLayer &&
                mapLayer._leaflet_id === layers.value.find(l => l.id === layerId)?.leafletLayer._leaflet_id) {
                // 禁用动画
                mapLayer.options.zoomAnimation = false;
                // 移除图层
                map.value.removeLayer(mapLayer);
            }
        });

        // 从数组中移除图层
        const layerIndex = layers.value.findIndex(l => l.id === layerId);
        if (layerIndex > -1) {
            layers.value.splice(layerIndex, 1);
        }
    } catch (error) {
        console.error('MapView.vue - Error removing layer:', error);
    }
};


// 获取滑块步长
const getSliderStep = (satelliteType) => {
    if (!satelliteType) return 0.1;

    switch (satelliteType) {
        case 'LANDSAT':
            return 0.001;  // Landsat 数据范围通常在 0-1 ，需要精细的控制
        case 'SENTINEL':
            return 1;      // Sentinel 数据范围较大，使用整数步长
        case 'MODIS':
            return 1;      // MODIS 数据也使用整数步长
        default:
            return 0.1;
    }
};

// 格式化显示
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

// 添加防抖函数
const debounce = (fn, delay) => {
    let timer = null;
    return function (...args) {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => {
            fn.apply(this, args);
        }, delay);
    };
};

// 监听图层变化时使用防抖
watch(layers, debounce((newLayers) => {
    if (!map) return;

    nextTick(() => {
        newLayers.forEach(layer => {
            if (layer.leafletLayer) {
                layer.leafletLayer.setOpacity(layer.opacity)

                if (layer.visible) {
                    // 如果图层应该可见，直接使用 layer.leafletLayer
                    if (!map.value.hasLayer(layer.leafletLayer)) {
                        layer.leafletLayer.addTo(map.value)
                    }
                    layer.leafletLayer.setZIndex(1000 + newLayers.indexOf(layer))
                } else {
                    // 如果图层应该隐藏遍历查找并移除
                    let mapLayers = Object.values(map.value._layers);
                    mapLayers.forEach((mapLayer) => {
                        if (mapLayer instanceof L.TileLayer &&
                            mapLayer !== baseLayer &&
                            mapLayer._leaflet_id === layer.leafletLayer._leaflet_id) {
                            map.value.removeLayer(mapLayer)
                        }
                    });
                }
            }
        })
    })
}, 100), { deep: true })

// 修改 changeBaseMap 函数
const changeBaseMap = () => {
    // 移除旧底图
    if (baseLayer) {
        // 先从地图中移除旧图层
        Object.values(map.value._layers).forEach(layer => {
            if (layer instanceof L.TileLayer && 
                (layer._url === baseLayer._url || 
                 baseMaps.some(m => layer._url === m.url.replace('{s}', layer.options.subdomains[0])))) {
                map.value.removeLayer(layer);
            }
        });
        
        // 清理旧底图的引用
        baseLayer.off();
        baseLayer = null;
    }

    // 创建新底图
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
            baseLayer.addTo(map.value)
        }
        
        // 添加日志以便调试
        console.log('MapView.vue - New baseLayer created:', {
            id: baseLayer._leaflet_id,
            url: baseLayer._url
        });
    }
}

// 修改底图可见性监听
watch(baseLayerVisible, (newValue) => {
    nextTick(() => {
        if (baseLayer) {
            if (newValue) {
                // 确保不会重复添加
                if (!map.value.hasLayer(baseLayer)) {
                    baseLayer.addTo(map.value)
                    baseLayer.setZIndex(0)
                }
            } else {
                if (map.value.hasLayer(baseLayer)) {
                    baseLayer.remove()
                }
            }
        }
    })
})

// 监听底图类型变化
watch(selectedBaseMap, () => {
    if (map.value) {
        changeBaseMap()
    }
})

// 在 onMounted 中只需要调用这个函
onMounted(async () => {
    try {
        // 创建地图实例时直接赋值给 ref
        map.value = L.map('map', {
            center: [20, 0],
            zoom: 3,
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

        // 初始化底图
        changeBaseMap()

        // 初始化绘制控件
        initDrawControl()

        // 添加滚动优化
        map.value.on('zoomstart', () => {
            // 禁用所有图层的动画
            layers.value.forEach(layer => {
                if (layer.leafletLayer) {
                    layer.leafletLayer.options.zoomAnimation = false;
                }
            });
        });

        map.value.on('zoomend', () => {
            // 重新启用动画
            setTimeout(() => {
                layers.value.forEach(layer => {
                    if (layer.leafletLayer) {
                        layer.leafletLayer.options.zoomAnimation = true;
                    }
                });
            }, 250);
        });

        // 添加绘制完成事件监听
        map.value.on(L.Draw.Event.CREATED, async (event) => {
            const layer = event.layer;
            drawnItems.value.addLayer(layer);

            // 获取绘制图形的坐标
            let coordinates;
            if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
                coordinates = {
                    type: 'Polygon',
                    coordinates: [layer.getLatLngs()[0].map(latLng => [latLng.lng, latLng.lat])]
                };
            }

            try {
                // 发送绘制的区域到后端
                const response = await fetch('http://localhost:5000/filter-by-geometry', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        geometry: coordinates,
                    })
                });
                console.log('Response:', response);
            } catch (error) {
                console.error('Error filtering images:', error);
            }
        });

        // 修改删除事���监听
        map.value.on(L.Draw.Event.DELETED, async (event) => {
            try {
                const layers = event.layers;

                // 获取被删除图层的坐标
                const deletedCoordinates = [];
                layers.eachLayer((layer) => {
                    if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
                        deletedCoordinates.push(
                            layer.getLatLngs()[0].map(latLng => [latLng.lng, latLng.lat])
                        );
                    }
                });

                // 先清理本地图层
                if (drawnItems.value) {
                    drawnItems.value.clearLayers();
                }

                // 然后再发送请求到后端
                const response = await fetch('http://localhost:5000/remove-geometry', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        coordinates: deletedCoordinates
                    })
                });

                // 等待后端响应后再进行其他操作
                await response.json();

            } catch (error) {
                console.error('Error removing geometries:', error);
            }
        });

        // 触发初始化完成事件
        emit('map-initialized', map.value)

    } catch (error) {
        console.error('MapView.vue - Error loading map:', error)
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

// 暴露方法和属性给父组件
defineExpose({
    layers,
    map: map,  // 使用 readonly 包装，防止外部修改
    addNewLayer,
    removeLayer,
    updateLayerOrder
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
const openLayerSettings = async (layer) => {
    try {
        currentLayer.value = layer
        console.log('MapView.vue - openLayerSettings - currentLayer:', currentLayer.value);
        
        // 如果已经有波段信息，直接使用
        if (layer.bandInfo) {
            availableBands.value = layer.bandInfo
            
            // 设置波段模式
            bandMode.value = layer.visParams.bands.length === 1 ? 1 : 3
            
            // 更新范围和参数
            updateRangeBasedOnBands(layer.visParams)
            Object.assign(visParams, {
                bands: [...layer.visParams.bands],
                min: visParams.range[0],
                max: visParams.range[1],
                gamma: layer.visParams.gamma || 1.4
            })
            
            showLayerSettings.value = true
            return
        }

    } catch (error) {
        console.error('MapView.vue - Error opening layer settings:', error)
        ElMessage.error('获取波段信息失败')
    }
}

// 添加一个函数来更新范围设置
const updateRangeBasedOnBands = (vis) => {
    visParams.range = [vis.min, vis.max]
}

// 应用可视化参数
const applyVisParams = async () => {
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
            gamma: visParams.gamma
        }

        console.log('MapView.vue - applyVisParams - updatedVisParams:', updatedVisParams);

        // 如果是单波段，添加调色板
        if (bandMode.value === 1) {
            updatedVisParams.bands = [visParams.bands[0]]
            updatedVisParams.palette = palettes[selectedPalette.value]
        }

        const response = await fetch('http://localhost:5000/update-vis-params', {
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
                // 先移除旧图层
                if (layer.leafletLayer) {
                    let mapLayers = Object.values(map.value._layers);

                    mapLayers.forEach((mapLayer) => {
                        // 检查是否是我们要删除的图层且不是底图
                        // 确保删除的是瓦片图层的例且是当前在修改的图层
                        if (mapLayer instanceof L.TileLayer &&
                            mapLayer !== baseLayer &&
                            mapLayer._url === layer.leafletLayer._url) {  // 通过URL匹配确保是同一个图层

                            // 禁用动画
                            mapLayer.options.zoomAnimation = false;
                            // 移除图层
                            map.value.removeLayer(mapLayer);
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

// 修改波段变化的监听
watch(() => visParams.bands, (newBands) => {
    if (!currentLayer.value || !currentLayer.value.bandInfo) return
    updateRangeBasedOnBands(visParams)
}, { deep: true })

// 在 script setup 中添加 importSettings 函数
const importSettings = () => {
    // TODO: 实现导入设置功能
    console.log('MapView.vue - Import settings clicked')
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
                if (map.value && map.value.hasLayer(layer.leafletLayer)) {
                    map.value.removeLayer(layer.leafletLayer)
                }

                layer.leafletLayer = null
            } catch (error) {
                console.error('MapView.vue - Error cleaning up layer:', error)
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
            if (map.value && map.value.hasLayer(baseLayer)) {
                map.value.removeLayer(baseLayer)
            }
            baseLayer = null
        } catch (error) {
            console.error('MapView.vue - Error cleaning up base layer:', error)
        }
    }

    // 移除地图事件监听
    if (map.value) {
        map.value.off()
        map.value.remove()
        map.value = null
    }

    // 清理绘制相关的内容
    if (drawnItems.value) {
        map.value.removeLayer(drawnItems.value)
    }
    if (drawControl.value) {
        map.value.removeControl(drawControl.value)
    }
})

// 初始化绘制控件
const initDrawControl = () => {
    // 创建绘制图层组
    drawnItems.value = new L.FeatureGroup()
    map.value.addLayer(drawnItems.value)

    // 配置绘制控件
    const drawOptions = {
        // position 可选值: 'topleft', 'topright', 'bottomleft', 'bottomright'
        position: 'topleft',
        draw: {
            // 明确设置每个工具的启用/禁用状态
            polyline: true,
            polygon: true,
            circle: false,      // 明确禁用圆形
            circlemarker: false, // 明确禁用圆形标记
            rectangle: true,
            marker: true,
        },
        edit: {
            featureGroup: drawnItems.value,
            remove: true
        }
    };

    // 单独配置每个绘制工具
    drawOptions.draw.polyline = {
        shapeOptions: {
            color: '#f357a1',
            weight: 3
        }
    };

    drawOptions.draw.polygon = {
        allowIntersection: false,
        drawError: {
            color: '#e1e100',
            message: '<strong>错误：</strong>多边形不能自相交！'
        },
        shapeOptions: {
            color: '#bada55',
            fillOpacity: 0.5
        }
    };

    drawOptions.draw.rectangle = {
        showArea: false,
        shapeOptions: {
            color: '#4a80f5',
            fill: false,
            weight: 5,
            clickable: true
        },
        repeatMode: false,
        metric: false
    };

    drawOptions.draw.marker = {
        icon: new L.Icon.Default(),
        repeatMode: true
    };

    // 创建绘制控件
    drawControl.value = new L.Control.Draw(drawOptions);

    map.value.addControl(drawControl.value)
}

// 在 script setup 中添加
const emit = defineEmits(['map-initialized'])

</script>

<style src="../styles/map-view.css"></style>
