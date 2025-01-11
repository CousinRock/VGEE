import { ElMessage } from 'element-plus'
import { API_ROUTES } from '../../api/routes'

// 标准波段选项
export const BAND_OPTIONS = [
    { label: '红波段 (Red)', value: 'RED' },
    { label: '绿波段 (Green)', value: 'GREEN' },
    { label: '蓝波段 (Blue)', value: 'BLUE' },
    { label: '近红外波段 (NIR)', value: 'NIR' },
    { label: '短波红外1 (SWIR1)', value: 'SWIR1' },
    { label: '短波红外2 (SWIR2)', value: 'SWIR2' }
]

// 处理波段重命名
export const handleBandRename = async (layerId, bandMappings, mapView) => {
    try {
        const response = await fetch(API_ROUTES.TOOLS.RENAME_BANDS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                layer_id: layerId,
                band_mappings: bandMappings,
                vis_params: [{
                    id: layerId,
                    visParams: mapView.layers.find(l => l.id === layerId)?.visParams
                }]
            })
        })
        
        const data = await response.json()
        if (!data.success) {
            throw new Error(data.message || '重命名波段失败')
        }
        return data
    } catch (error) {
        console.error('Error renaming bands:', error)
        throw error
    }
} 