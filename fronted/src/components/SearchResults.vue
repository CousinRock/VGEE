<template>
  <div class="search-results-container">
    <h2>搜索结果</h2>
    <el-button @click="closeResults" type="danger" class="close-button">关闭</el-button>
    <el-table :data="datasets" style="width: 100%" height="400" stripe>
      <el-table-column prop="title" label="标题" width="200"></el-table-column>
      <el-table-column prop="provider" label="提供者" width="150"></el-table-column>
      <el-table-column prop="dates" label="日期范围" width="180"></el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button @click="selectDataset(scope.row)" type="primary">选择</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  datasets: Array
})

const emit = defineEmits(['select', 'close'])

const selectDataset = (dataset) => {
  emit('select', dataset)
}

const closeResults = () => {
  emit('close')
}
</script>

<style src="../styles/search-results.css"></style>
