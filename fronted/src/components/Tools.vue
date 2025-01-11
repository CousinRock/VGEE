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
                            <div v-if="tool.id === 'search-data-id' && activeSearchId" 
                                class="id-search" 
                                @click.stop
                            >
                                <el-input 
                                    v-model="customDatasetId"
                                    placeholder="输入数据集ID"
                                    size="small"
                                    @keyup.enter="handleCustomIdSearch"
                                >
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
    <el-dialog v-model="showLayerSelect" :title="getDialogTitle"
        :width="['kmeans', 'raster-calculator', 'image-bands-rename'].includes(currentTool?.id) ? '800px' : '400px'" width="800px">
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
            <div v-if="(currentTool?.id === 'kmeans' || currentTool?.id === 'random-forest' || 
            currentTool?.id === 'raster-calculator' || currentTool?.id === 'image-bands-rename') && selectedLayerName.length > 0"
                class="layer-select-right">
                
                <!-- K-means 设置 -->
                <div v-if="currentTool?.id === 'kmeans'">
                    <MacLeaClassify 
                        :selectedLayerName="selectedLayerName" 
                        :availableLayers="availableLayers" 
                        :clusterCounts="clusterCounts" 
                        currentTool="kmeans" 
                    />
                </div>

                <!-- 随机森林设置 -->
                <div v-if="currentTool?.id === 'random-forest'">
                    <MacLeaClassify 
                        :selectedLayerName="selectedLayerName" 
                        :availableLayers="availableLayers" 
                        :clusterCounts="clusterCounts" 
                        :rfParams="rfParams" 
                        currentTool="random-forest" 
                    />
                </div>

                <!-- 栅格计算器设置 -->
                <div v-if="currentTool?.id === 'raster-calculator'">
                    <RasterCalculator 
                        :selectedLayerName="selectedLayerName" 
                        :availableLayers="availableLayers" 
                        :layerBands="layerBands" 
                        @band-click="handleBandClick"
                        @update-expression="calculatorExpression = $event"
                        @update-calcumode="calculatorMode = $event"
                    />
                </div>

                <!-- 重命名波段 -->
                <div v-if="currentTool?.id === 'image-bands-rename'">
                    <RenameBands :availableBands="ToolService.getCommonBands(layerBands)" />
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
    <SearchResults v-if="showSearchResults" :datasets="searchResults" @select="onDatasetSelect" @close="showSearchResults = false" />
    <!-- 上传数据 -->
    <UploadData ref="uploadDataRef" :mapView="mapView" />
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { menuItems } from '../config/tools-config'

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

// 状态变量
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
const clusterCounts = ref({})  // 用于存储每个图层的分类数量
const showSearchResults = ref(false)
const searchResults = ref([])
const selectedDataset = ref(null)
const customDatasetId = ref('')
const activeSearchId = ref(false)
const uploadDataRef = ref(null)

const calculatorExpression = ref('')
const layerBands = ref({})  // 存储每个图层的波段信息
const calculatorMode = ref('single')

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

// 工具处理方法
const handleToolClick = async (tool) => {
    try {
        // 处理其他工具...
        switch (tool.id) {
            case 'cloud-removal':
            case 'image-filling':
            case 'kmeans':
            // 添加所有指数计算的处理
            case 'ndvi':
            case 'ndwi':
            case 'ndbi':
            case 'evi':
            case 'savi':
            case 'mndwi':
            case 'bsi':
            case 'histogram-equalization':
            case 'random-forest':
            case 'raster-calculator':
            case 'image-bands-rename':
                console.log('Tools.vue - handleToolClick - tool', tool)
                await commonMethod(tool)
                break
            case 'upload-vector-assets':
                uploadDataRef.value.showAssetsDialog = true
                await uploadDataRef.value.loadAssets()
                break              
            // 添加搜索数据的处理逻辑
            case 'search-data-landsat':
            case 'search-data-sentinel':
            case 'search-data-modis':
            case 'search-data-viirs':
            case 'search-data-dem':
                const datasetType = tool.label
                const datasets = await SearchDataService.searchData(datasetType)
                searchResults.value = datasets
                console.log('Tools.vue - handleToolClick - searchResults', searchResults.value)
                showSearchResults.value = true
                break
            case 'search-data-id':
                activeSearchId.value = !activeSearchId.value // 切换输入框的显示状态
                break
            default:
                ElMessage.warning('该功能尚未实现')
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

// 添加对话框标题计算属性
const getDialogTitle = computed(() => {
    if (currentTool.value?.id === 'kmeans') {
        return '选择需要分类的图层'
    }
    return '选择需要处理的图'
})

// 图层选择处理
const handleLayerSelect = async () => {
    if (!selectedLayerName.value.length) {
        ElMessage.warning('请选择至少一个图层')
        return
    }

    try {
        let result
        if (currentTool.value.id === 'raster-calculator') {
            if (!calculatorExpression.value) {
                ElMessage.warning('请输入计算表达式')
                return
            }
            console.log('Tools.vue - handleLayerSelect - calculatorMode:', calculatorMode.value)
            // 添加计算模式参数
            result = await ToolService.processLayerSelect(
                selectedLayerName.value,
                currentTool.value,
                props.mapView,
                {
                    expression: calculatorExpression.value,
                    mode: calculatorMode.value
                },
                isProcessing
            )
        } else if (currentTool.value.id === 'kmeans') {
            // kmeans 处理逻辑
            result = await ToolService.processLayerSelect(
                selectedLayerName.value,
                currentTool.value,
                props.mapView,
                clusterCounts.value,
                isProcessing
            )
        } else if (currentTool.value.id === 'random-forest') {
            // 随机森林处理逻辑
            result = await ToolService.processLayerSelect(
                selectedLayerName.value,
                currentTool.value,
                props.mapView,
                rfParams.value,
                isProcessing
            )
            console.log('Tools.vue - handleLayerSelect - result', result)
        } else {
            // 其他工具处理逻辑
            result = await ToolService.processLayerSelect(
                selectedLayerName.value,
                currentTool.value,
                props.mapView,
                null,       // 如果工具不需要额外参数，传入 null
                isProcessing  // 为所有工具都传入 isProcessing
            )
        }


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

// 监听选中图层的变化，初始化分类数量
watch(selectedLayerName, (newVal) => {
    if (currentTool.value?.id === 'kmeans') {
        // 为新选中的图层设置默认值
        newVal.forEach(layerId => {
            if (!clusterCounts.value[layerId]) {
                clusterCounts.value[layerId] = 5  // 默认5类
            }
        })
        // 清理未选中的图层
        Object.keys(clusterCounts.value).forEach(layerId => {
            if (!newVal.includes(layerId)) {
                delete clusterCounts.value[layerId]
            }
        })
    }
})

// 监听选中图层的变化，初始化波段信息
watch(selectedLayerName, async (newVal) => {
    if (currentTool.value?.id === 'raster-calculator' || currentTool.value?.id === 'image-bands-rename') {
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
    SearchDataService.handleDatasetSelect(dataset, selectedDataset, showSearchResults)
}

// 添加处理ID搜索的方法
const handleCustomIdSearch = () => {
    SearchDataService.handleIdSearch(customDatasetId.value, searchResults, showSearchResults)
}
</script>

<style src="../styles/tools.css"></style>