<template>
    <div class="control-panel">
        <h3>遥感影像查询</h3>

        <div class="control-section">
            <h4>卫星选择</h4>
            <div class="control-item">
                <el-select v-model="satellite" placeholder="选择卫星" @change="handleSatelliteChange">
                    <el-option-group v-for="group in satelliteOptions" :key="group.label" :label="group.label">
                        <el-option v-for="item in group.options" :key="item.value" :label="item.label"
                            :value="item.value" />
                    </el-option-group>
                </el-select>
            </div>
        </div>

        <div class="control-section">
            <h4>时间范围</h4>
            <div class="date-range-info">
                {{ getDateRangeText }}
            </div>
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
import { ref, computed, onMounted } from 'vue'
import { API_ROUTES } from '../api/routes'

// 定义emit事件 'add-layer' 用于向父组件 Map.vue 发送添加新图层的事件
// 当用户点击添加图层按钮时,会触发此事件并传递图层名称和地图数据
// Map.vue 中的 handleAddLayer 方法会接收这些数据并调用 MapView 组件的 addNewLayer 方法来实际添加图层
const emit = defineEmits(['add-layer', 'update-map'])

// 日期控制
const currentYear = new Date().getFullYear()
const minDate = ref(`2000-01-01`)
const maxDate = ref(`${currentYear}-12-31`)
const startDate = ref(`${currentYear}-01-01`)
const endDate = ref(`${currentYear}-12-31`)

// 其他变量
const satellite = ref([])  // 默认选择
const satelliteOptions = ref([])


const cloudCover = ref(20)
const layerName = ref('')

// 获取卫星配置
const fetchSatelliteConfig = async () => {
    try {
        const response = await fetch(API_ROUTES.MAP.GET_SATELLITE_CONFIG)
        const data = await response.json()
        if (data.success) {
            satelliteOptions.value = data.satelliteOptions
        } else {
            console.error('Failed to get satellite config:', data.message)
        }
    } catch (error) {
        console.error('Error fetching satellite config:', error)
    }
}

// 在组件挂载时获取配置
onMounted(() => {
    fetchSatelliteConfig()
})

// 修改计算属性以使用后端数据
const getDateRangeText = computed(() => {
    const satelliteConfig = satelliteOptions.value
        .flatMap(group => group.options)
        .find(option => option.value === satellite.value)
        
    if (!satelliteConfig) return ''
    
    const startDate = satelliteConfig.startDate || '未知'
    const endDate = satelliteConfig.endDate || '至今'
    
    return `${startDate} 至 ${endDate}`
})

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
            satellite: satellite.value,
            startDate: startDate.value,
            endDate: endDate.value,
            cloudCover: cloudCover.value,
            layerName: layerName.value,
            _t: Date.now()
        })

        const response = await fetch(`${API_ROUTES.MAP.GET_MAP_DATA}?${params}`)
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

// 处理卫星选择变化
const handleSatelliteChange = (value) => {
    // 触发更新地图
    emit('update-map', {
        satellite: value,
        startDate: startDate.value,
        endDate: endDate.value,
        cloudCover: cloudCover.value
    })
}

// 导出属性供父组件使用
defineExpose({
    satellite,
    startDate,
    endDate,
    cloudCover
})
</script>

<style src="../styles/control-panel.css"></style>