<template>
    <div class="statistics-container">
        <el-form :model="statisticsParams" label-width="120px">

            <!-- 面积统计模式的参数 -->
            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                <div class="layer-name">
                    {{ availableLayers.find(l => l.id === layerId)?.name }}
                </div>
                <!-- 波段选择 -->
                <el-form-item label="统计波段">
                    <el-select v-model="statisticsParams.params[layerId].band" class="band-select">
                        <el-option 
                            v-for="band in layerBands[layerId]" 
                            :key="band" 
                            :label="band" 
                            :value="band" 
                        />
                    </el-select>
                </el-form-item>
                
                <!-- 目标值输入 -->
                <el-form-item label="目标值">
                    <el-input-number v-model="statisticsParams.params[layerId].value" :step="1" />
                </el-form-item>
            </div>
        </el-form>

        <!-- 统计结果展示 -->
        <div v-if="statisticsResult" class="statistics-result">
            <h3>统计结果</h3>
            <el-table :data="formatResults" border style="width: 100%">
                <el-table-column prop="layerName" label="影像名称" />
                <el-table-column prop="band" label="统计波段" />
                <el-table-column prop="value" label="目标值" />
                <el-table-column prop="totalArea" label="面积(km²)">
                    <template #default="scope">
                        {{ Number(scope.row.totalArea).toFixed(2) }}
                    </template>
                </el-table-column>         
            </el-table>
        </div>
    </div>
</template>

<script setup>
import { ref, defineProps, defineExpose, computed, watch } from 'vue'

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
       
    }))
})

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
</style>
