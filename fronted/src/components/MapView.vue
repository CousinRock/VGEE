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
</template>

<script setup>
import { onMounted, ref, watch, nextTick } from 'vue'
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

let map = null
let baseLayer = null

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

        mapData.overlayLayers.forEach(layerData => {
            const newLayer = {
                id: `layer-${Date.now()}`,
                name: layerName,
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
            layers.value.push(newLayer)
        })

        // 更新图层顺序
        updateLayerOrder()
    } catch (error) {
        console.error('Error adding layer:', error)
        alert('添加图层失败，请重试')
    }
}

// 移除图层
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

// 监听图层变化
watch(layers, (newLayers) => {
    nextTick(() => {
        newLayers.forEach(layer => {
            if (layer.leafletLayer) {
                layer.leafletLayer.setOpacity(layer.opacity)
                if (layer.visible) {
                    layer.leafletLayer.addTo(map)
                    layer.leafletLayer.setZIndex(1000 + newLayers.indexOf(layer))
                } else {
                    layer.leafletLayer.remove()
                }
            }
        })
    })
}, { deep: true })

// 监听底图可见性
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
            preferCanvas: true
        })

        baseLayer = L.tileLayer(mapData.baseLayer.url, {
            subdomains: mapData.baseLayer.subdomains,
            attribution: mapData.baseLayer.attribution,
            maxZoom: 20,
            maxNativeZoom: 20,
            tileSize: 256,
            zIndex: 0
        }).addTo(map)

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
</script>

<style src="../styles/map-view.css"></style>