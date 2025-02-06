<template>
  <div class="search-results-container" v-show="searchState.showResults || searchState.activeSearchId">
    <h2>搜索结果</h2>
    <el-button @click="closeResults" type="danger" class="close-button">
      <i class="fas fa-times"></i>
    </el-button>

    <!-- 自定义ID搜索框 -->
    <div v-if="searchState.activeSearchId" class="id-search">
      <el-input v-model="searchState.customId" placeholder="输入数据集ID" size="small" @keyup.enter="handleCustomIdSearch"
        class="search-input">
        <template #append>
          <el-button @click="handleCustomIdSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- 只在有搜索结果时显示表格 -->
    <el-table v-if="searchState.results.length > 0" :data="searchState.results" style="width: 100%" height="400" stripe>
      <!-- 缩略图列 -->
      <el-table-column label="预览图" width="120">
        <template #default="scope">
          <el-image v-if="scope.row.thumbnail_url" :src="scope.row.thumbnail_url"
            :preview-src-list="[scope.row.thumbnail_url]" fit="cover" class="thumbnail-image">
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
            <a v-if="scope.row.asset_url" :href="scope.row.asset_url" target="_blank" class="dataset-link">
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
            import
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as SearchDataService from '../../service/headTools/searchData'
import { ElMessage } from 'element-plus'

// 统一管理搜索相关的状态
const searchState = ref({
  showResults: false,
  results: [],
  selectedDataset: null,
  customId: '',
  activeSearchId: false,
  typeMap: {
    'image_collection': '影像集合',
    'image': '影像',
    'feature_collection': '矢量集合',
    'feature': '矢量'
  },
  tagTypeMap: {
    'image_collection': 'success',
    'image': 'primary',
    'feature_collection': 'warning',
    'feature': 'info'
  }
})

// 格式化数据类型显示
const formatType = (type) => {
  return searchState.value.typeMap[type] || type
}

// 获取类型标签的样式
const getTypeTagType = (type) => {
  return searchState.value.tagTypeMap[type] || ''
}

// 处理数据集选择
const selectDataset = async (dataset) => {
  try {
    searchState.value.selectedDataset = dataset
    await SearchDataService.handleDatasetSelect(dataset)
    // 通知已经在 handleDatasetSelect 中完成
  } catch (error) {
    console.error('Error selecting dataset:', error)
    ElMessage.error('选择数据集失败')
  }
}

// 处理ID搜索
const handleCustomIdSearch = async () => {
  try {
    const datasets = await SearchDataService.handleIdSearch(searchState.value.customId)
    searchState.value.results = datasets
    searchState.value.showResults = true
  } catch (error) {
    console.error('Error searching by ID:', error)
  }
}

// 更新搜索结果
const updateSearchResults = (datasets) => {
  searchState.value.results = datasets
  searchState.value.showResults = true
}

// 关闭结果
const closeResults = () => {
  searchState.value.showResults = false
  searchState.value.activeSearchId = false
  searchState.value.results = []
  searchState.value.customId = ''
}

// 切换ID搜索状态
const toggleIdSearch = () => {
  searchState.value.activeSearchId = !searchState.value.activeSearchId
  // 如果是开启搜索，清空之前的结果
  if (searchState.value.activeSearchId) {
    searchState.value.results = []
    searchState.value.customId = ''
  }
}


// 暴露方法和状态给父组件
defineExpose({
  searchState,
  updateSearchResults,
  toggleIdSearch,
  handleCustomIdSearch
})
</script>

<style src="../../styles/search-results.css"></style>
