<template>
    <div class="container">
        <Header :map-view="mapView" />

        <!-- 左侧边栏预留 -->
        <div class="sidebar-left"></div>

        <!-- 中间地图区域 -->
        <MapView ref="mapView" @map-initialized="onMapInitialized" />

        <!-- 右侧控制面板 -->
        <div class="sidebar-right">
            <ControlPanel @add-layer="handleAddLayer" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MapView from './MapView.vue'
import ControlPanel from './ControlPanel.vue'
import Header from './Header.vue'

const mapView = ref(null)

// 添加地图初始化完成的处理函数
const onMapInitialized = (mapInstance) => {
    console.log('Map initialized:', mapInstance)
    // 确保 mapView 已经获取到了实例
    if (mapView.value) {
        mapView.value.map = mapInstance
    }
}

onMounted(() => {
    console.log('Map.vue - MapView component mounted:', mapView.value)
})

const handleAddLayer = ({ layerName, mapData }) => {
    mapView.value?.addNewLayer(layerName, mapData)
}
</script>

<style src="../styles/map.css"></style>
