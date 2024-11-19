<template>
    <div class="container">
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
import { ref } from 'vue'
import MapView from './MapView.vue'
import ControlPanel from './ControlPanel.vue'

const mapView = ref(null)

const handleAddLayer = ({ layerName, mapData }) => {
    mapView.value.addNewLayer(layerName, mapData)
}
</script>

<style src="../styles/map.css"></style>
