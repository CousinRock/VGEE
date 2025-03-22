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
            ElMessage.error(data.message || 'Failed to search data')
            return []
        }
    } catch (error) {
        console.error('Error searching data:', error)
        ElMessage.error('Failed to search data')
        return []
    }
}

// 处理数据集选择
export const handleDatasetSelect = async (dataset) => {
    try {
        // 发送事件通知
        eventBus.emit('dataset-selected', dataset)
        return dataset
    } catch (error) {
        console.error('Error handling dataset select:', error)
        throw error
    }
}

// 处理ID搜索
export const handleIdSearch = async (datasetId) => {
    try {
        const datasets = await searchData(datasetId)
        return datasets
    } catch (error) {
        console.error('Error searching dataset:', error)
        ElMessage.error('Failed to search dataset')
    }

}