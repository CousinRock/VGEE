<template>
    <div class="container">
        <!-- 传递整个 mapView 引用 -->
        <Header :map-view="mapView" />

        <!-- 左侧边栏预留 -->
        <div class="sidebar-left"></div>

        <!-- 中间地图区域 -->
        <MapView ref="mapView" />

        <!-- 右侧控制面板 -->
        <div class="sidebar-right">
            <ControlPanel @add-layer="handleAddLayer" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import MapView from './MapView.vue'
import ControlPanel from './ControlPanel.vue'
import Header from './Header.vue'

const mapView = ref(null)

// 监听 mapView 的变化
watch(() => mapView.value, (newMapView) => {
    if (newMapView) {
        console.log('MapView component updated:', {
            // object: Object.keys(newMapView)
            newMapView
        })
    }
}, { deep: true })

onMounted(() => {
    console.log('MapView component mounted:', mapView.value)
})

const handleAddLayer = ({ layerName, mapData }) => {
    mapView.value?.addNewLayer(layerName, mapData)
}
</script>

<style src="../styles/map.css"></style>
