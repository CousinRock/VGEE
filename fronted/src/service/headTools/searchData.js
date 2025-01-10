import { ElMessage } from 'element-plus'
import { API_ROUTES } from '../../api/routes'
import eventBus from '../../util/eventBus'

// 搜索数据
export const searchData = async (datasetType) => {
    try {
        const response = await fetch(API_ROUTES.SEARCH.SEARCH_DATA, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ dataset_type: datasetType })
        })
        const data = await response.json()
        if (data.success) {
            return data.datasets
        } else {
            ElMessage.error(data.message || '搜索数据失败')
            return []
        }
    } catch (error) {
        console.error('Error searching data:', error)
        ElMessage.error('搜索数据失败')
        return []
    }
}

// 处理数据集选择
export const handleDatasetSelect = (dataset, selectedDataset, showSearchResults) => {
    selectedDataset.value = dataset
    console.log('searchData.js - handleDatasetSelect - dataset:', dataset)
    eventBus.emit('dataset-selected', dataset)
    // showSearchResults.value = false
}

// ID搜索处理
export const handleIdSearch = async (customDatasetId, searchResults, showSearchResults) => {
    if (!customDatasetId || !customDatasetId.trim()) {
        ElMessage.warning('请输入数据集 ID')
        return
    }
    
    try {
        const datasets = await searchData(customDatasetId.trim())
        searchResults.value = datasets
        showSearchResults.value = true
    } catch (error) {
        console.error('Error searching dataset:', error)
        ElMessage.error('搜索失败')
    }
}