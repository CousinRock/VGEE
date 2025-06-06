<template>
    <div class="upload-data-content">
        <!-- 添加资产选择对话框 -->
        <el-dialog v-model="showAssetsDialog"
            :title="selectedAsset ? `Select Asset: ${selectedAsset.name}` : 'Select Asset'" :width="'400px'">
            <div class="assets-header">
                <el-button @click="refreshAssetsList" :loading="isLoadingAssets" type="primary" size="small">
                    <i class="fas fa-sync-alt"></i> Refresh
                </el-button>
            </div>
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
                            <span class="asset-actions">
                                <el-tooltip v-if="data.description" :content="data.description" placement="right">
                                    <i class="el-icon-info" />
                                </el-tooltip>
                                <el-button type="text" size="small" @click.stop="openRenameDialog(data)"
                                    :loading="isLoadingAssets" :disabled="isLoadingAssets">
                                    <i class="fas fa-edit"></i>
                                </el-button>
                                <el-popconfirm
                                    :title="`Are you sure you want to delete ${data.name} ${data.type === 'FOLDER' ? 'and all its contents' : ''}?`"
                                    @confirm="deleteAsset(data)">
                                    <template #reference>
                                        <el-button type="text" size="small" class="delete-btn"
                                            :loading="isLoadingAssets" :disabled="isLoadingAssets">
                                            <i class="fas fa-trash"></i>
                                        </el-button>
                                    </template>
                                </el-popconfirm>
                            </span>
                        </span>
                    </template>
                </el-tree>
            </div>

            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showAssetsDialog = false">Cancel</el-button>
                    <el-button type="primary" :loading="isLoadingAssets" @click="confirmAssetSelect">
                        {{ isLoadingAssets ? 'Adding...' : 'Confirm' }}
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 时间序列对话框 -->
        <el-dialog v-model="showTimeseriesDialog" :title="`Add ${satelliteType} Time Series`" width="400px">
            <div class="upload-form">
                <el-form :model="form" label-width="100px">
                    <el-form-item label="Time Frequency">
                        <el-select v-model="form.frequency" placeholder="Select Time Frequency">
                            <el-option label="Yearly" value="year" />
                            <el-option label="Monthly" value="month" />
                        </el-select>
                    </el-form-item>

                    <el-form-item label="Time Interval">
                        <el-input-number v-model="form.interval" :min="1" :max="12" :step="1"
                            controls-position="right" />
                    </el-form-item>

                    <el-form-item label="Start Date">
                        <el-date-picker v-model="form.startDate" type="date" placeholder="Select Start Date"
                            format="YYYY-MM-DD" value-format="YYYY-MM-DD">
                        </el-date-picker>
                    </el-form-item>

                    <el-form-item label="End Date">
                        <el-date-picker v-model="form.endDate" type="date" placeholder="Select End Date"
                            format="YYYY-MM-DD" value-format="YYYY-MM-DD">
                        </el-date-picker>
                    </el-form-item>

                    <el-form-item label="Cloud Cover Settings" class="cloud-settings">
                        <div class="cloud-control-group">
                            <el-slider v-model="form.cloudCover" :min="0" :max="100" :step="1" class="cloud-slider">
                            </el-slider>
                            <div class="cloud-mask-option">
                                <el-checkbox v-model="form.apply_fmask">
                                    Enable Cloud Mask
                                </el-checkbox>
                                <el-tooltip
                                    content="For Landsat and Sentinel-2 data, the cloud mask will be automatically applied"
                                    placement="right">
                                    <i class="fas fa-question-circle"></i>
                                </el-tooltip>
                            </div>
                        </div>
                    </el-form-item>
                </el-form>
            </div>

            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showTimeseriesDialog = false">Cancel</el-button>
                    <el-button type="primary" @click="submitForm" :loading="isSubmitting">
                        {{ isSubmitting ? 'Adding...' : 'Confirm' }}
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 重命名对话框 -->
        <el-dialog v-model="showRenameDialog" title="Rename Asset" width="400px">
            <el-form :model="renameForm">
                <el-form-item label="New Name">
                    <el-input v-model="renameForm.newName" placeholder="Enter new name"></el-input>
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showRenameDialog = false">Cancel</el-button>
                    <el-button @click="handleRename" :loading="isLoadingAssets">
                        Confirm
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
    onSubmitTimeseries,
    refreshAssets,
    onDeleteAsset,
    onRenameAsset
} from '../../service/headTools/upload'
import { TOOL_IDS } from '../../config/tools-config'
import { ElMessage } from 'element-plus'


// 定义 props
const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})

// 状态变量
const showAssetsDialog = ref(false)
const showTimeseriesDialog = ref(false)
const showRenameDialog = ref(false)  // 对话框显示状态
const assetsList = ref([])
const selectedAsset = ref(null)
const isLoadingAssets = ref(false)
const isSubmitting = ref(false)
const form = ref({
    startDate: '',
    endDate: '',
    cloudCover: 20,
    frequency: 'year',  // 默认为年度
    interval: 1,  // 默认间隔为1
    apply_fmask: false
})

// 添加卫星类型状态
const satelliteType = ref('Landsat')

// 添加当前工具ID状态
const currentToolId = ref(null)

// 添加重命名相关的状态
const renameForm = ref({
    newName: '',
    asset: null
})

// 添加刷新方法
const refreshAssetsList = async () => {
    await refreshAssets(isLoadingAssets, assetsList);
}

// 修改 loadAssets 方法
const loadAssets = async () => {
    await onLoadAssets(isLoadingAssets, assetsList);
}

// 修改资产选择处理方法
const handleAssetSelect = async (data) => {
    await onHandleAssetSelect(data, selectedAsset)
}

// 修改确认选择方法
const confirmAssetSelect = async () => {
    await onConfirmAssetSelect(selectedAsset, showAssetsDialog, isLoadingAssets, props.mapView)
}

// 修改显示对话框的方法
const showTimeseriesDialogMethod = (toolId) => {
    currentToolId.value = toolId  // 保存当前工具ID
    if (toolId === TOOL_IDS.UPLOAD.LANDSAT_TIMESERIES) {
        satelliteType.value = 'Landsat'
    } else if (toolId === TOOL_IDS.UPLOAD.SENTINEL2_TIMESERIES) {
        satelliteType.value = 'Sentinel-2'
    }
    showTimeseriesDialog.value = true
}

// 提交表单
const submitForm = async () => {
    await onSubmitTimeseries(
        form,
        props.mapView,
        showTimeseriesDialog,
        isSubmitting,
        currentToolId.value,  // 传递工具ID
    )
}

// 添加删除资产方法
const deleteAsset = async (asset) => {
    await onDeleteAsset(asset, isLoadingAssets, assetsList)
};

// 重命名为 openRenameDialog
const openRenameDialog = (asset) => {
    renameForm.value.newName = asset.name
    renameForm.value.asset = asset
    showRenameDialog.value = true
}

// 处理重命名
const handleRename = async () => {
    if (!renameForm.value.newName.trim()) {
        ElMessage.warning('Please enter a new name')
        return
    }

    await onRenameAsset(
        renameForm.value.asset,
        renameForm.value.newName,
        isLoadingAssets,
        assetsList
    )
    showRenameDialog.value = false
}

// 暴露方法和状态给父组件
defineExpose({
    showAssetsDialog,
    showTimeseriesDialog,
    loadAssets,
    showTimeseriesDialogMethod
})
</script>

<style scoped>
.upload-form {
    padding: 20px;
}

/* 修改云量设置相关样式 */
.cloud-settings {
    margin-bottom: 22px;
}

.cloud-control-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.cloud-slider {
    flex: 1;
    margin-right: 16px;
}

.cloud-mask-option {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 4px;
}

.cloud-mask-option i {
    color: #909399;
    cursor: help;
    font-size: 14px;
}

.assets-container {
    padding: 0 20px;
}

.asset-node {
    display: flex;
    align-items: center;
    gap: 8px;
}

.assets-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.current-path {
    font-size: 14px;
    color: #666;
}

.custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-right: 8px;
}

.asset-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}

.asset-actions .el-button {
    padding: 2px 4px;
}

.delete-btn {
    color: #F56C6C;
}

.delete-btn:hover {
    color: #f89898;
}
</style>
