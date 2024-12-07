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

    <!-- 添加图层选择对话框 -->
    <el-dialog v-model="showLayerSelect" title="选择需要处理的图层" width="400px">
        <div class="layer-select-content">
            <!-- 添加全选复选框 -->
            <div class="select-all-option">
                <el-checkbox 
                    v-model="selectAll"
                    @change="handleSelectAllChange"
                    :indeterminate="isIndeterminate">
                    全选
                </el-checkbox>
            </div>
            <el-checkbox-group 
                v-model="selectedLayerName"
                @change="handleCheckedLayersChange">
                <div v-for="layer in availableLayers" :key="layer.id" class="layer-option">
                    <el-checkbox :label="layer.id">{{ layer.name }}</el-checkbox>
                </div>
            </el-checkbox-group>
        </div>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showLayerSelect = false">取消</el-button>
                <el-button type="primary" 
                    :loading="isProcessing" 
                    @click="handleLayerSelect">
                    {{ isProcessing ? '处理中...' : '确定' }}
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { menuItems } from '../config/tools-config'
import L from 'leaflet'

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

// 获取可用图层的通用方法
const getAvailableLayers = async () => {
    try {
        const response = await fetch('http://localhost:5000/tools/get-layers')
        const data = await response.json()

        if (!data.success) {
            ElMessage.error('获取图层失败')
            return null
        }

        if (!data.layers || data.layers.length === 0) {
            ElMessage.warning('没有可用的 Landsat 图层')
            return null
        }

        return data.layers
    } catch (error) {
        console.error('Tools.vue - Error getting layers:', error)
        ElMessage.error('获取图层失败')
        return null
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

// 创建通用的请求数据构建函数
const createRequestData = (selectedIds) => {
    return {
        layer_ids: selectedIds,
        vis_params: props.mapView.layers
            .filter(l => selectedIds.includes(l.id))
            .map(l => ({
                id: l.id,
                visParams: l.visParams
            }))
    }
}

// 图层选择处理
const handleLayerSelect = async () => {
    if (selectedLayerName.value.length === 0) {
        ElMessage.warning('请选择至少一个图层')
        return
    }
    
    try {
        isProcessing.value = true

        // 根据当前工具类型选择不同的处理端点和参数
        let endpoint = ''
        let requestData = {}
        
        switch (currentTool.value.id) {
            case 'cloud-removal':
                endpoint = 'cloud-removal'               
                break
            case 'image-filling':
                endpoint = 'image-filling'
                break
            // 添加指数计算的处理
            case 'ndvi':
            case 'ndwi':
            case 'ndbi':
            case 'evi':
            case 'savi':
            case 'mndwi':
            case 'bsi':
                endpoint = 'calculate-index'
                break
            default:
                throw new Error('未知的工具类型')
        }

        // 构建请求数据
        if (endpoint === 'calculate-index') {
            requestData = {
                ...createRequestData(selectedLayerName.value),
                index_type: currentTool.value.id  // 添加指数类型
            }
        } else {
            requestData = createRequestData(selectedLayerName.value)
        }

        const result = await fetch(`http://localhost:5000/tools/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })

        const data = await result.json()
        if (data.success) {
            // 处理返回的多个图层结果
            if (Array.isArray(data.results)) {
                for (const layerResult of data.results) {
                    // 计算指数后重新获取波段信息
                    if (endpoint === 'calculate-index') {
                        const layer = props.mapView.layers.find(l => l.id === layerResult.layer_id)
                        if (layer) {
                            const response = await fetch(`http://localhost:5000/layer-info?id=${layer.id}&satellite=${layer.satellite}`)
                            const layerInfo = await response.json()
                            if (layerInfo.success) {
                                layer.bandInfo = layerInfo.bands
                            }
                        }
                    }
                    await updateMapLayer(layerResult.tileUrl, layerResult.layer_id)
                }
            } else {
                // 处理单个图层结果
                await updateMapLayer(data.tileUrl, selectedLayerName.value[0])
            }
            
            ElMessage.success(data.message)
            showLayerSelect.value = false
            selectedLayerName.value = []
        } else {
            ElMessage.error(data.message || '处理失败')
        }
    } catch (error) {
        console.error('Tools.vue - Error processing layers:', error)
        ElMessage.error('处理失败')
    } finally {
        isProcessing.value = false
    }
}

// 更新地图图层
async function updateMapLayer(tileUrl, layerId) {
    const layer = props.mapView.layers.find(l => l.id === layerId)
    if (!layer) return

    // 移除旧图层
    if (layer.leafletLayer && props.mapView.map._layers) {
        let mapLayers = Object.values(props.mapView.map._layers)
        mapLayers.forEach((mapLayer) => {
            if (mapLayer instanceof L.TileLayer &&
                mapLayer._url === layer.leafletLayer._url) {
                mapLayer.options.zoomAnimation = false
                props.mapView.map.removeLayer(mapLayer)
            }
        })
    }

    // 创建新图层
    const newLeafletLayer = L.tileLayer(tileUrl, {
        opacity: layer.opacity,
        maxZoom: 20,
        maxNativeZoom: 20,
        tileSize: 256,
        updateWhenIdle: false,
        updateWhenZooming: false,
        keepBuffer: 2,
        zIndex: layer.zIndex
    })

    // 更新图层引用
    layer.leafletLayer = newLeafletLayer
    console.log('Tools.vue - layer.visParams', layer.visParams)

    // 如果图层是可见的，则添加到地图
    if (layer.visible) {
        newLeafletLayer.addTo(props.mapView.map)
        newLeafletLayer.setZIndex(layer.zIndex)
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

// 在显示对话框时重置选择状态
watch(showLayerSelect, (newVal) => {
    if (newVal) {
        selectAll.value = false
        isIndeterminate.value = false
        selectedLayerName.value = []
    }
})

// 暴露方法��父组件
defineExpose({
    closeAllMenus: () => {
        showSubmenu.value = ''
        activeMenu.value = ''
        activeSubMenu.value = ''
    }
})
</script>

<style src="../styles/tools.css"></style>