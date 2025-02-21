<template>
  <div class="rename-bands-container">
    <h3>Rename Bands</h3>
    <div v-for="(band, index) in renameBandsParams.bands" :key="index" class="band-row">
      <el-select v-model="band.original" placeholder="Select Original Band Name">
        <el-option v-for="option in availableBands" :key="option" :label="option" :value="option" />
      </el-select>
      <el-select v-model="band.new" placeholder="Select New Band Name">
        <el-option v-for="option in newBandNames" :key="option" :label="option" :value="option" />
        <el-option label="Custom" value="custom" />
      </el-select>
      <el-input v-if="band.new === 'custom'" v-model="band.customName" placeholder="Enter Custom Name" />
      <el-button @click="removeBand(index)" type="danger" circle class="delete-btn">
        ×
      </el-button>
    </div>
    <div class="button-group">
      <el-button @click="addBand">Add Band</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineEmits, defineExpose } from 'vue'

const props = defineProps({
  availableBands: {
    type: Array,
    required: true
  },
  layerBands: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:bands'])
// 统一管理重命名参数
const renameBandsParams = ref({
  bands: [{ original: '', new: '', customName: '' }]
})

const newBandNames = ['RED', 'GREEN', 'BLUE', 'NIR', 'SWIR1', 'SWIR2']
const addBand = () => {
  renameBandsParams.value.bands.push({ original: '', new: '', customName: '' })
}

const removeBand = (index) => {
  renameBandsParams.value.bands.splice(index, 1)
}

// 监听参数变化
watch(renameBandsParams, (newVal) => {
  console.log('RenameBands.vue - watch - renameBandsParams:', newVal)
  emit('update:bands', newVal.bands)
}, { deep: true })

// 暴露方法和状态给父组件
defineExpose({
  renameBandsParams
})
</script>

<style scoped>
.rename-bands-container {
  margin: 20px;
}

.band-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.button-group {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.delete-btn {
  font-size: 20px;
  padding: 8px;
  line-height: 1;
}
</style>
