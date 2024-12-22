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
                            <template v-if="layer.type === 'vector'">
                                <el-dropdown trigger="click" :teleported="false">
                                    <button class="layer-settings" title="图层设置" tabindex="0">
                                        <i class="fas fa-cog"></i>
                                    </button>
                                    <template #dropdown>
                                        <el-dropdown-menu>
                                            <el-dropdown-item @click="toggleStudyArea(layer)" tabindex="0">
                                                <i :class="layer.isStudyArea ? 'el-icon-check' : 'el-icon-crop'"></i>
                                                {{ layer.isStudyArea ? '取消研究区域' : '设为研究区域' }}
                                            </el-dropdown-item>
                                            <el-dropdown-item @click="openVectorStyleSettings(layer)" tabindex="0">
                                                <i class="el-icon-setting"></i>
                                                样式设置
                                            </el-dropdown-item>
                                        </el-dropdown-menu>
                                    </template>
                                </el-dropdown>
                            </template>
                            <template v-else>
                                <button class="layer-settings" @click="openLayerSettings(layer)" title="图层设置">
                                    <i class="fas fa-cog"></i>
                                </button>
                            </template>
                            <button class="remove-layer" @click="removeLayer(layer.id)" title="移除图层">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <input type="range" v-model="layer.opacity" min="0" max="1" step="0.1" class="opacity-slider"
                        v-if="layer.visible">
                </div>
            </div>
        </div>

        <!-- 底图设置对话框 -->
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
                        <el-select v-model="selectedPalette" style="width: 100%;"
                            popper-class="palette-select-dropdown">
                            <el-option v-for="(colors, name) in palettes" :key="name" :label="name" :value="name">
                                <div class="palette-preview-item">
                                    <div class="palette-preview" :style="getPalettePreviewStyle(colors)"></div>
                                    <span>{{ name }}</span>
                                </div>
                            </el-option>
                        </el-select>
                    </div>
                </div>

                <!-- 多波段选择区域 -->
                <div class="band-selection" v-else>
                    <!-- 原有的RGB波段选择不变 -->
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
                    <el-slider v-model="visParams.range" range :min="currentLayer.min" :max="currentLayer.max"
                        :step="getSliderStep(currentLayer.satellite)" :format-tooltip="val => formatSliderValue(val)"
                        @change="handleRangeChange" />
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

        <!-- 添加矢量样式设置对话框 -->
        <el-dialog v-model="showVectorStyleDialog" title="矢量图层样式设置" width="400px">
            <div class="vector-style-settings">
                <div class="style-item">
                    <span>边框颜色</span>
                    <el-color-picker v-model="vectorStyle.color" show-alpha popper-class="color-picker-popper" />
                </div>
                <div class="style-item">
                    <span>边框宽度</span>
                    <el-slider v-model="vectorStyle.weight" :min="1" :max="5" :step="0.5" />
                </div>
                <div class="style-item">
                    <span>边框透明度</span>
                    <el-slider v-model="vectorStyle.opacity" :min="0" :max="1" :step="0.1" />
                </div>
                <div class="style-item">
                    <span>填充透明度</span>
                    <el-slider v-model="vectorStyle.fillOpacity" :min="0" :max="1" :step="0.1" />
                </div>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showVectorStyleDialog = false">取消</el-button>
                    <el-button type="primary" @click="applyVectorStyle">确定</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick, reactive, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
// 引入底图配置
import { baseMaps, palettes } from '../config/map-config'
import { normalizeRange, layerChangeRemove } from '../util/methods'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import '@fortawesome/fontawesome-free/css/all.css'
import 'leaflet-draw'
import 'leaflet-draw/dist/leaflet.draw.css'
import { API_ROUTES } from '../api/routes'

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

// 添加绘制控制相关的状态
const drawnItems = ref(null)
const drawControl = ref(null)

// 添加新的状态变量
const showVectorStyleDialog = ref(false)
const currentVectorLayer = ref(null)
const vectorStyle = ref({
    color: '#3388ff',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.2
})



// 切换图层控制面板显示
const toggleLayerControl = () => {
    showLayerControl.value = !showLayerControl.value
}

// 添加新图层
const addNewLayer = async (layerName, mapData) => {
    try {
        if (!mapData?.overlayLayers?.length) {
            alert('未找符合条件的影像数据')
            return
        }

        console.log('MapView.vue - addNewLayer - mapData:', mapData.overlayLayers[0].id);
        // 1. 预取波段信息并缓存
        const response = await fetch(`${API_ROUTES.LAYER.GET_LAYER_INFO}?id=${mapData.overlayLayers[0].id}&satellite=${mapData.satellite}`)
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
                defaultBands = ['NDVI']  // MODIS 默认示 NDVI
                break
            default:
                defaultBands = layerInfo.bands.slice(0, 3)  // 默认使用前三个波段
        }

        // 3. 为每个图层创建新的图层对
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

            // 5. 添加到地图图层数组
            newLayer.leafletLayer.addTo(map.value)
            layers.value.push(newLayer)
            console.log('MapView.vue - newLayer.visParams:', newLayer.visParams);
        })

        index += 1

        // 更新图层顺序
        updateLayerOrder()
    } catch (error) {
        console.error('MapView.vue - Error adding layer:', error)
        alert('添加图层失败，请重试')
    }
}

// 移除选定的图层
const removeLayer = async (layerId) => {
    if (!map.value) return;

    try {
        // 先调用后端移除数据集中的图层
        const response = await fetch(API_ROUTES.MAP.REMOVE_LAYER, {
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

        // 找到要移除的图层
        const layer = layers.value.find(l => l.id === layerId);
        if (layer && layer.leafletLayer) {
            // 从地图中移除图层
            if (map.value.hasLayer(layer.leafletLayer)) {
                map.value.removeLayer(layer.leafletLayer);
            }
        }

        // 从数组中移除图层
        const layerIndex = layers.value.findIndex(l => l.id === layerId);
        if (layerIndex > -1) {
            layers.value.splice(layerIndex, 1);
        }
    } catch (error) {
        console.error('MapView.vue - Error removing layer:', error);
        ElMessage.error('移除图层失败');
    }
};


// 取滑块步长和范围
const getSliderStep = (satelliteType) => {
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
const formatSliderValue = (value) => {
    if (!currentLayer.value) return value.toFixed(3);

    switch (currentLayer.value.satellite) {
        case 'SENTINEL-2':
            return Math.round(value);  // 整数显示
        case 'MODIS-NDVI':
            return Math.round(value);  // 整数显���
        case 'LANDSAT-8':
        case 'LANDSAT-7':
        case 'LANDSAT-5':
            return value.toFixed(3);  // 显示3位小数
        default:
            return value.toFixed(3);
    }
}

// 添加防抖函数,防止缩放移动时图层卡死
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
                if (layer.type === 'vector') {
                    if (layer.visible) {
                        if (!map.value.hasLayer(layer.leafletLayer)) {
                            layer.leafletLayer.addTo(map.value)
                        }
                        // 使用保存的样式
                        if (layer.vectorStyle) {
                            layer.leafletLayer.setStyle({
                                ...layer.vectorStyle,
                                opacity: layer.opacity,
                                fillOpacity: layer.opacity * layer.vectorStyle.fillOpacity
                            })
                        }
                    } else {
                        if (map.value.hasLayer(layer.leafletLayer)) {
                            map.value.removeLayer(layer.leafletLayer)
                        }
                    }
                } else {
                    // 对于栅格图层，使用 setOpacity
                    layer.leafletLayer.setOpacity(layer.opacity)

                    if (layer.visible) {
                        if (!map.value.hasLayer(layer.leafletLayer)) {
                            layer.leafletLayer.addTo(map.value)
                        }
                        layer.leafletLayer.setZIndex(1000 + newLayers.indexOf(layer))
                    } else {
                        // 如果图层应该隐藏遍历查找并移除
                        layerChangeRemove(map.value, layer.leafletLayer)
                    }
                }
            }
        })
    })
}, 100), { deep: true })



// 修改 changeBaseMap 函数
const changeBaseMap = () => {
    // 正确移除旧底图
    if (baseLayer) {
        layerChangeRemove(map.value, baseLayer)
        baseLayer = null
    }

    // 创建新底图
    const selectedMap = baseMaps.find(m => m.id === selectedBaseMap.value)
    if (selectedMap) {
        // 处理普通瓦片服务
        baseLayer = L.tileLayer(selectedMap.url, {
            subdomains: selectedMap.subdomains || 'abc',
            attribution: selectedMap.attribution,
            maxZoom: 20,
            maxNativeZoom: 20
        })

        if (baseLayerVisible.value) {
            baseLayer.addTo(map.value)
            baseLayer.setZIndex(0)
        }
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
        // 创建地图实例时直接赋给 ref
        map.value = L.map('map', {
            center: [20, 0],
            zoom: 3,
            zoomAnimation: true,
            fadeAnimation: true,
            preferCanvas: true,
            wheelDebounceTime: 150,
            wheelPxPerZoomLevel: 120,
            // 添加投影关配置
            crs: L.CRS.EPSG3857,  // 明确定投影系统
            continuousWorld: true, // 确保连续的世界地图
            worldCopyJump: true,   // 允许在经度方向
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
            // 禁用所有图层的画
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
                const response = await fetch(API_ROUTES.MAP.FILTER_BY_GEOMETRY, {
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

        // 修改删除事监听
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
                const response = await fetch(API_ROUTES.MAP.REMOVE_GEOMETRY, {
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

        // 触发初化完成事件
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

// 添加范围变化处理函数
const handleRangeChange = (value) => {
    // 确保范围不超出限制
    visParams.range = [
        Math.max(value[0], currentLayer.value.min),
        Math.min(value[1], currentLayer.value.max)
    ];
};

// 修改打开层设置方法
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
            Object.assign(visParams, {
                bands: [...layer.visParams.bands],
                min: layer.visParams.min,
                max: layer.visParams.max,
                // 确保范围在限制内
                range: [
                    Math.max(layer.visParams.min, layer.min),
                    Math.min(layer.visParams.max, layer.max)
                ],
                gamma: layer.visParams.gamma || 1.4
            })

            showLayerSettings.value = true
            return
        }
        else {
            console.log('MapView.vue - openLayerSettings - no bandInfo:', layer);
        }

    } catch (error) {
        console.error('MapView.vue - Error opening layer settings:', error)
        ElMessage.error('获取波段信息失败')
    }
}

// 修改更新围函数
const updateRangeBasedOnBands = async (vis) => {
    try {
        if (!currentLayer.value) return;

        // 添加加载状态到 Apply 按钮
        const applyButton = document.querySelector('.el-dialog__body .button-group .el-button--primary')
        if (applyButton) {
            applyButton.disabled = true
            applyButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 计算中...'
        }

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
                // 先移除旧图层
                if (layer.leafletLayer) {
                    layerChangeRemove(map.value, layer.leafletLayer)
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

    console.log('MapView-watch', visParams);

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

    // 清理图
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
            // 明确置每个工具的启用/禁用状态
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

    // 单独配置每个绘制具
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
            message: '<strong>误：</strong>多边形不自相交！'
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

// 添加获取调色板预览样的方法
const getPalettePreviewStyle = (colors) => {
    return {
        background: `linear-gradient(to right, ${colors.join(',')})`
    }
}

// 添加矢量图层相关方法
const toggleStudyArea = async (layer) => {
    try {
        if (layer.isStudyArea) {
            // 取消研究区域
            await fetch(API_ROUTES.MAP.REMOVE_GEOMETRY, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    asset_id: layer.id,
                    type: 'vector'
                })
            })
            layer.isStudyArea = false
            ElMessage.success(`已取消${layer.name}研究区域设置`)
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
            ElMessage.success(`已设置${layer.name}为研究区域`)
        }
    } catch (error) {
        console.error('Error toggling study area:', error)
        ElMessage.error('设置研究区域失败')
    }
}

const openVectorStyleSettings = (layer) => {
    currentVectorLayer.value = layer

    // 获取当前图层的样式
    const style = layer.leafletLayer.options.style || {};


    // 设置当前样式值
    vectorStyle.value.color = style.color || '#3388ff'
    vectorStyle.value.weight = style.weight
    vectorStyle.value.opacity = style.opacity
    vectorStyle.value.fillOpacity = style.fillOpacity

    showVectorStyleDialog.value = true
}

const applyVectorStyle = () => {
    if (!currentVectorLayer.value) return

    // 直接设置图层样式
    currentVectorLayer.value.leafletLayer.setStyle({
        color: vectorStyle.value.color,
        weight: vectorStyle.value.weight,
        opacity: vectorStyle.value.opacity,
        fillOpacity: vectorStyle.value.fillOpacity
    })

    // 保存当前样式到图层选项中
    currentVectorLayer.value.leafletLayer.options.style = {
        color: vectorStyle.value.color,
        weight: vectorStyle.value.weight,
        opacity: vectorStyle.value.opacity,
        fillOpacity: vectorStyle.value.fillOpacity
    }

    showVectorStyleDialog.value = false
    ElMessage.success('样式已更新')
}
</script>

<style src="../styles/map-view.css"></style>