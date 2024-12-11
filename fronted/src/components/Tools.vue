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
        :width="currentTool?.id === 'kmeans' ? '800px' : '400px'" width="800px">
        <div class="layer-select-content" :class="{ 'with-settings': currentTool?.id === 'kmeans' }">
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
            <div v-if="currentTool?.id === 'kmeans' && selectedLayerName.length > 0" class="layer-select-right">
                <div class="kmeans-options">
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
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { menuItems } from '../config/tools-config'
import { getAvailableLayers, processLayerSelect } from './service/tool'

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
            default:
                ElMessage.warning('该功能尚未实现')
        }
    } catch (error) {
        console.error('Tools.vue - Error handling tool click:', error)
        ElMessage.error('工具执行失败')
    }
}

// 添加指数计算处理函数
async function handleIndexCalculation(tool) {
    const layers = await getAvailableLayers()
    if (!layers) return

    selectedLayerName.value = []  // 清空之前的选择
    availableLayers.value = layers
    currentTool.value = tool
    showLayerSelect.value = true
}

// 云去除功能处理函数
async function handleCloudRemoval(tool) {
    const layers = await getAvailableLayers()
    if (!layers) return

    selectedLayerName.value = []  // 清空之前的选择
    availableLayers.value = layers
    currentTool.value = tool
    showLayerSelect.value = true
}

// 图像填补功能处理函数
async function handleImageFilling(tool) {
    const layers = await getAvailableLayers()
    if (!layers) return

    // 允许多选图层
    selectedLayerName.value = []  // 清空之前的选择
    availableLayers.value = layers
    currentTool.value = tool
    showLayerSelect.value = true
}

// 添加K-means聚类处理函数
async function handleKMeansClustering(tool) {
    const layers = await getAvailableLayers()
    if (!layers) return

    selectedLayerName.value = []  // 清除之前的选择
    availableLayers.value = layers
    currentTool.value = tool
    showLayerSelect.value = true
}

// 添加直方图均衡化处理函数
async function handleHistogramEqualization(tool) {
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
    const result = await processLayerSelect(
        selectedLayerName.value,
        currentTool.value,
        props.mapView,
        clusterCounts.value,
        isProcessing
    )

    if (result) {
        showLayerSelect.value = false
        selectedLayerName.value = []
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