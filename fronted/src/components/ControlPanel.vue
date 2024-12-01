<template>
    <div class="control-panel">
        <h3>遥感影像查询</h3>

        <div class="control-section">
            <h4>数据源选择</h4>
            <div class="control-item">
                <select v-model="selectedImage">
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
                <input type="date" v-model="startDate" :min="minDate" :max="endDate">
            </div>

            <div class="control-item">
                <label>结束日期</label>
                <input type="date" v-model="endDate" :min="startDate" :max="maxDate">
            </div>
        </div>

        <div class="control-section">
            <h4>云量设置</h4>
            <div class="control-item">
                <div class="range-container">
                    <input type="range" v-model="cloudCover" min="0" max="100" step="5">
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
</template>

<script setup>
import { ref } from 'vue'

// 定义emit事件 'add-layer' 用于向父组件 Map.vue 发送添加新图层的事件
// 当用户点击添加图层按钮时,会触发此事件并传递图层名称和地图数据
// Map.vue 中的 handleAddLayer 方法会接收这些数据并调用 MapView 组件的 addNewLayer 方法来实际添加图层
const emit = defineEmits(['add-layer'])

// 日期控制
const currentYear = new Date().getFullYear()
const minDate = ref(`2000-01-01`)
const maxDate = ref(`${currentYear}-12-31`)
const startDate = ref(`${currentYear}-01-01`)
const endDate = ref(`${currentYear}-12-31`)

// 其他变量
const selectedImage = ref('LANDSAT')
const cloudCover = ref(20)
const layerName = ref('')

// 添加新图层
const addNewLayer = async () => {
    if (!layerName.value || !layerName.value.trim()) {
        alert('请输入图层名称')
        return
    }

    try {
        // 添加加载状态
        const addButton = document.querySelector('.add-layer-btn')
        if (addButton) {
            addButton.disabled = true
            addButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 添加中...'
        }

        // 每次添加图层时都重新获取地图数据
        const params = new URLSearchParams({
            satellite: selectedImage.value,
            startDate: startDate.value,
            endDate: endDate.value,
            cloudCover: cloudCover.value,
            layerName: layerName.value,
            _t: Date.now()
        })

        const response = await fetch(`http://localhost:5000/map-data?${params}`)
        const mapData = await response.json()
        console.log('ControlPanel.vue - mapData:', mapData);
        if (!mapData?.overlayLayers?.length) {
            alert('未找到符合条件的影像数据')
            return
        }

        emit('add-layer', {
            layerName: layerName.value,
            mapData: mapData
        })
        layerName.value = ''

    } catch (error) {
        console.error('ControlPanel.vue - Error adding layer:', error)
        alert('添加图层失败，请重试')
    } finally {
        // 恢复按钮状态
        const addButton = document.querySelector('.add-layer-btn')
        if (addButton) {
            addButton.disabled = false
            addButton.innerHTML = '<i class="fas fa-plus"></i> 添加图层'
        }
    }
}
</script>

<style src="../styles/control-panel.css"></style>