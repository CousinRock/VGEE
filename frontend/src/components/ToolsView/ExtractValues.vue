<template>
    <div class="extract-container">
        <el-form :model="extractParams" label-width="120px">
            <!-- 采样点图层选择 -->
            <el-form-item label="Sample Points">
                <el-select v-model="extractParams.sampleLayerId" class="sample-select">
                    <el-option 
                        v-for="layer in vectorLayers" 
                        :key="layer.id" 
                        :label="layer.name" 
                        :value="layer.id"
                    />
                </el-select>
            </el-form-item>

            <!-- 采样分辨率 -->
            <el-form-item label="Scale">
                <el-input-number 
                    v-model="extractParams.scale" 
                    :min="1" 
                    :max="1000" 
                    :step="1"
                    class="scale-input" 
                />
                <div class="parameter-hint">
                    Sampling resolution in meters. Lower values give more precise results but take longer to process.
                </div>
            </el-form-item>

            <!-- 导出格式选择 -->
            <el-form-item label="Export Format">
                <el-radio-group v-model="exportFormat">
                    <el-radio label="csv">CSV</el-radio>
                    <el-radio label="excel">Excel</el-radio>
                </el-radio-group>
            </el-form-item>
        </el-form>
    </div>
</template>

<script setup>
import { ref, defineProps, defineExpose, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'

const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})

// 提取参数
const extractParams = ref({
    sampleLayerId: '',
    scale: 30
})

// 导出格式选择
const exportFormat = ref('csv')

// 获取矢量图层（点）
const vectorLayers = computed(() => {
    return props.mapView.layers.filter(layer => layer.type === 'vector')
})

// 导出为CSV
const exportCSV = (data, filename) => {
    if (!data || data.length === 0) {
        ElMessage.warning('No data to export')
        return
    }

    // 获取所有列（除了系统属性）
    const firstResult = data[0]
    const columns = Object.keys(firstResult).filter(key => 
        !['pointId', 'layerId', 'layerName'].includes(key)
    )

    const headers = ['Point ID', 'Layer Name', ...columns]
    const csvContent = [
        headers.join(','),
        ...data.map(row => [
            row.pointId,
            row.layerName,
            ...columns.map(col => {
                const value = row[col]
                return typeof value === 'number' ? value.toFixed(6) : value
            })
        ].join(','))
    ].join('\n')

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
}

// 导出为Excel
const exportExcel = (data, filename) => {
    try {
        if (!data || data.length === 0) {
            ElMessage.warning('No data to export')
            return
        }

        // 获取所有列（除了系统属性）
        const firstResult = data[0]
        const columns = Object.keys(firstResult).filter(key => 
            !['pointId', 'layerId', 'layerName'].includes(key)
        )

        const excelData = data.map(row => {
            const baseData = {
                'point_id': row.pointId,
                'layer_name': row.layerName
            }
            columns.forEach(col => {
                const value = row[col]
                baseData[col] = typeof value === 'number' ? value.toFixed(6) : value
            })
            return baseData
        })

        const wb = XLSX.utils.book_new()
        const ws = XLSX.utils.json_to_sheet(excelData)

        const headers = ['Point ID', 'Layer Name', ...columns]
        XLSX.utils.sheet_add_aoa(ws, [headers], { origin: 'A1' })

        const colWidths = [
            { wch: 15 }, // Point ID
            { wch: 20 }, // Layer Name
            ...columns.map(() => ({ wch: 12 }))
        ]
        ws['!cols'] = colWidths

        XLSX.utils.book_append_sheet(wb, ws, 'Extracted Values')
        XLSX.writeFile(wb, filename)

        ElMessage.success('Export successfully')
    } catch (error) {
        console.error('Error exporting to Excel:', error)
        ElMessage.error('Export failed')
    }

}

// 暴露方法给父组件
defineExpose({
    getParams: () => ({
        ...extractParams.value,
        exportFormat: exportFormat.value
    }),
    setResult: (result) => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
        const filename = `Extracted_Values_${timestamp}`
        
        if (exportFormat.value === 'csv') {
            exportCSV(result, `${filename}.csv`)
        } else {
            exportExcel(result, `${filename}.xlsx`)
        }
    }
})
</script>

<style scoped>
.extract-container {
    padding: 20px;
}

.sample-select {
    width: 200px;
}

.scale-input {
    width: 180px;
}

.parameter-hint {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.4;
}

:deep(.el-select) {
    width: 200px;
}
</style> 