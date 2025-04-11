<template>
  <div class="tif2vector-settings">
    <h3>Raster to Vector Settings</h3>
    
    <!-- 比例尺设置 -->
    <div class="setting-item">
      <span class="setting-label">Scale (meters):</span>
      <el-input-number 
        v-model="params.scale" 
        :min="10"
        :max="1000"
        :step="10"
        size="small"
      />
      <div class="setting-hint">Resolution of analysis (10-1000m)</div>
    </div>

    <!-- 几何类型选择 -->
    <div class="setting-item">
      <span class="setting-label">Geometry Type:</span>
      <el-select 
        v-model="params.geometryType" 
        placeholder="Select geometry type"
        size="small"
      >
        <el-option label="Polygon" value="polygon" />
        <el-option label="Bounding Box" value="bb" />
        <el-option label="Centroid" value="centroid" />
      </el-select>
      <div class="setting-hint">Type of output geometry</div>
    </div>

    <!-- 连接方式设置 -->
    <div class="setting-item">
      <span class="setting-label">Connection Type:</span>
      <el-switch
        v-model="params.eightConnected"
        active-text="8-connected"
        inactive-text="4-connected"
      />
      <div class="setting-hint">How pixels are considered connected</div>
    </div>

    <!-- 最大像素数设置 -->
    <div class="setting-item">
      <span class="setting-label">Max Pixels:</span>
      <el-input-number 
        v-model="params.maxPixels" 
        :min="1000"
        :max="10000000000000000000"
        :step="1000"
        size="small"
      />
      <div class="setting-hint">Maximum number of pixels to process</div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  selectedLayerName: {
    type: Array,
    required: true
  },
  layerBands: {
    type: Object,
    required: true
  }
})

// 参数设置
const params = ref({
  scale: 10,      // 默认30米分辨率
  geometryType: 'polygon',  // 默认多边形
  eightConnected: true,  // 默认8连通
  maxPixels: 10000000,  // 默认最大像素数
})

// 计算可用的波段
const availableBands = computed(() => {
  if (!props.selectedLayerName || !props.layerBands) return []
  
  // 如果只选择了一个图层，返回该图层的所有波段
  if (props.selectedLayerName.length === 1) {
    return props.layerBands[props.selectedLayerName[0]] || []
  }
  
  // 如果选择了多个图层，返回所有图层共有的波段
  return props.selectedLayerName.reduce((commonBands, layerId) => {
    const layerBands = props.layerBands[layerId] || []
    if (commonBands.length === 0) return layerBands
    return commonBands.filter(band => layerBands.includes(band))
  }, [])
})

// 监听选中图层变化，重置波段选择
watch(() => props.selectedLayerName, () => {
  params.value.band = null
}, { deep: true })

// 获取参数方法
const getParams = () => {
  // 为每个选中的图层创建参数
  const parameters = {}
  props.selectedLayerName.forEach(layerId => {
    parameters[layerId] = {
      scale: params.value.scale,
      geometryType: params.value.geometryType,
      eightConnected: params.value.eightConnected,
      maxPixels: params.value.maxPixels,
      band: params.value.band
    }
  })
  
  return parameters
}

// 暴露方法给父组件
defineExpose({
  getParams
})
</script>

<style scoped>
.tif2vector-settings {
  padding: 20px;
}

.setting-item {
  margin-bottom: 20px;
}

.setting-label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.setting-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #666;
}

.el-input-number {
  width: 180px;
}

.el-select {
  width: 180px;
}
</style>