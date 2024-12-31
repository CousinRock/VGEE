<template>
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
        <div class="layer-select-content" :class="{ 'with-settings': ['kmeans', 'raster-calculator'].includes(currentTool?.id) }">
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
                    
                    <!-- 波段列表 -->
                    <div class="bands-list">
                        <h5>可用波段:</h5>
                        <div class="bands-container">
                            <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-bands">
                                <div class="layer-name">{{ availableLayers.find(l => l.id === layerId)?.name }}</div>
                                <div class="band-buttons">
                                    <el-button 
                                        v-for="band in layerBands[layerId]" 
                                        :key="band"
                                        size="small"
                                        @click="insertBand(layerId, band)"
                                    >
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
                        <el-input
                            v-model="calculatorExpression"
                            type="textarea"
                            :rows="4"
                            placeholder="点击波段和运算符按钮生成表达式，可手动输入数字"
                        />
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

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showAssetsDialog = false">取消</el-button>
                <el-button type="primary" :loading="isLoadingAssets" @click="confirmAssetSelect">
                    {{ isLoadingAssets ? '添加中...' : '确定' }}
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { menuItems } from '../config/tools-config'
import { getAvailableLayers, processLayerSelect, handleVectorAsset, handleImageAsset } from './service/tool'
import { API_ROUTES } from '../api/routes'
import { calculatorTools } from './service/tool'

const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})

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
const selectedAssetIds = ref([])  // 用于存储选中的资产ID
const rfParams = ref({
    numberOfTrees: 50,
    trainRatio: 0.7
});
const calculatorExpression = ref('')
const layerBands = ref({})  // 存储每个图层的波段信息

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
        switch (tool.id) {
            case 'cloud-removal':
                await handleCloudRemoval(tool)
                break
            case 'image-filling':
                await handleImageFilling(tool)
                break
            case 'kmeans':
                await handleKMeansClustering(tool)
                break
            // 添加所有指数计算的处理
            case 'ndvi':
            case 'ndwi':
            case 'ndbi':
            case 'evi':
            case 'savi':
            case 'mndwi':
            case 'bsi':
                await handleIndexCalculation(tool)
                break
            case 'histogram-equalization':
                await handleHistogramEqualization(tool)
                break
            case 'upload-vector-assets':
                showAssetsDialog.value = true
                await loadAssets()
                break
            case 'random-forest':
                await handleRandomForest(tool)
                break
            case 'raster-calculator':
                await handleRasterCalculator(tool)
                break
            default:
                ElMessage.warning('该功能尚未实现')
        }
    } catch (error) {
        console.error('Error handling tool click:', error)
        ElMessage.error('工具执行失败')
    }
}

const commonMethod = async (tool) => {
    const layers = await getAvailableLayers()
    if (!layers) return

    selectedLayerName.value = []  // 清空之前的选择
    availableLayers.value = layers
    currentTool.value = tool
    showLayerSelect.value = true
}

// 添加指数计算处理函数
async function handleIndexCalculation(tool) {
    commonMethod(tool)
}

// 云去除功能处理函数
async function handleCloudRemoval(tool) {
    commonMethod(tool)
}

// 图像填补功能处理函数
async function handleImageFilling(tool) {
    commonMethod(tool)
}

// 添加K-means聚类处理函数
async function handleKMeansClustering(tool) {
    commonMethod(tool)
}

// 添加直方图均衡化处理函数
async function handleHistogramEqualization(tool) {
    commonMethod(tool)
}

// 添加随机森林分类处理方法
const handleRandomForest = async (tool) => {
    commonMethod(tool)
}

// 添加栅格计算器处理方法
const handleRasterCalculator = async (tool) => {
    const layers = await getAvailableLayers()
    if (!layers) return

    selectedLayerName.value = []
    availableLayers.value = layers
    currentTool.value = tool
    
    // 初始化计算表达式
    calculatorExpression.value = ''
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
            // 栅格计算器处理逻辑
            if (!calculatorExpression.value) {
                ElMessage.warning('请输入计算表达式')
                return
            }
            result = await processLayerSelect(
                selectedLayerName.value,
                currentTool.value,
                props.mapView,
                calculatorExpression.value,
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
    try {
        isLoadingAssets.value = true
        const url = new URL(API_ROUTES.TOOLS.GET_ASSETS)
        if (folder) {
            url.searchParams.append('folder', folder)
        }

        const response = await fetch(url)
        const data = await response.json()

        if (!data.success) {
            ElMessage.error(data.message || '获取资产列表失败')
            return
        }

        assetsList.value = data.assets
        console.log('Tools.vue - loadAssets - assets:', data.assets)
    } catch (error) {
        console.error('Tools.vue - Error loading assets:', error)
        ElMessage.error('获取资产列表失败')
    } finally {
        isLoadingAssets.value = false
    }
}

// 修改资产选择处理方法
const handleAssetSelect = async (data) => {
    try {
        // 如果是文件夹，不进行选择
        if (data.type === 'FOLDER') {
            return
        }

        // 只更新选中状态，不关闭对话框
        selectedAsset.value = data
        console.log('Tools.vue - handleAssetSelect - selected asset:', data)
    } catch (error) {
        console.error('Tools.vue - Error selecting asset:', error)
        ElMessage.error('选择资产失败')
    }
}

// 修改确认选择方法
const confirmAssetSelect = async () => {
    try {
        if (!selectedAsset.value) {
            ElMessage.warning('请选择一个资产')
            return
        }

        // 设置加载状态
        isLoadingAssets.value = true

        console.log('Tools.vue - confirmAssetSelect - selectedAsset:', selectedAsset.value)
        // 根据资产类型处理
        if (selectedAsset.value.type === 'TABLE') {
            // 处理矢量数据
            const loadingMessage = ElMessage({
                message: '正在添加矢量图层...',
                type: 'info',
                duration: 0
            })
            const success = await handleVectorAsset(selectedAsset.value, props.mapView)
            loadingMessage.close()  // 只关闭加载消息
            if (success) {
                ElMessage.success(`已添加矢量图层: ${selectedAsset.value.name}`)
            }
        } else if (selectedAsset.value.type === 'IMAGE') {
            // 处理栅格影像
            const loadingMessage = ElMessage({
                message: '正在添加栅格图层...',
                type: 'info',
                duration: 0
            })
            const success = await handleImageAsset(selectedAsset.value, props.mapView)
            loadingMessage.close()  // 只关闭加载消息
            if (success) {
                ElMessage.success(`已添加栅格图层: ${selectedAsset.value.name}`)
            }
        }

        showAssetsDialog.value = false
    } catch (error) {
        console.error('Tools.vue - Error confirming asset selection:', error)
        ElMessage.error('添加图层失败')
    } finally {
        // 清除加载状态
        isLoadingAssets.value = false
    }
}

// 修改波段信息获取监听器
watch(selectedLayerName, async (newVal) => {
    if (currentTool.value?.id === 'raster-calculator') {
        for (const layerId of newVal) {
            if (!layerBands.value[layerId]) {
                layerBands.value[layerId] = calculatorTools.getLayerBands(props.mapView, layerId)
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

//  在表达式中插入波段引用
const insertBand = (layerId, band) => {
    calculatorExpression.value = calculatorTools.insertBand(calculatorExpression.value, band)
}

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

// 暴露方法父组件
defineExpose({
    closeAllMenus: () => {
        showSubmenu.value = ''
        activeMenu.value = ''
        activeSubMenu.value = ''
    }
})
</script>

<style src="../styles/tools.css"></style>