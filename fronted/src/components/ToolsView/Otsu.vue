<template>
  <div class="otsu-settings">
    <h3>OTSU Threshold Settings</h3>
    
    <!-- 比例尺设置 -->
    <div class="setting-item">
      <span class="setting-label">Scale (meters):</span>
      <el-input-number 
        v-model="otsuParams.scale" 
        :min="10"
        :max="1000"
        :step="10"
        size="small"
      />
      <div class="setting-hint">Resolution of analysis (10-1000m)</div>
    </div>

    <!-- 最大数组大小设置 -->
    <div class="setting-item">
      <span class="setting-label">Max Buckets:</span>
      <el-input-number 
        v-model="otsuParams.maxArray" 
        :min="10"
        :max="2000"
        :step="1"
        size="small"
      />
      <div class="setting-hint">Maximum number of histogram buckets (10-2000)</div>
    </div>

    <!-- 最小距离设置 -->
    <div class="setting-item">
      <span class="setting-label">Minimum Distance:</span>
      <el-input-number 
        v-model="otsuParams.minDis" 
        :min="0.001"
        :max="1"
        :step="0.001"
        :precision="3"
        size="small"
      />
      <div class="setting-hint">Minimum distance between buckets (0.001-1)</div>
    </div>

    <!-- 波段选择 -->
    <div class="setting-item">
      <span class="setting-label">Band:</span>
      <el-select 
        v-model="otsuParams.band" 
        placeholder="Select band"
        size="small"
      >
        <el-option
          v-for="band in availableBands"
          :key="band"
          :label="band"
          :value="band"
        />
      </el-select>
      <div class="setting-hint">Select band for threshold calculation</div>
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

// OTSU 参数
const otsuParams = ref({
  scale: 30,      // 默认30米分辨率
  maxArray: 1000,  // 默认256个直方图分组
  minDis: 0.01,  // 默认最小距离
  band: null      // 选择的波段
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
  otsuParams.value.band = null
}, { deep: true })

// 验证参数
const validateParams = () => {
  if (!otsuParams.value.band) {
    ElMessage.warning('Please select a band')
    return false
  }
  return true
}

// 获取参数方法
const getParams = () => {
  if (!validateParams()) return null
  
  // 为每个选中的图层创建参数
  const params = {}
  props.selectedLayerName.forEach(layerId => {
    params[layerId] = {
      scale: otsuParams.value.scale,
      maxArray: otsuParams.value.maxArray,
      minDis: otsuParams.value.minDis,
      band: otsuParams.value.band
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
.otsu-settings {
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
