<template>
    <header class="header">
        <nav class="nav-menu">
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
        </nav>
    </header>
    <!-- 添加图层选择对话框 -->
    <el-dialog v-model="showLayerSelect" title="选择需要处理的图层" width="400px">
        <div class="layer-select-content">
            <el-checkbox-group v-model="selectedLayerName">
                <div v-for="layer in availableLayers" :key="layer.id" class="layer-option">
                    <el-checkbox :label="layer.id">{{ layer.name }}</el-checkbox>
                </div>
            </el-checkbox-group>
        </div>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showLayerSelect = false">取消</el-button>
                <el-button type="primary" @click="handleLayerSelect">
                    确定
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

const layers = ref([])
let map = ref(null)

// 修改 props 定义
const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})

// 监听 mapView 的变化
watch(() => props.mapView, (newMapView) => {
    if (newMapView) {
        console.log('Header received mapView:', {
            instance: newMapView,
            layers: newMapView.layers,
            map: newMapView.map
        })
        layers.value = newMapView.layers
        console.log('newMapView:', newMapView.layers);
    }
}, { immediate: true })

// 定义菜单项
const menuItems = [
    {
        id: 'tools',
        label: '工具箱',
        children: [
            {
                id: 'preprocessing',
                label: '预处理工具',
                children: [
                    { id: 'cloud-removal', label: '影像除云', icon: 'fas fa-cloud-sun' },
                    { id: 'atmospheric-correction', label: '大气校正', icon: 'fas fa-wind' },
                    { id: 'radiometric-calibration', label: '辐射定标', icon: 'fas fa-adjust' },
                    { id: 'geometric-correction', label: '几何校正', icon: 'fas fa-ruler-combined' }
                ]
            },
            {
                id: 'index-calculation',
                label: '指数计算',
                children: [
                    { id: 'ndvi', label: 'NDVI', icon: 'fas fa-leaf' },
                    { id: 'ndwi', label: 'NDWI', icon: 'fas fa-water' },
                    { id: 'ndbi', label: 'NDBI', icon: 'fas fa-building' },
                    { id: 'custom-index', label: '自定义指数', icon: 'fas fa-calculator' }
                ]
            },
            {
                id: 'classification',
                label: '分类工具',
                children: [
                    { id: 'supervised', label: '监督分类', icon: 'fas fa-tags' },
                    { id: 'unsupervised', label: '非监督分类', icon: 'fas fa-random' },
                    { id: 'object-based', label: '对象分类', icon: 'fas fa-object-group' }
                ]
            },
            {
                id: 'change-detection',
                label: '变化检测',
                children: [
                    { id: 'difference', label: '差值检测', icon: 'fas fa-not-equal' },
                    { id: 'ratio', label: '比值检测', icon: 'fas fa-percentage' },
                    { id: 'pca', label: 'PCA检测', icon: 'fas fa-chart-line' }
                ]
            },
            {
                id: 'vector-tools',
                label: '矢量工具',
                children: [
                    { id: 'measure', label: '测量工具', icon: 'fas fa-ruler' },
                    { id: 'draw', label: '绘制工具', icon: 'fas fa-draw-polygon' },
                    { id: 'buffer', label: '缓冲区分析', icon: 'fas fa-expand-alt' },
                    { id: 'overlay', label: '叠加分析', icon: 'fas fa-layer-group' }
                ]
            },
            {
                id: 'export',
                label: '导出工具',
                children: [
                    { id: 'export-image', label: '导出影像', icon: 'fas fa-file-image' },
                    { id: 'export-vector', label: '导出矢量', icon: 'fas fa-file-export' },
                    { id: 'export-stats', label: '导出统计', icon: 'fas fa-chart-bar' }
                ]
            }
        ]
    },
    {
        id: 'help',
        label: '帮助',
        children: [
            { id: 'about', label: '关于', icon: 'fas fa-info-circle' },
            { id: 'docs', label: '文档', icon: 'fas fa-book' },
            { id: 'tutorial', label: '教程', icon: 'fas fa-graduation-cap' }
        ]
    }
]

const activeMenu = ref('')
const showSubmenu = ref('')
const activeSubMenu = ref('')

// 添加需要的状态
const isProcessing = ref(false); // 处理状态

// 添加新的状态变量
const showLayerSelect = ref(false)
const availableLayers = ref([])
const selectedLayerName = ref([])
const currentTool = ref(null)

// 在工具执行时显示加载状态
const executeWithLoading = async (callback) => {
    isProcessing.value = true;
    try {
        await callback();
    } finally {
        isProcessing.value = false;
    }
}

// 切换主菜单
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

// 处理子菜单点击
const handleSubMenuClick = (item) => {
    if (item.children) {
        // 如果点击的是同一个菜单项，则关闭子菜单
        if (activeSubMenu.value === item.id) {
            activeSubMenu.value = ''
        } else {
            activeSubMenu.value = item.id
        }
    } else {
        console.log('Menu item clicked:', item.id)
        // 处理没有子菜单的项目点击
        showSubmenu.value = ''
        activeSubMenu.value = ''
    }
}

// 处理工具点击
const handleToolClick = async (tool) => {
    try {
        if (tool.id === 'cloud-removal') {
            // 获取可用的 Landsat 图层
            const response = await fetch('http://localhost:5000/tools/get-layers')
            const data = await response.json()

            if (!data.success) {
                ElMessage.error('获取图层失败')
                return
            }

            if (!data.layers || data.layers.length === 0) {
                ElMessage.warning('没有可用的 Landsat 图层')
                return
            }

            // 显示图层选择对话框
            availableLayers.value = data.layers
            currentTool.value = tool
            showLayerSelect.value = true
        }
        // ... 其他工具的处理 ...
    } catch (error) {
        console.error('Error handling tool click:', error)
        ElMessage.error('工具执行失败')
    }
}

// 处理图层选择
const handleLayerSelect = async () => {
    if (selectedLayerName.value.length === 0) {
        ElMessage.warning('请选择至少一个图层')
        return
    }

    try {
        const mapViewInstance = layers
        if (!mapViewInstance) {
            console.error('Layers not available')
            ElMessage.error('图层未初始化')
            return
        }

        // 获取地图实例
        const mapRef = props.mapView  // 正确访问响应式的 map 实例
        if (!mapRef) {
            console.error('Map not available')
            ElMessage.error('地图未初始化')
            return
        }

        console.log('Map instance:', mapRef)
        console.log('Current layers:', mapViewInstance.value)
        console.log('Selected layer ID:', selectedLayerName.value[0])

        const result = await fetch('http://localhost:5000/tools/cloud-removal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                layer_id: selectedLayerName.value[0]
            })
        })

        const data = await result.json()
        if (data.success && data.tileUrl) {
            // 找到要更新的图层
            const layer = mapViewInstance.value.find(l => l.id === selectedLayerName.value[0])
            if (layer) {
                console.log('Layer found:', layer)
                // 移除旧图层
                if (layer.leafletLayer) {
                    // 确保 _layers 存在
                    if (mapRef._layers) {
                        let mapLayers = Object.values(mapRef._layers);
                        console.log('mapLayers:', mapLayers);

                        mapLayers.forEach((mapLayer) => {
                            if (mapLayer instanceof L.TileLayer &&
                                mapLayer._url === layer.leafletLayer._url) {
                                mapLayer.options.zoomAnimation = false;
                                mapRef.removeLayer(mapLayer);
                            }
                        });
                    }
                }

                // 创建新图层
                const newLeafletLayer = L.tileLayer(data.tileUrl, {
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

                // 如果图层是可见的，则添加到地图
                if (layer.visible) {
                    newLeafletLayer.addTo(mapRef)
                    newLeafletLayer.setZIndex(layer.zIndex)
                }
            }
            ElMessage.success(data.message)
            showLayerSelect.value = false
            selectedLayerName.value = []
        }
    } catch (error) {
        console.error('Error processing layers:', error)
        ElMessage.error('处理失败')
    }
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
    const header = document.querySelector('.header')
    if (header && !header.contains(event.target)) {
        showSubmenu.value = ''
        activeMenu.value = ''
        activeSubMenu.value = ''
    }
}

// 添加和移除全局点击事件监听
onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>

<style src="../styles/header.css"></style>

<style>
/* 添加处理中的样式 */
.submenu-item.processing {
    opacity: 0.7;
    cursor: not-allowed;
}

.submenu-item.processing i.fa-spin {
    margin-left: auto;
    color: #4a90e2;
}

.layer-select-content {
    max-height: 300px;
    overflow-y: auto;
}

.layer-option {
    padding: 8px 0;
}
</style>
