<template>
  <div class="canny-settings">
    <h3>Canny Edge Detection Settings</h3>
    
    <!-- 阈值设置 -->
    <div class="setting-item">
      <span class="setting-label">Threshold:</span>
      <el-input-number 
        v-model="cannyParams.threshold" 
        :min="0"
        :max="1"
        :step="0.1"
        :precision="2"
        size="small"
      />
      <div class="setting-hint">Threshold value for edge detection (0-1)</div>
    </div>

    <!-- Sigma 设置 -->
    <div class="setting-item">
      <span class="setting-label">Sigma:</span>
      <el-input-number 
        v-model="cannyParams.sigma" 
        :min="0"
        :max="5"
        :step="0.1"
        :precision="2"
        size="small"
      />
      <div class="setting-hint">Sigma value for Gaussian filter (0-5)</div>
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

// Canny 参数
const cannyParams = ref({
  threshold: 0.5,  // 默认阈值
  sigma: 1.0,      // 默认 sigma 值
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
  cannyParams.value.band = null
}, { deep: true })


// 获取参数方法
const getParams = () => {
  // 为每个选中的图层创建参数
  const params = {}
  props.selectedLayerName.forEach(layerId => {
    params[layerId] = {
      threshold: cannyParams.value.threshold,
      sigma: cannyParams.value.sigma
    }
  })
  
  return params
}

// 暴露方法给父组件
defineExpose({
  getParams
})
</script>

<style scoped>
.canny-settings {
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