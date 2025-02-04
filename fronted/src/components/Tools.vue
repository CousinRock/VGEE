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
                    <el-checkbox v-model="selectAll" @change="handleSelectAllChange" :indeterminate="isIndeterminate">
                        全选
                    </el-checkbox>
                </div>

                <el-checkbox-group v-model="selectedLayerName" @change="handleCheckedLayersChange">
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
                    <MacLeaClassify :selectedLayerName="selectedLayerName" :availableLayers="availableLayers"
                        :clusterCounts="clusterCounts" :currentTool="currentTool.id" />
                </div>


                <!-- 随机森林设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.CLASSIFICATION.RANDOM_FOREST
                    || currentTool?.id === TOOL_IDS.CLASSIFICATION.SVM">
                    <MacLeaClassify :selectedLayerName="selectedLayerName" :availableLayers="availableLayers"
                        :clusterCounts="clusterCounts" :rfParams="rfParams" :svmParams="svmParams"
                        :currentTool="currentTool.id" />

                </div>

                <!-- 栅格计算器设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.CALCULATOR">
                    <RasterCalculator :selectedLayerName="selectedLayerName" :availableLayers="availableLayers"
                        :layerBands="layerBands" @update-expression="calculatorExpression = $event"
                        @update-calcumode="calculatorMode = $event" />

                </div>
                <!-- <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.CALCULATOR">
                    <RasterCalculator ref="rasterCalculatorRef" :mapView="mapView" />
                </div> -->

                <!-- 重命名波段 -->
                <div v-if="currentTool?.id === TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME">
                    <RenameBands :availableBands="ToolService.getCommonBands(layerBands)"
                        @update:bands="bands = $event" />
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
    <SearchResults v-if="showSearchResults" :datasets="searchResults" @select="onDatasetSelect"
        @close="showSearchResults = false" />
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

// 定义 emit 事件
const emit = defineEmits(['dataset-selected'])

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

//机器学习分类
const clusterCounts = ref({})  // 用于存储每个图层的分类数量
const rfParams = ref({})  // 用于存储随机森林参数
const svmParams = ref({});

//栅格计算器
const calculatorExpression = ref('')
const layerBands = ref({})  // 存储每个图层的波段信息
const calculatorMode = ref('single')

//搜索数据
const showSearchResults = ref(false)
const searchResults = ref([])
const selectedDataset = ref(null)
const customDatasetId = ref('')
const activeSearchId = ref(false)

//上传数据
const uploadDataRef = ref(null)

const rasterCalculatorRef = ref(null)

// 添加 bands 状态变量
const bands = ref({})  // 用于存储波段映射信息

// 添加 toolParams 计算属性
const toolParams = computed(() => {
    if (!currentTool.value) return null

    switch (currentTool.value.id) {
        case TOOL_IDS.CLASSIFICATION.KMEANS:
            return clusterCounts.value
        case TOOL_IDS.CLASSIFICATION.RANDOM_FOREST:
            return rfParams.value
        case TOOL_IDS.CLASSIFICATION.SVM:
            return svmParams.value
        case TOOL_IDS.RASTER_OPERATION.CALCULATOR:
            return {
                expression: calculatorExpression.value,
                mode: calculatorMode.value
            }
        case TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME:
            return bands.value
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

// 在 handleToolClick 之前添加 handleSpecialTool 方法
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
                searchResults.value = datasets
                showSearchResults.value = true
                break
            case TOOL_IDS.SEARCH.ID:
                activeSearchId.value = !activeSearchId.value
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

    selectedLayerName.value = []  // 清空之前的选择
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
    selectedLayerName.value = val ? availableLayers.value.map(layer => layer.id) : []
    isIndeterminate.value = false
}

// 处理选中图层变化
const handleCheckedLayersChange = (value) => {
    const checkedCount = value.length
    selectAll.value = checkedCount === availableLayers.value.length
    isIndeterminate.value = checkedCount > 0 && checkedCount < availableLayers.value.length
}

// 在显示对话框时重置状态
watch(showLayerSelect, (newVal) => {
    if (newVal) {
        selectAll.value = false
        isIndeterminate.value = false
        selectedLayerName.value = []
        // 重置分类数量
        clusterCounts.value = {}
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

// 处理数据集选择
const onDatasetSelect = (dataset) => {
    SearchDataService.handleDatasetSelect(dataset, selectedDataset)
}

// 添加处理ID搜索的方法
const handleCustomIdSearch = () => {
    SearchDataService.handleIdSearch(customDatasetId.value, searchResults, showSearchResults)
}

// 替换 menuItems 的使用
const menuItems = computed(() => TOOLS_CONFIG.getMenuItems())

// 替换工具配置的获取方式
const toolConfig = computed(() => currentTool.value ? TOOLS_CONFIG.getToolById(currentTool.value.id) : null)
</script>

<style src="../styles/tools.css"></style>