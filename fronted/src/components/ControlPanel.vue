<template>
    <div class="control-panel">
        <h3>Remote Sensing Image Query</h3>

        <div class="control-section">
            <h4>Satellite Selection</h4>
            <div class="control-item">
                <el-select v-model="satellite" placeholder="Select Dataset" @change="handleSatelliteChange">
                    <el-option-group v-for="group in satelliteOptions" :key="group.label" :label="group.label">
                        <el-option v-for="item in group.options" :key="item.value" :label="item.label"
                            :value="item.value" />
                    </el-option-group>
                </el-select>
                <div v-if="selectedSatelliteInfo" class="selected-satellite-info">
                    <el-tag size="small" :type="getTypeTagType(selectedSatelliteInfo.type)">
                        {{ formatType(selectedSatelliteInfo.type) }}
                    </el-tag>
                </div>
            </div>
        </div>

        <div class="control-section">
            <h4>Time Range</h4>
            <div class="date-range-info">
                {{ getDateRangeText }}
            </div>
            <div class="control-item">
                <label>Start Date</label>
                <input type="date" v-model="startDate" :min="minDate" :max="endDate">
            </div>

            <div class="control-item">
                <label>End Date</label>
                <input type="date" v-model="endDate" :min="startDate" :max="maxDate">
            </div>
        </div>

        <div class="control-section">
            <h4>Composite Method</h4>
            <div class="control-item">
                <el-select v-model="compositeMethod" placeholder="Select Composite Method">
                    <el-option v-for="item in compositeMethods" :key="item.value" :label="item.label"
                        :value="item.value" />
                </el-select>
            </div>
        </div>

        <div class="control-section">
            <h4>Cloud Cover Settings</h4>
            <div class="control-item">
                <div class="range-container">
                    <input type="range" v-model="cloudCover" min="0" max="100" step="5">
                    <span class="range-value">{{ cloudCover }}%</span>
                </div>
            </div>
        </div>

        <div class="control-section">
            <h4>Layer Settings</h4>
            <div class="control-item">
                <label>Layer Name</label>
                <input type="text" v-model="layerName" placeholder="Please enter the layer name"
                    class="layer-name-input">
            </div>
            <div class="control-item">
                <button class="add-layer-btn" @click="addNewLayer" :disabled="!layerName.trim()">
                    <i class="fas fa-plus"></i>
                    Add Layer
                </button>
            </div>
        </div>

        <div v-for="layer in layers" :key="layer.id" class="layer-item">
            <div class="layer-controls">
                <div class="vis-params-control">
                    <el-form-item label="Display Range">
                        <el-input-number v-model="layer.visParams.min" :step="0.1" @change="updateLayer(layer)" />
                        <el-input-number v-model="layer.visParams.max" :step="0.1" @change="updateLayer(layer)" />
                    </el-form-item>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { API_ROUTES } from '../api/routes'
import eventBus from '../util/eventBus'
import { ElMessage } from 'element-plus'
import { satelliteManager } from '../service/controlPanel'

// 定义emit事件 'add-layer' 用于向父组件 Map.vue 发送添加新图层的事件
// 当用户点击添加图层按钮时,会触发此事件并传递图层名称和地图数据
// Map.vue 中的 handleAddLayer 方法会接收这些数据并调用 MapView 组件的 addNewLayer 方法来实际添加图层
const emit = defineEmits(['add-layer', 'update-map', 'dataset-selected'])

// 日期控制
const currentYear = new Date().getFullYear()
const minDate = ref(`2000-01-01`)
const maxDate = ref(`${currentYear}-12-31`)
const startDate = ref(`${currentYear - 1}-01-01`)
const endDate = ref(`${currentYear - 1}-12-31`)

// 其他变量
const satellite = ref(null)
const satelliteOptions = ref([])

const cloudCover = ref(20)
const layerName = ref('')

// 添加合成方式选项
const compositeMethods = [
    { label: 'median', value: 'median' },
    { label: 'mean', value: 'mean' },
    { label: 'max', value: 'max' },
    { label: 'min', value: 'min' },
    { label: 'first', value: 'first' }
]
const compositeMethod = ref('median') // 默认使用中值

// 获取卫星配置
const fetchSatelliteConfig = async () => {
    satelliteOptions.value = await satelliteManager.satelliteConfig()
    console.log('ControlPanel.vue - satelliteOptions:', satelliteOptions.value)
}

// 在组件挂载时获取配置
onMounted(() => {
    fetchSatelliteConfig()

    // 监听事件总线的事件
    eventBus.on('dataset-selected', (dataset) => {
        console.log('ControlPanel.vue - Received dataset:', dataset)
        satelliteManager.addDataToSatelliteConfig(dataset, satelliteOptions)

    })
})

// 在组件卸载时移除事件监听
onUnmounted(() => {
    eventBus.off('dataset-selected')
})

// 修改计算属性以使用后端数据
const getDateRangeText = computed(() => {
    const satelliteConfig = satelliteOptions.value
        .flatMap(group => group.options)
        .find(option => option.value === satellite.value)

    if (!satelliteConfig) return ''

    const startDate = satelliteConfig.startDate || 'Unknown'
    const endDate = satelliteConfig.endDate || 'Now'

    return `${startDate} - ${endDate}`
})

// 添加新图层
const addNewLayer = async () => {
    if (!layerName.value || !layerName.value.trim()) {
        alert('Please enter the layer name')
        return
    }
    console.log('ControlPanel.vue - satellite:', satellite.value)

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
            compositeMethod: compositeMethod.value, // 添加合成方式参数
            type: selectedSatelliteInfo.value.type,
            _t: Date.now()
        })

        const response = await fetch(`${API_ROUTES.MAP.GET_MAP_DATA}?${params}`)
        const mapData = await response.json()
        console.log('ControlPanel.vue - mapData:', mapData);
        if (!mapData?.overlayLayers?.length) {
            alert('No matching image data found')
            return
        }

        emit('add-layer', {
            layerName: layerName.value,
            mapData: mapData
        })
        layerName.value = ''

    } catch (error) {
        console.error('ControlPanel.vue - Error adding layer:', error)
        alert('Failed to add layer, please try again')
    } finally {
        // 恢复按钮状态
        const addButton = document.querySelector('.add-layer-btn')
        if (addButton) {
            addButton.disabled = false
            addButton.innerHTML = '<i class="fas fa-plus"></i> Add Layer'
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

// 添加数据类型格式化函数
const formatType = (type) => {
    const typeMap = {
        'image_collection': 'Image Collection',
        'image': 'Image',
        'feature_collection': 'Feature Collection',
        'feature': 'Feature'
    }
    return typeMap[type] || type
}

// 添加标签类型函数
const getTypeTagType = (type) => {
    const typeTagMap = {
        'image_collection': 'success',
        'image': 'primary',
        'feature_collection': 'warning',
        'feature': 'info'
    }
    return typeTagMap[type] || ''
}

// 添加计算属性获取选中卫星的信息
const selectedSatelliteInfo = computed(() => {
    return satelliteOptions.value
        .flatMap(group => group.options)
        .find(option => option.value === satellite.value)
})

// 导出属性供父组件使用
defineExpose({
    satellite,
    startDate,
    endDate,
    cloudCover
})
</script>

<style src="../styles/control-panel.css"></style>