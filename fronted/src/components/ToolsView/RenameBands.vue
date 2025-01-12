<template>
  <div class="rename-bands-container">
    <h3>重命名波段</h3>
    <div v-for="(band, index) in bands" :key="index" class="band-row">
      <el-select v-model="band.original" placeholder="选择原始波段名">
        <el-option
          v-for="option in availableBands"
          :key="option"
          :label="option"
          :value="option"
        />
      </el-select>
      <el-select v-model="band.new" placeholder="选择新波段名">
        <el-option
          v-for="option in newBandNames"
          :key="option"
          :label="option"
          :value="option"
        />
        <el-option label="自定义" value="custom" />
      </el-select>
      <el-input
        v-if="band.new === 'custom'"
        v-model="band.customName"
        placeholder="输入自定义名称"
      />
      <el-button @click="removeBand(index)" type="danger" circle class="delete-btn">
        ×
      </el-button>
    </div>
    <div class="button-group">
      <el-button @click="addBand">添加波段</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue'

const props = defineProps({
  availableBands: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['update:bands'])

const newBandNames = ['RED', 'GREEN', 'BLUE', 'NIR', 'SWIR1', 'SWIR2'] 
const bands = ref([{ original: '', new: '', customName: '' }])

const addBand = () => {
  bands.value.push({ original: '', new: '', customName: '' })
}

const removeBand = (index) => {
  bands.value.splice(index, 1)
}

watch(bands, (newVal) => {
    console.log('RenameBands.vue - watch - bands:', newVal)
    emit('update:bands', newVal)
}, { deep: true })

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
