<template>
    <div class="mac-lea-classify">
        <h4>分类设置</h4>
        
        <!-- K-means 分类设置 -->
        <div v-if="currentTool === 'kmeans'">
            <h5>K-means 分类设置</h5>
            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                <div class="layer-name">
                    {{ availableLayers.find(l => l.id === layerId)?.name }}
                </div>
                <div class="option-item">
                    <label>分类数量：</label>
                    <el-slider v-model="clusterCounts[layerId]" :min="2" :max="20" :step="1" show-input :marks="{
                        2: '2',
                        5: '5',
                        10: '10',
                        20: '20',
                    }" />
                </div>
            </div>
        </div>

        <!-- 随机森林分类设置 -->
        <div v-if="currentTool === 'random-forest'">
            <h5>随机森林设置</h5>
            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                <div class="layer-name">
                    {{ availableLayers.find(l => l.id === layerId)?.name }}
                </div>
                <div class="option-item">
                    <label>决策树数量：</label>
                    <el-slider v-model="rfParams.numberOfTrees" :min="10" :max="100" :step="10" show-input :marks="{
                        10: '10',
                        50: '50',
                        100: '100'
                    }" />
                </div>
                <div class="option-item">
                    <label>训练集比例：</label>
                    <el-slider v-model="rfParams.trainRatio" :min="0.5" :max="0.9" :step="0.1" show-input :marks="{
                        0.5: '50%',
                        0.7: '70%',
                        0.9: '90%'
                    }" />
                </div>
            </div>
        </div>

        <!-- 添加 SVM 分类设置 -->
        <div v-if="currentTool === 'svm'">
            <h5>支持向量机设置</h5>
            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                <div class="layer-name">
                    {{ availableLayers.find(l => l.id === layerId)?.name }}
                </div>
                <div class="option-item">
                    <label>核函数类型：</label>
                    <el-select v-model="svmParams.kernel" class="kernel-select">
                        <el-option label="RBF (径向基函数)" value="RBF" />
                        <el-option label="Linear (线性核)" value="LINEAR" />
                    </el-select>
                </div>
                <div class="option-item">
                    <label>训练集比例：</label>
                    <el-slider 
                        v-model="svmParams.trainRatio" 
                        :min="0.5" 
                        :max="0.9" 
                        :step="0.1" 
                        show-input 
                        :marks="{
                            0.5: '50%',
                            0.7: '70%',
                            0.9: '90%'
                        }" 
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
    selectedLayerName: {
        type: Array,
        required: true
    },
    availableLayers: {
        type: Array,
        required: true
    },
    clusterCounts: {
        type: Object,
        required: true
    },
    currentTool: {
        type: String,
        required: true
    },
    rfParams: {
        type: Object,
        required: true
    },
    // 添加 SVM 参数
    svmParams: {
        type: Object,
        required: true
    }
});
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
