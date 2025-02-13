<template>
    <div class="upload-data-content">
        <!-- 添加资产选择对话框 -->
        <el-dialog v-model="showAssetsDialog" :title="selectedAsset ? `选择资产: ${selectedAsset.name}` : '选择资产'"
            :width="'400px'" >
            <div class="assets-select-content">
                <el-tree :data="assetsList" :props="{
                    label: 'name',
                    children: 'children'
                }" @node-click="handleAssetSelect" node-key="id" :default-expand-all="false" :highlight-current="true">
                    <template #default="{ node, data }">
                        <span class="custom-tree-node">
                            <span>
                                <i :class="data.type === 'FOLDER' ? 'el-icon-folder' : 'el-icon-document'" />
                                {{ data.name }}
                            </span>
                            <el-tooltip v-if="data.description" :content="data.description" placement="right">
                                <i class="el-icon-info" />
                            </el-tooltip>
                        </span>
                    </template>
                </el-tree>
            </div>

            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showAssetsDialog = false">取消</el-button>
                    <el-button type="primary" :loading="isLoadingAssets" @click="confirmAssetSelect">
                        {{ isLoadingAssets ? '添加中...' : '确定' }}
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <!-- Landsat时间序列对话框 -->
        <el-dialog v-model="showLandsatTimeseriesDialog" title="添加 Landsat 时间序列" width="400px">
            <div class="upload-form">
                <el-form :model="form" label-width="120px">
                    <el-form-item label="开始日期">
                        <el-date-picker 
                            v-model="form.startDate"
                            type="date"
                            placeholder="选择开始日期"
                            format="YYYY-MM-DD"
                            value-format="YYYY-MM-DD">
                        </el-date-picker>
                    </el-form-item>
                    
                    <el-form-item label="结束日期">
                        <el-date-picker 
                            v-model="form.endDate"
                            type="date"
                            placeholder="选择结束日期"
                            format="YYYY-MM-DD"
                            value-format="YYYY-MM-DD">
                        </el-date-picker>
                    </el-form-item>
                    
                    <el-form-item label="云量阈值(%)">
                        <el-slider 
                            v-model="form.cloudCover"
                            :min="0"
                            :max="100"
                            :step="1">
                        </el-slider>
                    </el-form-item>
                </el-form>
            </div>

            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showLandsatTimeseriesDialog = false">取消</el-button>
                    <el-button type="primary" @click="submitForm" :loading="isSubmitting">
                        {{ isSubmitting ? '添加中...' : '确定' }}
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'
import { 
    onLoadAssets, 
    onHandleAssetSelect, 
    onConfirmAssetSelect,
    onSubmitLandsatTimeseries 
} from '../../service/headTools/upload'

// 定义 props
const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})

// 状态变量
const showAssetsDialog = ref(false)
const showLandsatTimeseriesDialog = ref(false)
const assetsList = ref([])
const selectedAsset = ref(null)
const isLoadingAssets = ref(false)
const isSubmitting = ref(false)
const form = ref({
    startDate: '',
    endDate: '',
    cloudCover: 20
})

// 修改 loadAssets 方法
const loadAssets = async (folder = null) => {
    await onLoadAssets(folder, isLoadingAssets, assetsList)
}

// 修改资产选择处理方法
const handleAssetSelect = async (data) => {
    await onHandleAssetSelect(data, selectedAsset)
}

// 修改确认选择方法
const confirmAssetSelect = async () => {
    await onConfirmAssetSelect(selectedAsset, showAssetsDialog, isLoadingAssets, props.mapView)
}

// 提交 Landsat 时间序列表单
const submitForm = async () => {
    await onSubmitLandsatTimeseries(form, props.mapView, showLandsatTimeseriesDialog, isSubmitting)
}

// 暴露方法和状态给父组件
defineExpose({
    showAssetsDialog,
    showLandsatTimeseriesDialog,
    loadAssets
})
</script>

<style scoped>
.upload-form {
    padding: 20px;
}
</style>
