<template>
  <div class="random-points-container">
    <el-form :model="form" label-width="120px">
      <!-- Points -->
      <el-form-item label="points">
        <el-input-number
          v-model="form.numPixels"
          :min="1"
          :max="10000"
          :step="100"
          placeholder="Enter number of points"
        />
      </el-form-item>

      <!-- Scale -->
      <el-form-item label="scale(m)">
        <el-input-number
          v-model="form.scale"
          :min="10"
          :max="1000"
          :step="10"
          placeholder="Enter sampling scale"
        />
      </el-form-item>

      <!-- Seed -->
      <el-form-item label="seed">
        <el-input-number
          v-model="form.seed"
          :min="0"
          :max="1000"
          :step="1"
          placeholder="Enter random seed"
        />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  selectedLayerName: {
    type: Array,
    required: true
  },
  availableLayers: {
    type: Array,
    required: true
  }
})

// Form data
const form = ref({
  numPixels: 2000,
  scale: 30,
  seed: 0
})

// Get params method for parent component
const getParams = () => {
  return {
    ...form.value
  }
}

// Expose methods to parent
defineExpose({
  getParams
})
</script>

<style scoped>
.random-points-container {
  padding: 20px;
}
</style> 