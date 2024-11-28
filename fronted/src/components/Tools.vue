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
            <el-checkbox-group v-model="selectedLayerName">
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { menuItems } from '../config/tools-config'  // 将菜单配置移到单独的文件
import L from 'leaflet'  // 添加这行

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
        if (tool.id === 'cloud-removal') {
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

            availableLayers.value = data.layers
            currentTool.value = tool
            showLayerSelect.value = true
        }
    } catch (error) {
        console.error('Error handling tool click:', error)
        ElMessage.error('工具执行失败')
    }
}

// 图层处理方法
const handleLayerSelect = async () => {
    if (selectedLayerName.value.length === 0) {
        ElMessage.warning('请选择至少一个图层')
        return
    }

    try {
        // 设置处理状态
        isProcessing.value = true

        // 发送请求到后端
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
            const layer = props.mapView.layers.find(l => l.id === selectedLayerName.value[0])
            if (layer) {
                console.log('Layer found:', layer)
                // 移除旧图层
                if (layer.leafletLayer) {
                    // 确保 _layers 存在
                    if (props.mapView.map._layers) {
                        let mapLayers = Object.values(props.mapView.map._layers);
                        console.log('mapLayers:', mapLayers);

                        mapLayers.forEach((mapLayer) => {
                            if (mapLayer instanceof L.TileLayer &&
                                mapLayer._url === layer.leafletLayer._url) {
                                mapLayer.options.zoomAnimation = false;
                                props.mapView.map.removeLayer(mapLayer);
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
                    newLeafletLayer.addTo(props.mapView.map)
                    newLeafletLayer.setZIndex(layer.zIndex)
                }
            }
            ElMessage.success(data.message)
            showLayerSelect.value = false
            selectedLayerName.value = []
        } else {
            ElMessage.error(data.error || '处理失败')
        }
    } catch (error) {
        console.error('Error processing layers:', error)
        ElMessage.error('处理失败')
    } finally {
        // 重置处理状态
        isProcessing.value = false
    }
}

// 暴露方法给父组件
defineExpose({
    closeAllMenus: () => {
        showSubmenu.value = ''
        activeMenu.value = ''
        activeSubMenu.value = ''
    }
})
</script>

<style src="../styles/tools.css"></style>
