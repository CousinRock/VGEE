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
    </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'
import { onLoadAssets, onHandleAssetSelect, onConfirmAssetSelect } from '../../service/headTools/upload'

// 定义 props
const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})

// 状态变量
const showAssetsDialog = ref(false)
const assetsList = ref([])
const selectedAsset = ref(null)
const isLoadingAssets = ref(false)

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

// 暴露方法和状态给父组件
defineExpose({
    showAssetsDialog,
    loadAssets
})
</script>
