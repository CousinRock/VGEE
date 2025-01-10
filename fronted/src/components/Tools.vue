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
        :width="['kmeans', 'raster-calculator'].includes(currentTool?.id) ? '800px' : '400px'" width="800px">
        <div class="layer-select-content"
            :class="{ 'with-settings': ['kmeans', 'raster-calculator'].includes(currentTool?.id) }">
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
            <div v-if="(currentTool?.id === 'kmeans' || currentTool?.id === 'random-forest' || currentTool?.id === 'raster-calculator') && selectedLayerName.length > 0"
                class="layer-select-right">
                <!-- K-means 设置 -->
                <div v-if="currentTool?.id === 'kmeans'" class="kmeans-options">
                    <h4>分类设置</h4>
                    <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-option-item">
                        <div class="layer-name">
                            {{ availableLayers.find(l => l.id === layerId)?.name }}
                        </div>
                        <div class="option-item">
                            <label>分类数量：</label>
                            <el-slider v-model="clusterCounts[layerId]" :min="2" :max="20" :step="1" show-input :marks="{
                                2: '2',
                                5: '5',
                                10: '10',
                                20: '20',
                            }" />
                        </div>
                    </div>
                </div>

                <!-- 随机森林设置 -->
                <div v-if="currentTool?.id === 'random-forest'" class="rf-options">
                    <h4>随机森林设置</h4>
                    <div class="option-item">
                        <label>决策树数量：</label>
                        <el-slider v-model="rfParams.numberOfTrees" :min="10" :max="100" :step="10" show-input :marks="{
                            10: '10',
                            50: '50',
                            100: '100'
                        }" />
                    </div>
                    <div class="option-item">
                        <label>训练集比例：</label>
                        <el-slider v-model="rfParams.trainRatio" :min="0.5" :max="0.9" :step="0.1" show-input :marks="{
                            0.5: '50%',
                            0.7: '70%',
                            0.9: '90%'
                        }" />
                    </div>
                </div>

                <!-- 栅格计算器设置 -->
                <div v-if="currentTool?.id === 'raster-calculator'" class="calculator-options">
                    <h4>栅格计算器</h4>

                    <!-- 添加计算模式选择 -->
                    <div class="calc-mode">
                        <h5>计算模式:</h5>
                        <el-radio-group v-model="calculatorMode">
                            <el-radio label="single">单波段计算</el-radio>
                            <el-radio label="multi">多图层计算</el-radio>
                            <el-radio label="all_bands">多波段计算</el-radio>
                        </el-radio-group>
                        <div class="mode-hint">
                            <template v-if="calculatorMode === 'single'">
                                将同一公式应用到每个选中的波段 (如: B4-B3)
                            </template>
                            <template v-if="calculatorMode === 'multi'">
                                多个图层之间的计算，生成一个结果 (如: layer1.B4-layer2.B3)
                            </template>
                            <template v-if="calculatorMode === 'all_bands'">
                                将同一公式应用到所选图层的所有波段 (使用 x 表示波段值，如:
                                {'x*2': ['B1','B2','B3'], 'x/2': ['B5','B6','B7']})
                            </template>
                        </div>
                    </div>

                    <!-- 波段列表 -->
                    <div class="bands-list">
                        <h5>可用波段:</h5>
                        <div class="bands-container">
                            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-bands">
                                <div class="layer-name">
                                    {{ availableLayers.find(l => l.id === layerId)?.name }}
                                </div>
                                <div class="band-buttons">
                                    <el-button v-for="band in layerBands[layerId]" :key="band" size="small"
                                        @click="handleBandClick(layerId, band)">
                                        {{ band }}
                                    </el-button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 运算符 -->
                    <div class="operators">
                        <h5>运算符:</h5>
                        <div class="operator-buttons">
                            <!-- 算术运算符 -->
                            <div class="operator-group">
                                <h6>算术运算符:</h6>
                                <el-button size="small" @click="insertOperator('+')">+</el-button>
                                <el-button size="small" @click="insertOperator('-')">-</el-button>
                                <el-button size="small" @click="insertOperator('*')">×</el-button>
                                <el-button size="small" @click="insertOperator('/')">/</el-button>
                                <el-button size="small" @click="insertOperator('(')">(</el-button>
                                <el-button size="small" @click="insertOperator(')')">)</el-button>
                            </div>
                            <!-- 比较运算符 -->
                            <div class="operator-group">
                                <h6>比较运算符:</h6>
                                <el-button size="small" @click="insertOperator('==')">=</el-button>
                                <el-button size="small" @click="insertOperator('!=')">&ne;</el-button>
                                <el-button size="small" @click="insertOperator('>')">&gt;</el-button>
                                <el-button size="small" @click="insertOperator('<')">&lt;</el-button>
                                <el-button size="small" @click="insertOperator('>=')">&ge;</el-button>
                                <el-button size="small" @click="insertOperator('<=')">&le;</el-button>
                            </div>
                            <!-- 逻辑运算符 -->
                            <div class="operator-group">
                                <h6>逻辑运算符:</h6>
                                <el-button size="small" @click="insertOperator('&&')">AND</el-button>
                                <el-button size="small" @click="insertOperator('||')">OR</el-button>
                            </div>
                        </div>
                    </div>

                    <!-- 常用函数 -->
                    <div class="functions">
                        <h5>常用函数:</h5>
                        <div class="function-buttons">
                            <el-button size="small" @click="insertFunction('sqrt')">sqrt</el-button>
                            <el-button size="small" @click="insertFunction('pow')">pow</el-button>
                            <el-button size="small" @click="insertFunction('exp')">exp</el-button>
                            <el-button size="small" @click="insertFunction('log')">log</el-button>
                            <el-button size="small" @click="insertFunction('abs')">abs</el-button>
                        </div>
                    </div>

                    <!-- 计算表达式输入框 -->
                    <div class="expression-input">
                        <h5>计算表达式:</h5>
                        <el-input v-model="calculatorExpression" type="textarea" :rows="4"
                            placeholder="点击波段和运算符按钮生成表达式，可手动输入数字" />
                        <div class="expression-actions">
                            <el-button size="small" @click="clearExpression">清除</el-button>
                            <el-button size="small" @click="backspace">回退</el-button>
                        </div>
                    </div>
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

    <!-- 资产选择对话框 -->
    <el-dialog v-model="showAssetsDialog" :title="selectedAsset ? `选择资产: ${selectedAsset.name}` : '选择资产'"
        :width="currentTool?.id === 'kmeans' ? '800px' : '400px'" width="800px">
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

        <!-- 添加资产 -->
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showAssetsDialog = false">取消</el-button>
                <el-button type="primary" :loading="isLoadingAssets" @click="confirmAssetSelect">
                    {{ isLoadingAssets ? '添加中...' : '确定' }}
                </el-button>
            </span>
        </template>
    </el-dialog>
    <!-- 搜索数据 -->
    <SearchResults v-if="showSearchResults" :datasets="searchResults" @select="onDatasetSelect" @close="showSearchResults = false" />
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { menuItems } from '../config/tools-config'
import { getAvailableLayers, processLayerSelect } from '../service/headTools/tool'
import { calculatorTools } from '../service/headTools/tool'
import SearchResults from './SearchResults.vue'
import { handleDatasetSelect, handleIdSearch , searchData} from '../service/headTools/searchData'
import { onLoadAssets, onHandleAssetSelect, onConfirmAssetSelect } from '../service/headTools/upload'

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
const showAssetsDialog = ref(false)
const assetsList = ref([])
const selectedAsset = ref(null)
const isLoadingAssets = ref(false)
const rfParams = ref({
    numberOfTrees: 50,
    trainRatio: 0.7
});
const calculatorExpression = ref('')
const layerBands = ref({})  // 存储每个图层的波段信息
const calculatorMode = ref('single')
const showSearchResults = ref(false)
const searchResults = ref([])
const selectedDataset = ref(null)
const customDatasetId = ref('')
const activeSearchId = ref(false)

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
                await commonMethod(tool)
                break
            case 'image-filling':
                await commonMethod(tool)
                break
            case 'kmeans':
                await commonMethod(tool)
                break
            // 添加所有指数计算的处理
            case 'ndvi':
            case 'ndwi':
            case 'ndbi':
            case 'evi':
            case 'savi':
            case 'mndwi':
            case 'bsi':
                await commonMethod(tool)
                break
            case 'histogram-equalization':
                await commonMethod(tool)
                break
            case 'upload-vector-assets':
                showAssetsDialog.value = true
                await loadAssets()
                break
            case 'random-forest':
                await commonMethod(tool)
                break
            case 'raster-calculator':
                await commonMethod(tool)
                 // 初始化计算表达式
                calculatorExpression.value = ''
                break
            // 添加搜索数据的处理逻辑
            case 'search-data-landsat':
            case 'search-data-sentinel':
            case 'search-data-modis':
            case 'search-data-viirs':
            case 'search-data-dem':
                const datasetType = tool.label
                const datasets = await searchData(datasetType)
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
    const layers = await getAvailableLayers()
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

            // 添加计算模式参数
            result = await processLayerSelect(
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
            result = await processLayerSelect(
                selectedLayerName.value,
                currentTool.value,
                props.mapView,
                clusterCounts.value,
                isProcessing
            )
        } else if (currentTool.value.id === 'random-forest') {
            // 随机森林处理逻辑
            result = await processLayerSelect(
                selectedLayerName.value,
                currentTool.value,
                props.mapView,
                rfParams.value,
                isProcessing
            )
            console.log('Tools.vue - handleLayerSelect - result', result)
        } else {
            // 其他工具处理逻辑
            result = await processLayerSelect(
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

// 修改 loadAssets 方法
const loadAssets = async (folder = null) => {
    await onLoadAssets(folder,isLoadingAssets,assetsList)
}

// 修改资产选择处理方法
const handleAssetSelect = async (data) => {
    await onHandleAssetSelect(data,selectedAsset)
}

// 修改确认选择方法
const confirmAssetSelect = async () => {
    await onConfirmAssetSelect(selectedAsset,showAssetsDialog,isLoadingAssets,props)
}

// 修改波段信息获取监听器
watch(selectedLayerName, async (newVal) => {
    if (currentTool.value?.id === 'raster-calculator') {
        for (const layerId of newVal) {
            if (!layerBands.value[layerId]) {
                layerBands.value[layerId] = calculatorTools.getLayerBands(props.mapView, layerId)
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
})

// 栅格计算器操作方法

// 调用calculatorTools.insertOperator方法将运算符插入到当前表达式中
const insertOperator = (operator) => {
    calculatorExpression.value = calculatorTools.insertOperator(calculatorExpression.value, operator)
}

// 调用calculatorTools.clearExpression方法清空当前表达式
const clearExpression = () => {
    calculatorExpression.value = calculatorTools.clearExpression()
}

// 调用calculatorTools.backspace方法智能删除表达式的最后一部分
const backspace = () => {
    calculatorExpression.value = calculatorTools.backspace(calculatorExpression.value)
}

// 调用calculatorTools.insertFunction方法将数学函数插入到当前表达式中
const insertFunction = (func) => {
    calculatorExpression.value = calculatorTools.insertFunction(calculatorExpression.value, func)
}

// 修改波段点击处理方法
const handleBandClick = (layerId, band) => {
    const layerName = availableLayers.value.find(l => l.id === layerId)?.name || layerId
    if (calculatorMode.value === 'multi') {
        // 多图层模式：使用图层名.波段的格式
        calculatorExpression.value += `${layerName}.${band}`
    } else if (calculatorMode.value === 'all_bands') {
        calculatorExpression.value += "'"+band+"'"
    } else {
        // 单图层模式：直接使用波段名
        calculatorExpression.value += `${band}`
    }
}

////// 栅格计算器操作方法 //////

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
    handleDatasetSelect(dataset, selectedDataset, showSearchResults)
}

// 添加处理ID搜索的方法
const handleCustomIdSearch = () => {
    handleIdSearch(customDatasetId.value, searchResults, showSearchResults)
}
</script>

<style src="../styles/tools.css"></style>