<template>
    <div class="statistics-container">
        <el-form :model="statisticsParams" label-width="120px">
            <el-form-item label="Scale">
                <el-input-number v-model="statisticsParams.resolution" :min="1" :max="1000" :step="1"
                    class="resolution-input" />
                <div class="parameter-hint">
                    Calculation accuracy, the smaller the value, the higher the accuracy, but the calculation time will
                    be longer
                </div>
            </el-form-item>

            <!-- Area statistics mode parameters -->
            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                <div class="layer-name">
                    {{availableLayers.find(l => l.id === layerId)?.name}}
                </div>
                <!-- Band selection -->
                <el-form-item label="Statistical Band">
                    <el-select v-model="statisticsParams.params[layerId].band" class="band-select">
                        <el-option v-for="band in layerBands[layerId]" :key="band" :label="band" :value="band" />
                    </el-select>
                </el-form-item>

                <!-- Target value input -->
                <el-form-item label="Target Value">
                    <el-input-number v-model="statisticsParams.params[layerId].value" :step="1" />
                </el-form-item>
            </div>
        </el-form>

        <!-- Statistics result display -->
        <div v-if="statisticsResult" class="statistics-result">
            <div class="result-header">
                <h3>Statistics Result</h3>
                <div class="export-buttons">
                    <el-dropdown @command="handleExport">
                        <el-button type="primary" size="small">
                            <i class="fas fa-download"></i> Export
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </el-button>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item command="csv">Export as CSV</el-dropdown-item>
                                <el-dropdown-item command="excel">Export as Excel</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
            </div>

            <el-table :data="formatResults" style="width: 100%">
                <el-table-column prop="layerName" label="Image Name" />
                <el-table-column prop="band" label="Statistical Band" />
                <el-table-column prop="value" label="Target Value" />
                <el-table-column prop="totalArea" label="Area(km²)">
                    <template #default="scope">
                        {{ Number(scope.row.totalArea).toFixed(5) }}
                    </template>
                </el-table-column>
                <el-table-column prop="count" label="Pixel Count" />
                <el-table-column prop="mean" label="Mean">
                    <template #default="scope">
                        {{ Number(scope.row.mean).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column prop="median" label="Median">
                    <template #default="scope">
                        {{ Number(scope.row.median).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column prop="mode" label="Mode">
                    <template #default="scope">
                        {{ Number(scope.row.mode).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column prop="min" label="Minimum">
                    <template #default="scope">
                        {{ Number(scope.row.min).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column prop="max" label="Maximum">
                    <template #default="scope">
                        {{ Number(scope.row.max).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column prop="stdDev" label="Standard Deviation">
                    <template #default="scope">
                        {{ Number(scope.row.stdDev).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column prop="q1" label="Q1">
                    <template #default="scope">
                        {{ Number(scope.row.q1).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column prop="q3" label="Q3">
                    <template #default="scope">
                        {{ Number(scope.row.q3).toFixed(2) }}
                    </template>
                </el-table-column>
            </el-table>
        </div>
    </div>
</template>

<script setup>
import { ref, defineProps, defineExpose, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'

const props = defineProps({
    selectedLayerName: {
        type: Array,
        required: true
    },
    availableLayers: {
        type: Array,
        required: true
    },
    layerBands: {
        type: Object,
        required: true
    }
})

// 统计参数
const statisticsParams = ref({
    resolution: 30,  // 默认分辨率为30米
    params: {}  // 每个图层的面积统计参数
})

// 监听选中图层变化，初始化参数
watch(() => props.selectedLayerName, (newLayers) => {
    // 初始化每个图层的面积统计参数
    newLayers.forEach(layerId => {
        if (!statisticsParams.value.params[layerId]) {
            statisticsParams.value.params[layerId] = {
                band: null,
                value: 0
            }
        }
    })
    // 清理未选中图层的参数
    Object.keys(statisticsParams.value.params).forEach(layerId => {
        if (!newLayers.includes(layerId)) {
            delete statisticsParams.value.params[layerId]
        }
    })
}, { immediate: true })

// 统计结果
const statisticsResult = ref(null)

// 格式化结果为表格数据
const formatResults = computed(() => {
    console.log('statisticsResult', statisticsResult.value);

    if (!statisticsResult.value) return []

    return statisticsResult.value.map(result => ({
        layerName: props.availableLayers.find(l => l.id === result.layerId)?.name || result.layerId,
        band: result.band,
        value: result.value,
        totalArea: result.totalArea,
        mean: result.mean,
        median: result.median,
        min: result.min,
        max: result.max,
        count: result.count,
        mode: result.mode,
        stdDev: result.stdDev,
        q1: result.q1,
        q3: result.q3
    }))
})

// 添加导出相关函数
const handleExport = (type) => {
    if (!statisticsResult.value) {
        ElMessage.warning('没有可导出的数据')
        return
    }

    const data = formatResults.value
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')

    if (type === 'csv') {
        exportCSV(data, `Statistics Result_${timestamp}.csv`)
    } else if (type === 'excel') {
        exportExcel(data, `Statistics Result_${timestamp}.xlsx`)
    }
}

const exportCSV = (data, filename) => {
    // 获取表头
    const headers = [
        'Image Name', 'Statistical Band', 'Target Value', 'Area(km²)',
        'Pixel Count', 'Mean', 'Median', 'Mode',
        'Minimum', 'Maximum', 'Standard Deviation', 'Q1', 'Q3'
    ]

    const num = 5;
    // 转换数据为CSV格式
    const csvContent = [
        headers.join(','),
        ...data.map(row => [
            row.layerName,
            row.band,
            row.value,
            Number(row.totalArea).toFixed(num),
            row.count,
            Number(row.mean).toFixed(num),
            Number(row.median).toFixed(num),
            Number(row.mode).toFixed(num),
            Number(row.min).toFixed(num),
            Number(row.max).toFixed(num),
            Number(row.stdDev).toFixed(num),
            Number(row.q1).toFixed(num),
            Number(row.q3).toFixed(num)
        ].join(','))
    ].join('\n')

    // 创建Blob对象并下载
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
}

const exportExcel = async (data, filename) => {
    const num = 5;
    try {
        const excelData = data.map(row => ({
            'layer_name': row.layerName,
            'band': row.band,
            'target_value': row.value,
            'area': Number(row.totalArea).toFixed(num),
            'pixel_count': row.count,
            'mean': Number(row.mean).toFixed(num),
            'median': Number(row.median).toFixed(num),
            'mode': Number(row.mode).toFixed(num),
            'min': Number(row.min).toFixed(num),
            'max': Number(row.max).toFixed(num),
            'std_dev': Number(row.stdDev).toFixed(num),
            'q1': Number(row.q1).toFixed(num),
            'q3': Number(row.q3).toFixed(num)
        }))

        const wb = XLSX.utils.book_new()
        const ws = XLSX.utils.json_to_sheet(excelData)

        // 定义中文表头
        const headers = [
            'Image Name', 'Statistical Band', 'Target Value', 'Area(km²)',
            'Pixel Count', 'Mean', 'Median', 'Mode',
            'Minimum', 'Maximum', 'Standard Deviation', 'Q1', 'Q3'
        ]

        // 在第一行插入中文表头
        XLSX.utils.sheet_add_aoa(ws, [headers], { origin: 'A1' })

        // 设置列宽
        const colWidths = [
            { wch: 20 }, // 影像名称
            { wch: 10 }, // 统计波段
            { wch: 12 }, // 目标值
            { wch: 12 }, // 面积
            { wch: 12 }, // 像素数量
            { wch: 10 }, // 均值
            { wch: 10 }, // 中位值
            { wch: 10 }, // 众数
            { wch: 10 }, // 最小值
            { wch: 10 }, // 最大值
            { wch: 10 }, // 标准差
            { wch: 10 }, // Q1
            { wch: 10 }  // Q3
        ]
        ws['!cols'] = colWidths

        XLSX.utils.book_append_sheet(wb, ws, 'Statistics Result')
        XLSX.writeFile(wb, filename)

        ElMessage.success('Export successfully')
    } catch (error) {
        console.error('Error exporting to Excel:', error)
        ElMessage.error('Export Excel failed')
    }
}

// 导出参数和方法
defineExpose({
    statisticsParams,
    statisticsResult,
    setResult: (result) => {
        statisticsResult.value = result
    }
})
</script>

<style scoped>
.statistics-container {
    padding: 20px;
}

.statistics-result {
    margin-top: 20px;
    padding: 15px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.layer-option-item {
    margin-bottom: 20px;
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
}

.layer-name {
    font-weight: bold;
    margin-bottom: 10px;
    color: #409EFF;
}

.band-select {
    width: 200px;
}

:deep(.el-select) {
    width: 200px;
}

.resolution-input {
    width: 180px;
}

.parameter-hint {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.4;
}
</style>
