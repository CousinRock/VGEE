<template>
  <div class="search-results-container">
    <h2>搜索结果</h2>
    <el-button @click="closeResults" type="danger" class="close-button">
      <i class="fas fa-times"></i>
    </el-button>

    <el-table :data="datasets" style="width: 100%" height="400" stripe>
      <!-- 缩略图列 -->
      <el-table-column label="预览图" width="120">
        <template #default="scope">
          <el-image
            v-if="scope.row.thumbnail_url"
            :src="scope.row.thumbnail_url"
            :preview-src-list="[scope.row.thumbnail_url]"
            fit="cover"
            class="thumbnail-image"
          >
            <template #error>
              <div class="image-placeholder">
                <i class="fas fa-image"></i>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>

      <!-- 标题列 -->
      <el-table-column prop="title" label="标题" min-width="200">
        <template #default="scope">
          <div class="title-cell">
            <span class="dataset-title">{{ scope.row.title }}</span>
            <a 
              v-if="scope.row.asset_url" 
              :href="scope.row.asset_url" 
              target="_blank" 
              class="dataset-link"
            >
              <i class="fas fa-external-link-alt"></i>
            </a>
          </div>
        </template>
      </el-table-column>

      <!-- 提供者列 -->
      <el-table-column prop="provider" label="提供者" width="150" />

      <!-- 数据类型列 -->
      <el-table-column prop="type" label="类型" width="120">
        <template #default="scope">
          <el-tag :type="getTypeTagType(scope.row.type)">
            {{ formatType(scope.row.type) }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- 时间范围列 -->
      <el-table-column label="时间范围" width="200">
        <template #default="scope">
          <div class="date-range">
            {{ scope.row.start_date }} 至 {{ scope.row.end_date || '至今' }}
          </div>
        </template>
      </el-table-column>

      <!-- 操作列 -->
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="scope">
          <el-button @click="selectDataset(scope.row)" type="primary" size="small">
            选择
          </el-button>
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

// 格式化数据类型显示
const formatType = (type) => {
  const typeMap = {
    'image_collection': '影像集合',
    'image': '影像',
    'feature_collection': '矢量集合',
    'feature': '矢量'
  }
  return typeMap[type] || type
}

// 获取类型标签的样式
const getTypeTagType = (type) => {
  const typeTagMap = {
    'image_collection': 'success',
    'image': 'primary',
    'feature_collection': 'warning',
    'feature': 'info'
  }
  return typeTagMap[type] || ''
}
</script>

<style src="../styles/search-results.css"></style>
