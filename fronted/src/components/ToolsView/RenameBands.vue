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
    </div>
    <el-button @click="addBand">添加波段</el-button>
    <el-button type="primary" @click="renameBands">重命名波段</el-button>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'

const props = defineProps({
  availableBands: {
    type: Array,
    required: true
  }
})

const newBandNames = ['红', '绿', '蓝'] // 固定的新波段名
const bands = ref([{ original: '', new: '', customName: '' }])

const addBand = () => {
  bands.value.push({ original: '', new: '', customName: '' })
}

const renameBands = () => {
  bands.value.forEach(band => {
    const newName = band.new === 'custom' ? band.customName : band.new
    console.log(`重命名 ${band.original} 为 ${newName}`)
    // 在这里添加实际的重命名逻辑
  })
}
</script>

<style scoped>
.rename-bands-container {
  margin: 20px;
}
.band-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
</style>
