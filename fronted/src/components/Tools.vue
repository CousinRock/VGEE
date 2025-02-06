<template>
    <!-- 工具菜单 -->
    <div class="tools-menu">
        <div class="nav-item" v-for="item in menuItems" :key="item.id" @click="toggleMenu(item)"
            :class="{ active: activeMenu === item.id }">
            <span>{{ item.label }}</span>
            <i class="fas fa-angle-down" v-if="item.children"></i>
            <!-- 下拉菜单 -->
            <div class="submenu" v-if="item.children && showSubmenu === item.id">
                <div class="submenu-item" v-for="child in item.children" :key="child.id"
                    @click.stop="handleSubMenuClick(child)">
                    <i :class="child.icon"></i>
                    <span>{{ child.label }}</span>
                    <!-- 显示工具的子菜单 -->
                    <div class="submenu" v-if="child.children && activeSubMenu === child.id">
                        <div class="submenu-item" v-for="tool in child.children" :key="tool.id"
                            @click.stop="handleToolClick(tool)" :class="{ 'processing': isProcessing }">
                            <i :class="tool.icon"></i>
                            <span>{{ tool.label }}</span>
                            <!-- 为 search-data-id 添加输入框，只在激活时显示 -->
                            <div v-if="tool.id === 'search-data-id' && activeSearchId" class="id-search" @click.stop>
                                <el-input v-model="customDatasetId" placeholder="输入数据集ID" size="small"
                                    @keyup.enter="handleCustomIdSearch">
                                    <template #append>
                                        <el-button @click="handleCustomIdSearch">搜索</el-button>
                                    </template>
                                </el-input>
                            </div>
                            <i class="fas fa-spinner fa-spin" v-if="isProcessing"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 修改图层选择对话框 -->
    <el-dialog v-model="showLayerSelect" :title="'选择需要处理的图层'"
        :width="['kmeans', 'raster-calculator', 'image-bands-rename'].includes(currentTool?.id) ? '800px' : '400px'"
        width="800px">
        <div class="layer-select-content"
            :class="{ 'with-settings': ['kmeans', 'raster-calculator', 'image-bands-rename'].includes(currentTool?.id) }">
            <div class="layer-select-left">
                <!-- 添加全选复选框 -->
                <div class="select-all-option">
                    <el-checkbox v-model="selectAll" @change="handleSelectAllChange" :indeterminate="isIndeterminate"
                        :disabled="!availableLayers.length">
                        全选
                    </el-checkbox>
                </div>

                <el-checkbox-group v-model="selectedLayerName" @change="handleCheckedLayersChange"
                    :disabled="!availableLayers.length">
                    <div v-for="layer in availableLayers" :key="layer.id" class="layer-option">
                        <el-checkbox :label="layer.id">{{ layer.name }}</el-checkbox>
                    </div>
                </el-checkbox-group>
            </div>

            <!-- 右侧分类设置区域 -->
            <div v-if="(currentTool?.id === TOOL_IDS.CLASSIFICATION.KMEANS
                || currentTool?.id === TOOL_IDS.CLASSIFICATION.RANDOM_FOREST
                || currentTool?.id === TOOL_IDS.CLASSIFICATION.SVM
                || currentTool?.id === TOOL_IDS.RASTER_OPERATION.CALCULATOR
                || currentTool?.id === TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME) && selectedLayerName.length > 0"
                class="layer-select-right">

                <!-- K-means 设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.CLASSIFICATION.KMEANS">
                    <MacLeaClassify ref="macLeaClassifyRef" :selectedLayerName="selectedLayerName"
                        :availableLayers="availableLayers" :currentTool="currentTool.id" />
                </div>

                <!-- 随机森林、svm设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.CLASSIFICATION.RANDOM_FOREST
                    || currentTool?.id === TOOL_IDS.CLASSIFICATION.SVM">
                    <MacLeaClassify ref="macLeaClassifyRef" :selectedLayerName="selectedLayerName"
                        :availableLayers="availableLayers" :currentTool="currentTool.id" />
                </div>

                <!-- 栅格计算器设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.CALCULATOR">
                    <RasterCalculator ref="rasterCalculatorRef" :selectedLayerName="selectedLayerName"
                        :availableLayers="availableLayers" :layerBands="layerBands" />
                </div>

                <!-- 重命名波段 -->
                <div v-if="currentTool?.id === TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME">
                    <RenameBands ref="renameBandsRef" :availableBands="ToolService.getCommonBands(layerBands)"
                        :layerBands="layerBands" />
                </div>

            </div>
        </div>

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showLayerSelect = false">取消</el-button>
                <el-button type="primary" :loading="isProcessing" @click="handleLayerSelect">
                    {{ isProcessing ? '处理中...' : '确定' }}
                </el-button>
            </span>
        </template>
    </el-dialog>

    <!-- 搜索数据 -->
    <SearchResults ref="searchResultsRef" />
    <!-- 上传数据 -->
    <UploadData ref="uploadDataRef" :mapView="mapView" />
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { TOOLS_CONFIG, TOOL_IDS } from '../config/tools-config'

//自定义工具
import * as ToolService from '../service/headTools/tool'// 导入工具服务
import * as SearchDataService from '../service/headTools/searchData'// 导入搜索数据服务

// 导入工具视图组件
import SearchResults from './ToolsView/SearchResults.vue'
import RasterCalculator from './ToolsView/RasterCalculator.vue'
import MacLeaClassify from './ToolsView/MacLeaClassify.vue'
import UploadData from './ToolsView/UploadData.vue'
import RenameBands from './ToolsView/RenameBands.vue'

const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})


//////////////状态变量///////////////
const activeMenu = ref('')
const showSubmenu = ref('')
const activeSubMenu = ref('')
const isProcessing = ref(false)
const showLayerSelect = ref(false)
const availableLayers = ref([])
const selectedLayerName = ref([])
const currentTool = ref(null)
const selectAll = ref(false)
const isIndeterminate = ref(false)
const layerBands = ref({})  // 存储每个图层的波段信息

//搜索数据
const searchResultsRef = ref(null)
//上传数据
const uploadDataRef = ref(null)
//栅格计算器
const rasterCalculatorRef = ref(null)
//机器学习
const macLeaClassifyRef = ref(null)
//重命名波段
const renameBandsRef = ref(null)

// 添加 toolParams 计算属性
const toolParams = computed(() => {
    if (!currentTool.value) return null

    switch (currentTool.value.id) {
        case TOOL_IDS.CLASSIFICATION.KMEANS:
            return macLeaClassifyRef.value?.classifyParams?.clusterCounts || {}
        case TOOL_IDS.CLASSIFICATION.RANDOM_FOREST:
            return macLeaClassifyRef.value?.classifyParams?.rfParams || {}
        case TOOL_IDS.CLASSIFICATION.SVM:
            return macLeaClassifyRef.value?.classifyParams?.svmParams || {}
        case TOOL_IDS.RASTER_OPERATION.CALCULATOR:
            if (!rasterCalculatorRef.value?.calculatorParams) return {}
            return {
                expression: rasterCalculatorRef.value.calculatorParams.expression || '',
                mode: rasterCalculatorRef.value.calculatorParams.mode || 'single'
            }
        case TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME:
            return renameBandsRef.value?.renameBandsParams?.bands || []
        default:
            return null
    }
})

//////////////状态变量///////////////

// 菜单操作方法
const toggleMenu = (item) => {
    if (showSubmenu.value === item.id) {
        showSubmenu.value = ''
        activeMenu.value = ''
        activeSubMenu.value = ''
    } else {
        showSubmenu.value = item.id
        activeMenu.value = item.id
    }
}

const handleSubMenuClick = (item) => {
    console.log('Tools.vue - handleSubMenuClick - item', item)
    if (item.children) {
        if (activeSubMenu.value === item.id) {
            activeSubMenu.value = ''
        } else {
            activeSubMenu.value = item.id
        }
    } else {
        showSubmenu.value = ''
        activeSubMenu.value = ''
    }
}

// 修改特殊工具处理方法
const handleSpecialTool = async (tool) => {
    try {
        switch (tool.id) {
            case TOOL_IDS.UPLOAD.VECTOR:
                uploadDataRef.value.showAssetsDialog = true
                await uploadDataRef.value.loadAssets()
                break
            case TOOL_IDS.SEARCH.LANDSAT:
            case TOOL_IDS.SEARCH.SENTINEL:
            case TOOL_IDS.SEARCH.MODIS:
            case TOOL_IDS.SEARCH.VIIRS:
            case TOOL_IDS.SEARCH.DEM:
                const datasetType = tool.label
                const datasets = await SearchDataService.searchData(datasetType)
                // 组件一直存在，可以直接调用方法
                searchResultsRef.value.updateSearchResults(datasets)
                break
            case TOOL_IDS.SEARCH.ID:
                searchResultsRef.value.toggleIdSearch()
                break
            default:
                ElMessage.warning('该功能尚未实现')
        }
    } catch (error) {
        console.error('Error handling special tool:', error)
        ElMessage.error('工具执行失败')
    }
}

// 工具处理方法
const handleToolClick = async (tool) => {
    const toolConfig = TOOLS_CONFIG.getToolById(tool.id)
    console.log('Tools.vue-handleToolClick-toolConfig', toolConfig)
    if (!toolConfig) {
        ElMessage.warning('该功能尚未实现')
        return
    }
    console.log('Tools.vue-handleToolClick-tool', tool)
    try {
        if (toolConfig.requireLayers) {
            await commonMethod(tool)
        } else {
            // 处理特殊工具（搜索、上传等）
            await handleSpecialTool(tool)
        }
    } catch (error) {
        console.error('Error handling tool click:', error)
        ElMessage.error('工具执行失败')
    }
}

//通用函数
const commonMethod = async (tool) => {
    const layers = await ToolService.getAvailableLayers()
    if (!layers) return

    // 重置选择状态
    selectedLayerName.value = []
    selectAll.value = false
    isIndeterminate.value = false

    availableLayers.value = layers
    currentTool.value = tool
    showLayerSelect.value = true
}

// 图层选择处理
const handleLayerSelect = async () => {
    if (!selectedLayerName.value.length) {
        ElMessage.warning('请选择至少一个图层')
        return
    }

    try {
        const result = await ToolService.processLayerSelect(
            selectedLayerName.value,
            currentTool.value,
            props.mapView,
            toolParams.value,  // 使用计算属性
            isProcessing
        )

        if (result) {
            showLayerSelect.value = false
        }
    } catch (error) {
        console.error('Error handling layer select:', error)
        ElMessage.error('处理失败')
    }
}

// 处理全选变化
const handleSelectAllChange = (val) => {
    // 添加判断，确保有可用图层时才能全选
    if (val && availableLayers.value.length > 0) {
        selectedLayerName.value = availableLayers.value.map(layer => layer.id)
    } else {
        selectedLayerName.value = []
    }
    isIndeterminate.value = false
}

// 处理选中图层变化
const handleCheckedLayersChange = (value) => {
    // 只有在有可用图层时才更新全选状态
    if (availableLayers.value.length > 0) {
        const checkedCount = value.length
        selectAll.value = checkedCount === availableLayers.value.length
        isIndeterminate.value = checkedCount > 0 && checkedCount < availableLayers.value.length
    } else {
        selectAll.value = false
        isIndeterminate.value = false
    }
}

// 在显示对话框时重置状态
watch(showLayerSelect, (newVal) => {
    if (newVal) {
        // 重置选择状态
        selectAll.value = false
        isIndeterminate.value = false
        selectedLayerName.value = []
    }
})

// 监听选中图层的变化，初始化波段信息
watch(selectedLayerName, async (newVal) => {
    if (currentTool.value?.id === TOOL_IDS.RASTER_OPERATION.CALCULATOR
        || currentTool.value?.id === TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME) {
        for (const layerId of newVal) {
            if (!layerBands.value[layerId]) {

                layerBands.value[layerId] = ToolService.getLayerBands(props.mapView, layerId)
                console.log('Tools.vue - watch - layerBands', layerBands.value)
            }
        }
        // 清理未选中图层的波段信息
        Object.keys(layerBands.value).forEach(layerId => {
            if (!newVal.includes(layerId)) {
                delete layerBands.value[layerId]
            }
        })
    }
});

// 暴露方法父组件
defineExpose({
    closeAllMenus: () => {
        showSubmenu.value = ''
        activeMenu.value = ''
        activeSubMenu.value = ''
    }
})

// 替换 menuItems 的使用
const menuItems = computed(() => TOOLS_CONFIG.getMenuItems())

// 替换工具配置的获取方式
const toolConfig = computed(() => currentTool.value ? TOOLS_CONFIG.getToolById(currentTool.value.id) : null)
</script>

<style src="../styles/tools.css"></style>