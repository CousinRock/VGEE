<template>
    <div class="clip-settings">
        <div class="clip-boundary-select">
            <h4>选择裁剪边界</h4>
            <el-select 
                v-model="selectedBoundary" 
                placeholder="请选择裁剪边界"
                class="boundary-select"
            >
                <el-option
                    v-for="layer in vectorLayers"
                    :key="layer.id"
                    :label="layer.name"
                    :value="layer.id"
                >
                    <span style="float: left">{{ layer.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                        {{ layer.type === 'vector' ? '矢量' : '手绘多边形' }}
                    </span>
                </el-option>
            </el-select>
        </div>

        <div class="no-boundary-tip" v-if="vectorLayers.length === 0">
            <el-alert
                title="没有可用的裁剪边界"
                type="warning"
                description="请先添加矢量图层或绘制多边形"
                show-icon
                :closable="false"
            />
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})

// 选中的裁剪边界
const selectedBoundary = ref('')

// 获取所有可用的矢量图层（包括矢量资产和手绘多边形）
const vectorLayers = computed(() => {
    return props.mapView.layers.filter(layer => 
        layer.type === 'vector' || 
        (layer.type === 'manual' && layer.geometryType === 'Polygon')
    )
})

// 暴露给父组件的方法
defineExpose({
    getClipParams: () => ({
        clipLayer: vectorLayers.value.find(l => l.id === selectedBoundary.value)
    })
})
</script>

<style scoped>
.clip-settings {
    padding: 20px;
}

.clip-boundary-select {
    margin-bottom: 20px;
}

.clip-boundary-select h4 {
    margin: 0 0 10px 0;
    font-size: 14px;
    color: #606266;
}

.boundary-select {
    width: 100%;
}

.no-boundary-tip {
    margin-top: 20px;
}
</style> 