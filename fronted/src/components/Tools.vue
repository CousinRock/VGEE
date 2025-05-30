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
                                <el-input v-model="customDatasetId" placeholder="Enter Dataset ID" size="small"
                                    @keyup.enter="handleCustomIdSearch">
                                    <template #append>
                                        <el-button @click="handleCustomIdSearch">Search</el-button>
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
    <el-dialog v-model="showLayerSelect" :title="'Select the layers to process'" :width="[TOOL_IDS.CLASSIFICATION.KMEANS,
    TOOL_IDS.RASTER_OPERATION.CALCULATOR,
    TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME,
    TOOL_IDS.SEGMENT.TEXT_SEGMENT, TOOL_IDS].includes(currentTool?.id) ? '800px' : '400px'" width="800px">
        <div class="layer-select-content" :class="{
            'with-settings': [TOOL_IDS.CLASSIFICATION.KMEANS,
            TOOL_IDS.RASTER_OPERATION.CALCULATOR,
            TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME,
            TOOL_IDS.SEGMENT.TEXT_SEGMENT].includes(currentTool?.id)
        }">
            <div class="layer-select-left">
                <!-- 添加全选复选框 -->
                <div class="select-all-option">
                    <el-checkbox v-model="selectAll" @change="handleSelectAllChange" :indeterminate="isIndeterminate"
                        :disabled="!availableLayers.length">
                        Select All
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
                || currentTool?.id === TOOL_IDS.RASTER_OPERATION.STATISTICS
                || currentTool?.id === TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME
                || currentTool?.id === TOOL_IDS.RASTER_OPERATION.CLIP
                || currentTool?.id === TOOL_IDS.SEGMENT.TEXT_SEGMENT
                || currentTool?.id === TOOL_IDS.RASTER_OPERATION.OTSU
                || currentTool?.id === TOOL_IDS.PREPROCESSING.GENERATE_RANDOM_POINTS
                || currentTool?.id === TOOL_IDS.RASTER_OPERATION.EXTRACT
                || currentTool?.id === TOOL_IDS.RASTER_OPERATION.CANNY
                || currentTool?.id === TOOL_IDS.RASTER_OPERATION.TIF2VECTOR) && selectedLayerName.length > 0"
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

                <!-- AI 工具设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.SEGMENT.TEXT_SEGMENT">
                    <AiTools ref="aiToolsRef" :selectedLayerName="selectedLayerName" :availableLayers="availableLayers"
                        :currentTool="currentTool.id" />
                </div>

                <!-- 裁剪设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.CLIP">
                    <ClipImage ref="clipImageRef" :mapView="props.mapView" />
                </div>

                <!-- 栅格统计设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.STATISTICS">
                    <RasterStatistics ref="rasterStatisticsRef" :selectedLayerName="selectedLayerName"
                        :availableLayers="availableLayers" :layerBands="layerBands" />
                </div>

                <!-- OTSU 设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.OTSU">
                    <Otsu 
                        ref="otsuRef"
                        :selectedLayerName="selectedLayerName"
                        :layerBands="layerBands"
                    />
                </div>
                <!-- 生成随机点 -->
                <div v-if="currentTool?.id === TOOL_IDS.PREPROCESSING.GENERATE_RANDOM_POINTS">
                    <RandomPoints ref="randomPointsRef" :selectedLayerName="selectedLayerName"
                    :availableLayers="availableLayers"/>
                </div>
                <!-- 提取值组件 -->
                <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.EXTRACT">
                    <ExtractValues ref="extractValuesRef" :mapView="props.mapView" />
                </div>

                <!-- Canny 边缘检测设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.CANNY">
                    <CannyEdge 
                        ref="cannyEdgeRef"
                        :selectedLayerName="selectedLayerName"
                        :layerBands="layerBands"
                    />
                </div>

                <!-- TIF to Vector 设置 -->
                <div v-if="currentTool?.id === TOOL_IDS.RASTER_OPERATION.TIF2VECTOR">
                    <Tif2Vec ref="tif2VecRef" :selectedLayerName="selectedLayerName" :mapView="props.mapView" />
                </div>

            </div>
        </div>

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showLayerSelect = false">Cancel</el-button>
                <el-button type="primary" :loading="isProcessing" @click="handleLayerSelect">
                    {{ isProcessing ? 'Processing...' : 'Confirm' }}
                </el-button>
            </span>
        </template>
    </el-dialog>

    <!-- 搜索数据 -->
    <SearchResults ref="searchResultsRef" />
    <!-- 上传数据 -->
    <UploadData ref="uploadDataRef" :mapView="mapView" />
    <!-- 定位组件 -->
    <LocationSearch ref="locationSearchRef" :mapView="props.mapView" />

    
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
import RasterStatistics from './ToolsView/RasterStatistics.vue'
import UploadData from './ToolsView/UploadData.vue'
import RenameBands from './ToolsView/RenameBands.vue'
import AiTools from './ToolsView/AiTools.vue'
import LocationSearch from './ToolsView/LocationSearch.vue'
import ClipImage from './ToolsView/ClipImage.vue'
import Otsu from './ToolsView/Otsu.vue'
import RandomPoints from './ToolsView/RandomPoints.vue'
import ExtractValues from './ToolsView/ExtractValues.vue'
import CannyEdge from './ToolsView/CannyEdge.vue'
import Tif2Vec from './ToolsView/Tif2Vec.vue'
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
// AI 工具
const aiToolsRef = ref(null)
// 定位组件
const locationSearchRef = ref(null)
// 裁剪组件
const clipImageRef = ref(null)
// 添加统计组件的引用
const rasterStatisticsRef = ref(null)
// OTSU 组件
const otsuRef = ref(null)
//生成随机点
const randomPointsRef = ref(null)
// 提取值组件
const extractValuesRef = ref(null)
// Canny 边缘检测组件
const cannyEdgeRef = ref(null)
// TIF to Vector 组件
const tif2VecRef = ref(null)


// 添加 toolParams 计算属性
const toolParams = computed(() => {
    if (!currentTool.value) return null

    switch (currentTool.value.id) {
        case TOOL_IDS.CLASSIFICATION.KMEANS://K-means
            return macLeaClassifyRef.value?.classifyParams?.clusterCounts || {}
        case TOOL_IDS.CLASSIFICATION.RANDOM_FOREST://随机森林
            return macLeaClassifyRef.value?.classifyParams?.rfParams || {}
        case TOOL_IDS.CLASSIFICATION.SVM://SVM
            return macLeaClassifyRef.value?.classifyParams?.svmParams || {}
        case TOOL_IDS.RASTER_OPERATION.CALCULATOR://栅格计算器
            return rasterCalculatorRef.value?.calculatorParams || {}
        case TOOL_IDS.RASTER_OPERATION.STATISTICS://栅格统计
            return rasterStatisticsRef.value?.statisticsParams || {}
        case TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME://重命名波段
            return renameBandsRef.value?.renameBandsParams?.bands || []
        case TOOL_IDS.SEGMENT.TEXT_SEGMENT://AI工具
            return aiToolsRef.value?.aiParams?.langSam || {}
        case TOOL_IDS.RASTER_OPERATION.CLIP:
            return clipImageRef.value?.getClipParams() || {}
        case TOOL_IDS.RASTER_OPERATION.OTSU:
            return otsuRef.value?.getParams() || {}
        case TOOL_IDS.PREPROCESSING.GENERATE_RANDOM_POINTS:
            return randomPointsRef.value?.getParams()||{}
        case TOOL_IDS.RASTER_OPERATION.EXTRACT:
            return extractValuesRef.value?.getParams() || {}
        case TOOL_IDS.RASTER_OPERATION.CANNY:
            return cannyEdgeRef.value?.getParams() || {}
        case TOOL_IDS.RASTER_OPERATION.TIF2VECTOR:
            return tif2VecRef.value?.getParams() || {}
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
            case TOOL_IDS.UPLOAD.ASSET:
                uploadDataRef.value.showAssetsDialog = true
                await uploadDataRef.value.loadAssets()
                break
            case TOOL_IDS.UPLOAD.LANDSAT_TIMESERIES:
            case TOOL_IDS.UPLOAD.SENTINEL2_TIMESERIES:
                uploadDataRef.value.showTimeseriesDialogMethod(tool.id)
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
            case TOOL_IDS.LOCATION.LOCALIZE:
                locationSearchRef.value.showDialog = true
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
        ElMessage.warning('Please select at least one layer')
        return
    }

    try {
        const result = await ToolService.processLayerSelect(
            selectedLayerName.value,
            currentTool.value,
            props.mapView,
            toolParams.value,
            isProcessing,
            { 
                rasterStatisticsRef: rasterStatisticsRef.value,
                extractValuesRef: extractValuesRef.value
            }
        )

        // 根据工具配置决定是否关闭窗口
        const toolConfig = TOOLS_CONFIG.getToolById(currentTool.value.id)
        if (result && !toolConfig.keepWindowOpen) {
            showLayerSelect.value = false
        }
    } catch (error) {
        console.error('Error handling layer select:', error)
        ElMessage.error('Processing failed')
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
        || currentTool.value?.id === TOOL_IDS.PREPROCESSING.IMAGE_BANDS_RENAME
        || currentTool.value?.id == TOOL_IDS.RASTER_OPERATION.STATISTICS
        || currentTool.value?.id == TOOL_IDS.RASTER_OPERATION.OTSU) {
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
</script>

<style src="../styles/tools.css"></style>