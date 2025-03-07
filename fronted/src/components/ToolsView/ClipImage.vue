<template>
    <div class="clip-settings">
        <div class="clip-boundary-select">
            <h4>Select Clip Boundary</h4>
            <el-select v-model="selectedBoundary" placeholder="Select Clip Boundary" class="boundary-select">
                <el-option v-for="layer in vectorLayers" :key="layer.id" :label="layer.name" :value="layer.id">
                    <span style="float: left">{{ layer.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                        {{ layer.type === 'vector' ? 'Vector' : layer.type === 'Raster' ? 'Raster' : 'Manual Polygon' }}
                    </span>
                </el-option>
            </el-select>
        </div>

        <div class="no-boundary-tip" v-if="vectorLayers.length === 0">
            <el-alert title="No available clip boundaries" type="warning"
                description="Please add vector layers or draw a polygon first" show-icon :closable="false" />
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

// 获取所有可用的矢量图层和栅格图层
const vectorLayers = computed(() => {
    return props.mapView.layers.filter(layer =>
        layer.type === 'vector' ||
        layer.type === 'Raster' ||  // 添加栅格图层
        (layer.type === 'manual' && layer.geometryType === 'Polygon')
    )
})

// 暴露给父组件的方法
defineExpose({
    getClipParams: () => {
        const selectedLayer = vectorLayers.value.find(l => l.id === selectedBoundary.value)
        if (!selectedLayer) return { clipLayer: null }
        console.log('ClipImgae.vue-getClipParams-selectedLayer', selectedLayer);

        // 如果是栅格图层，只传递必要的信息
        if (selectedLayer.type === 'Raster' || selectedLayer.type === 'vector') {
            return {
                clipLayer: {
                    id: selectedLayer.id,
                    type: selectedLayer.type
                }
            }
        }

        // 如果是矢量图层，返回原有的几何信息
        return {
            clipLayer: {
                geometry: selectedLayer.geometry,
                features: selectedLayer.features,
                type: selectedLayer.type
            }
        }
    }
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