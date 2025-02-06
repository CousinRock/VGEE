<template>
    <div class="ai-tools">
        <h4>AI 工具</h4>
        <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
            <div class="layer-name">
                {{ availableLayers.find(l => l.id === layerId)?.name }}
            </div>

            <div class="option-group">
                <h5>LangSAM 设置</h5>

                <div class="option-item">
                    <label>文本提示：</label>
                    <el-input v-model="aiParams.langSam.textPrompt" placeholder="输入要识别的目标，如：house, tree, water..." />
                </div>

                <div class="option-item">
                    <label>置信度阈值：</label>
                    <el-slider v-model="aiParams.langSam.threshold" :min="0" :max="1" :step="0.01" show-input :marks="{
                        0.2: '0.2',
                        0.5: '0.5',
                        0.8: '0.8'
                    }" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
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
})

// 统一管理AI工具参数
const aiParams = ref({
    langSam: {
        textPrompt: 'house',
        threshold: 0.24
    }
    // 其他AI工具的参数可以在这里添加
})

// 监听参数变化
watch(aiParams, (newVal) => {
    console.log('AiTools.vue - watch - aiParams:', newVal)
}, { deep: true })

// 暴露方法和状态给父组件
defineExpose({
    aiParams
})
</script>

<style scoped>
.ai-tools {
    padding: 15px;
}

.ai-tools h4 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #303133;
}

.layer-option-item {
    margin-bottom: 20px;
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
}

.layer-name {
    font-weight: bold;
    margin-bottom: 15px;
    color: #409EFF;
    font-size: 14px;
}

.option-group {
    background-color: white;
    padding: 15px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.option-group h5 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #606266;
}

.option-item {
    margin-bottom: 20px;
}

.option-item:last-child {
    margin-bottom: 0;
}

.option-item label {
    display: block;
    margin-bottom: 8px;
    color: #606266;
    font-size: 14px;
}

.el-input {
    width: 100%;
}

.el-slider {
    margin-top: 8px;
}

/* 提示信息样式 */
.parameter-hint {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.4;
}
</style>