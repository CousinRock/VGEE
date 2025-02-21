<template>
    <el-dialog v-model="showDialog" title="Location Search" width="400px">
        <div class="location-search-container">
            <div class="search-box">
                <el-input v-model="searchQuery" placeholder="Enter location name..." @keyup.enter="handleSearch">
                    <template #append>
                        <el-button @click="handleSearch" :loading="isSearching">
                            <i class="fas fa-search"></i>
                        </el-button>
                    </template>
                </el-input>
            </div>

            <div class="search-history" v-if="searchHistory.length > 0">
                <div class="history-header">
                    <h4>Search History</h4>
                    <el-button type="text" @click="clearHistory">
                        Clear History
                    </el-button>
                </div>
                <el-scrollbar height="200px">
                    <ul>
                        <li v-for="(item, index) in searchHistory" :key="index" class="history-item">
                            <span @click="handleHistoryClick(item)">
                                {{ item.address }}
                            </span>
                            <el-button type="text" @click="removeHistory(index)" class="delete-btn">
                                <i class="fas fa-times"></i>
                            </el-button>
                        </li>
                    </ul>
                </el-scrollbar>
            </div>
        </div>
    </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
    mapView: {
        type: Object,
        required: true,
        validator: (value) => {
            return value && value.map // 确保 map 对象存在
        }
    }
})

const searchQuery = ref('')
const searchHistory = ref([])
const showDialog = ref(false)
const isSearching = ref(false)

// 使用 Nominatim API 搜索位置
const handleSearch = async () => {
    if (!props.mapView?.map) {
        ElMessage.error('Map not initialized')
        return
    }
    if (!searchQuery.value) {
        ElMessage.warning('Please enter search content')
        return
    }

    isSearching.value = true
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}`
        )
        const data = await response.json()

        if (data && data.length > 0) {
            console.log(data);

            const location = data[0]

            // 移动地图到搜索位置
            props.mapView.map.setView([location.lat, location.lon], 15)

            // 添加到搜索历史
            const historyItem = {
                address: location.display_name,
                lat: location.lat,
                lon: location.lon
            }

            console.log('LocationSearch.vue-handleSearch-historyItem', historyItem);

            if (!searchHistory.value.some(item => item.address === historyItem.address)) {
                searchHistory.value.unshift(historyItem)
                // 限制历史记录数量
                if (searchHistory.value.length > 5) {
                    searchHistory.value.pop()
                }
                // 保存到本地存储
                localStorage.setItem('locationHistory', JSON.stringify(searchHistory.value))
            }

            searchQuery.value = '' // 清空搜索框
            ElMessage.success('Location found')
            showDialog.value = false
        } else {
            ElMessage.error('Location not found')
        }
    } catch (error) {
        console.error('Location search error:', error)
        ElMessage.error('Error searching location')
    } finally {
        isSearching.value = false
    }
}

const handleHistoryClick = (item) => {
    props.mapView.map.setView([item.lat, item.lon], 15)
    showDialog.value = false
}

const removeHistory = (index) => {
    searchHistory.value.splice(index, 1)
    localStorage.setItem('locationHistory', JSON.stringify(searchHistory.value))
}

const clearHistory = () => {
    searchHistory.value = []
    localStorage.removeItem('locationHistory')
}

// 从本地存储加载历史记录
const loadHistory = () => {
    const history = localStorage.getItem('locationHistory')
    if (history) {
        searchHistory.value = JSON.parse(history)
    }
}

// 初始化时加载历史记录
loadHistory()

// 暴露方法给父组件
defineExpose({
    showDialog
})
</script>

<style scoped>
.location-search-container {
    padding: 10px;
}

.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.history-header h4 {
    margin: 0;
    color: #606266;
}

.search-history {
    margin-top: 20px;
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    margin: 4px 0;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.history-item:hover {
    background: #f5f7fa;
}

.history-item span {
    flex: 1;
    margin-right: 10px;
    font-size: 14px;
}

.delete-btn {
    padding: 2px 4px;
    color: #909399;
}

.delete-btn:hover {
    color: #f56c6c;
}
</style>