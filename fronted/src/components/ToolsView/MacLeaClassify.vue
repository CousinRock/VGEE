<template>
    <div class="mac-lea-classify">
        <h4>分类设置</h4>

        <!-- K-means 分类设置 -->
        <div v-if="currentTool === TOOL_IDS.CLASSIFICATION.KMEANS">
            <h5>K-means 分类设置</h5>
            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                <div class="layer-name">
                    {{ availableLayers.find(l => l.id === layerId)?.name }}
                </div>
                <div class="option-item">
                    <label>分类数量：</label>
                    <el-slider v-model="classifyParams.clusterCounts[layerId]" :min="2" :max="20" :step="1" show-input
                        :marks="{
                            2: '2',
                            5: '5',
                            10: '10',
                            20: '20',
                        }" />
                </div>
            </div>
        </div>

        <!-- 随机森林分类设置 -->
        <div v-if="currentTool === TOOL_IDS.CLASSIFICATION.RANDOM_FOREST">
            <h5>随机森林设置</h5>
            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                <div class="layer-name">
                    {{ availableLayers.find(l => l.id === layerId)?.name }}
                </div>
                <div class="option-item">
                    <label>决策树数量：</label>
                    <el-slider v-model="classifyParams.rfParams[layerId].numberOfTrees" :min="10" :max="200" :step="1"
                        show-input :marks="{
                            10: '10',
                            50: '50',
                            100: '100',
                            150: '150',
                            200: '200'
                        }" />
                </div>
                <div class="option-item">


                    <label>训练集比例：</label>
                    <el-slider v-model="classifyParams.rfParams[layerId].trainRatio" :min="0.1" :max="0.9" :step="0.1"
                        show-input :marks="{
                            0.5: '50%',
                            0.7: '70%',
                            0.9: '90%'
                        }" />
                </div>
            </div>
        </div>

        <!-- SVM 分类设置 -->
        <div v-if="currentTool === TOOL_IDS.CLASSIFICATION.SVM">
            <h5>支持向量机设置</h5>
            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                <div class="layer-name">
                    {{ availableLayers.find(l => l.id === layerId)?.name }}
                </div>
                <div class="option-item">
                    <label>核函数类型：</label>
                    <el-select v-model="classifyParams.svmParams[layerId].kernel" size="small">
                        <el-option label="RBF" value="RBF" />
                        <el-option label="Linear" value="Linear" />
                        <el-option label="Poly" value="Poly" />
                    </el-select>
                </div>
                <div class="option-item">
                    <label>训练集比例：</label>
                    <el-slider v-model="classifyParams.svmParams[layerId].trainRatio" :min="0.1" :max="0.9" :step="0.1"
                        show-input :marks="{
                            0.5: '50%',
                            0.7: '70%',
                            0.9: '90%'
                        }" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { TOOL_IDS } from '../../config/tools-config'

const props = defineProps({
    selectedLayerName: {
        type: Array,
        required: true
    },
    availableLayers: {
        type: Array,
        required: true
    },
    currentTool: {
        type: String,
        required: true
    }
});

// 统一管理分类参数
const classifyParams = ref({
    clusterCounts: {},  // K-means的分类数量
    rfParams: {},       // 随机森林参数，改为对象形式
    svmParams: {}       // SVM参数，改为对象形式
});

// 监听选中图层变化，初始化参数
watch(() => props.selectedLayerName, (newLayers) => {
    // 初始化每个图层的随机森林参数
    newLayers.forEach(layerId => {
        if (!classifyParams.value.rfParams[layerId]) {
            classifyParams.value.rfParams[layerId] = {
                numberOfTrees: 50,
                trainRatio: 0.7
            }
        }
        if (!classifyParams.value.svmParams[layerId]) {
            classifyParams.value.svmParams[layerId] = {
                kernel: 'RBF',
                trainRatio: 0.7
            }
        }
    })
}, { immediate: true })

// 监听参数变化
watch(classifyParams, (newVal) => {
    console.log('MacLeaClassify.vue - watch - classifyParams:', newVal)
}, { deep: true });

// 暴露方法和状态给父组件
defineExpose({
    classifyParams
})

</script>

<style scoped>
/* 添加样式 */
.mac-lea-classify {
    padding: 10px;
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

.option-item {
    margin-bottom: 10px;
}

.option-item label {
    display: block;
    margin-bottom: 8px;
    color: #606266;
}

/* 添加新样式 */
.kernel-select {
    width: 100%;
    margin-bottom: 15px;
}

.el-select {
    width: 100%;
}

/* 提示信息样式 */
.parameter-hint {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.4;
}
</style>
