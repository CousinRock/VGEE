import { ElMessage } from 'element-plus'
import { API_ROUTES } from '../api/routes'


export const satelliteManager = {
    // 获取卫星配置
    satelliteConfig : async () => {
        try {
            const response = await fetch(API_ROUTES.MAP.GET_SATELLITE_CONFIG)
            const data = await response.json()
            if (data.success) {
                return data.satelliteOptions
            } else {
                console.error('Failed to get satellite config:', data.message)
                return null
            }
        } catch (error) {
            console.error('Error fetching satellite config:', error)
            ElMessage.error('Failed to get satellite config')
            return null
        }
    },
    //添加卫星数据到卫星配置中
    addDataToSatelliteConfig : async (dataset,satelliteOptions) => {
        // 检查是否已存在该数据集
    const isExist = satelliteOptions.value.some(group => 
        group.options.some(option => option.value === dataset.id)
    )
    
    if (!isExist) {
        const newOption = {
            label: dataset.title,
            options: [{
                value: dataset.id,
                label: dataset.title,
                startDate: dataset.start_date,
                endDate: dataset.end_date,
                asset_url: dataset.asset_url,
                thumbnail_url: dataset.thumbnail_url,
                provider: dataset.provider,
                tags: dataset.tags,
                type: dataset.type
            }]
        }
        satelliteOptions.value.push(newOption)
        console.log('ControlPanel.vue - addDatasetToOptions - satelliteOptions:', satelliteOptions)

        // 发送到后端存储
        fetch(API_ROUTES.SEARCH.ADD_SATELLITE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataset)
        }).then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Failed to add satellite:', data.message)
                    ElMessage({
                        message: `Failed to add satellite: ${data.message}`,
                        type: 'error'
                    })
                }
                ElMessage({
                    message: 'Add satellite successfully',
                    type: 'success'
                })

            })
            .catch(error => {
                console.error('Error adding satellite:', error)
                ElMessage({
                    message: `Failed to add satellite: ${error}`,
                    type: 'error'
                })
            })
    } else {
        console.log('Dataset already exists:', dataset.id)
        ElMessage({
            message: `Dataset already exists: ${dataset.id}`,
            type: 'warning'
        })
    }
    }
}
