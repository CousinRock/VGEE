<template>
    <div class="container">
        <!-- 左侧边栏预留 -->
        <div class="sidebar-left"></div>

        <!-- 中间地图区域 -->
        <div class="map-container">
            <div id="map"></div>

            <!-- 地图工具栏 -->
            <div class="map-tools">
                <div class="tool-group">
                    <div class="tool-button" @click="toggleLayerControl" :class="{ active: showLayerControl }"
                        title="图层">
                        <i class="fas fa-layer-group"></i>
                    </div>
                </div>

                <!-- 图层控制面板 -->
                <div class="layer-control" v-if="showLayerControl">
                    <div class="layer-item">
                        <input type="checkbox" v-model="baseLayerVisible" id="baseLayer">
                        <label for="baseLayer">
                            <i class="fas fa-map"></i>
                            <span>底图</span>
                        </label>
                    </div>

                    <!-- 动态图层列表 -->
                    <div class="layer-item" v-for="layer in layers" :key="layer.id">
                        <div class="layer-header">
                            <input type="checkbox" v-model="layer.visible" :id="layer.id">
                            <label :for="layer.id">
                                <i :class="layer.icon"></i>
                                <span>{{ layer.name }}</span>
                            </label>
                            <button class="remove-layer" @click="removeLayer(layer.id)" title="移除图层">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <input type="range" v-model="layer.opacity" min="0" max="1" step="0.1" class="opacity-slider"
                            v-if="layer.visible">
                    </div>
                </div>
            </div>
        </div>

        <!-- 右侧控制面板 -->
        <div class="sidebar-right">
            <div class="control-panel">
                <h3>遥感影像查询</h3>

                <div class="control-section">
                    <h4>数据源选择</h4>
                    <div class="control-item">
                        <select v-model="selectedImage" @change="changeImage">
                            <option value="LANDSAT">Landsat 8</option>
                            <option value="SENTINEL">Sentinel 2</option>
                            <option value="MODIS">MODIS</option>
                        </select>
                    </div>
                </div>

                <div class="control-section">
                    <h4>时间范围</h4>
                    <div class="control-item">
                        <label>开始日期</label>
                        <input type="date" v-model="startDate" :min="minDate" :max="endDate" @change="changeImage">
                    </div>

                    <div class="control-item">
                        <label>结束日期</label>
                        <input type="date" v-model="endDate" :min="startDate" :max="maxDate" @change="changeImage">
                    </div>
                </div>

                <div class="control-section">
                    <h4>云量设置</h4>
                    <div class="control-item">
                        <div class="range-container">
                            <input type="range" v-model="cloudCover" min="0" max="100" step="5" @change="changeImage">
                            <span class="range-value">{{ cloudCover }}%</span>
                        </div>
                    </div>
                </div>

                <div class="control-section">
                    <h4>图层设置</h4>
                    <div class="control-item">
                        <label>图层名称</label>
                        <input type="text" v-model="layerName" placeholder="请输入图层名称" class="layer-name-input">
                    </div>
                    <div class="control-item">
                        <button class="add-layer-btn" @click="addNewLayer" :disabled="!layerName.trim()">
                            <i class="fas fa-plus"></i>
                            添加图层
                        </button>
                    </div>
                </div>


            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import '../styles/map.css'
// 引入Font Awesome图标
import '@fortawesome/fontawesome-free/css/all.css'

// 添加layers的定义
const layers = ref([])

// 修改其他变量定义
const selectedImage = ref('LANDSAT')
const cloudCover = ref(20)
const showLayerControl = ref(false)
const baseLayerVisible = ref(true)
const layerName = ref('')

let map = null
let baseLayer = null

// 移除不需要的变量
// const satelliteLayerVisible = ref(true)
// const satelliteLayerOpacity = ref(1)
// let overlayLayer = null

// 日期控制
const currentYear = new Date().getFullYear()
const minDate = ref(`2000-01-01`)
const maxDate = ref(`${currentYear}-12-31`)
const startDate = ref(`${currentYear}-01-01`)
const endDate = ref(`${currentYear}-12-31`)

// 格式化日期显示
const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

// 修改changeImage函数，移除自动添加图层的逻辑
const changeImage = async () => {
    try {
        const params = new URLSearchParams({
            satellite: selectedImage.value,
            startDate: startDate.value,
            endDate: endDate.value,
            cloudCover: cloudCover.value
        })

        const response = await fetch(`http://localhost:5000/map-data?${params}`)
        const mapData = await response.json()

        if (!mapData?.overlayLayers?.length) {
            alert('未找到符合条件的影像数据')
            return
        }

        window.currentMapData = mapData

    } catch (error) {
        console.error('Error changing image:', error)
        alert('获取影像数据失败，请重试')
    }
}

// 修改addNewLayer函数
const addNewLayer = async () => {
    try {
        const mapData = window.currentMapData

        if (!mapData?.overlayLayers?.length) {
            alert('未找到符合条件的影像数据')
            return
        }

        mapData.overlayLayers.forEach(layerData => {
            const newLayer = {
                id: `layer-${Date.now()}`,
                name: layerName.value,
                icon: 'fas fa-satellite',
                visible: true,
                opacity: 1,
                leafletLayer: null,
                zIndex: 1000 + layers.value.length
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
                zIndex: newLayer.zIndex
            })

            // 添加到地图和图层列表
            newLayer.leafletLayer.addTo(map)
            // 将新图层添加到数组末尾，确保在列表中显示在最下方
            layers.value.push(newLayer)
        })

        layerName.value = ''

        // 更新图层顺序
        updateLayerOrder()
    } catch (error) {
        console.error('Error adding layer:', error)
        alert('添加图层失败，请重试')
    }
}

// 添加移除图层的函数
const removeLayer = (layerId) => {
    const layerIndex = layers.value.findIndex(l => l.id === layerId)
    if (layerIndex > -1) {
        const layer = layers.value[layerIndex]
        if (layer.leafletLayer && map) {
            map.removeLayer(layer.leafletLayer)
        }
        layers.value.splice(layerIndex, 1)
    }
}

// 修改图层可见性监听器
watch(layers, (newLayers) => {
    nextTick(() => {  // 使用nextTick避免递归更新
        newLayers.forEach(layer => {
            if (layer.leafletLayer) {
                layer.leafletLayer.setOpacity(layer.opacity)
                if (layer.visible) {
                    layer.leafletLayer.addTo(map)
                    layer.leafletLayer.setZIndex(1000 + newLayers.indexOf(layer))  // 设置图层顺序
                } else {
                    layer.leafletLayer.remove()
                }
            }
        })
    })
}, { deep: true })

// 切换图层控制面板显示
const toggleLayerControl = () => {
    showLayerControl.value = !showLayerControl.value
}

// 修改baseLayerVisible的监听器
watch(baseLayerVisible, (newValue) => {
    nextTick(() => {  // 使用nextTick避免递归更新
        if (baseLayer) {
            if (newValue) {
                baseLayer.addTo(map)
                baseLayer.setZIndex(0)  // 底图永远在最底层

            } else {
                baseLayer.remove()
            }
        }
    })
})

// 修改onMounted函数，确保底图在最底层
onMounted(async () => {
    try {
        const response = await fetch(`http://localhost:5000/map-data`)
        const mapData = await response.json()

        map = L.map('map', {
            center: mapData.center,
            zoom: mapData.zoom,
            zoomAnimation: true,
            fadeAnimation: true,
            preferCanvas: true
        })

        // 添加底图并设置最低层级
        baseLayer = L.tileLayer(mapData.baseLayer.url, {
            subdomains: mapData.baseLayer.subdomains,
            attribution: mapData.baseLayer.attribution,
            maxZoom: 20,
            maxNativeZoom: 20,
            tileSize: 256,
            zIndex: 0  // 底图永远在最底层
        }).addTo(map)

    } catch (error) {
        console.error('Error loading map:', error)
    }
})

// 修改updateLayerOrder函数
const updateLayerOrder = () => {
    layers.value.forEach((layer, index) => {
        if (layer.leafletLayer && layer.visible) {
            const zIndex = 1000 + index
            layer.leafletLayer.setZIndex(zIndex)
        }
    })
}

// 在图层可见性改变时更新顺序
watch(() => layers.value.map(l => l.visible), () => {
    nextTick(updateLayerOrder)
}, { deep: true })
</script>