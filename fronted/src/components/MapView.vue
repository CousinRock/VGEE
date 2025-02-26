<template>
    <div class="map-container">
        <div id="map"></div>

        <!-- 地图工具栏 -->
        <div class="map-tools">
            <div class="tool-group">
                <div class="tool-button" @click="toggleLayerControl" :class="{ active: showLayerControl }" title="图层">
                    <i class="fas fa-layer-group"></i>
                </div>
                <div class="tool-button" @click="togglePixelTool" :class="{ active: isPixelToolActive }" title="获取像素值">
                    <i class="fas fa-wrench"></i>
                </div>
            </div>

            <!-- 像素值显示面板 -->
            <div class="pixel-value-panel" v-if="isPixelToolActive && pixelValues">
                <h3>Pixel Values</h3>
                <div class="pixel-values-container">
                    <div v-for="(values, layerName) in pixelValues" :key="layerName" class="layer-pixel-values">
                        <h4>{{ layerName }}</h4>
                        <div class="band-values">
                            <div v-for="(value, band) in values" :key="band" class="band-value">
                                <span class="band-name">{{ band }}:</span>
                                <span class="band-value-number">{{ value.toFixed(6) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 图层控制面板 -->
            <div class="layer-control" v-if="showLayerControl">
                <div class="layer-item">
                    <div class="layer-header">
                        <input type="checkbox" v-model="baseLayerVisible" id="baseLayer">
                        <label for="baseLayer">
                            <i class="fas fa-map"></i>
                            <span>Base Map</span>
                        </label>
                        <button class="layer-settings" @click="showBaseMapSettings = true">
                            <i class="fas fa-cog"></i>
                        </button>
                    </div>
                </div>

                <!-- 动态图列表 -->
                <div class="layer-item" v-for="layer in layers" :key="layer.id" draggable="true"
                    @dragstart="toolManager.handleDragStart($event, layer)" @dragend="toolManager.handleDragEnd"
                    @dragover="toolManager.handleDragOver" @dragleave="toolManager.handleDragLeave"
                    @drop="toolManager.handleDrop($event, layer, layers)">
                    <div class="layer-header">
                        <input type="checkbox" v-model="layer.visible" :id="layer.id">
                        <label :for="layer.id">
                            <i :class="layer.icon"></i>
                            <span>{{ layer.name }}</span>
                        </label>
                        <div class="layer-actions">
                            <!-- 添加锁定按钮，只对点图层显示 -->
                            <button v-if="layer.geometryType === 'Point'" class="layer-action-btn"
                                :class="{ 'active': layer.locked }" @click="layer.locked = !layer.locked"
                                :title="layer.locked ? 'Unlock Layer' : 'Lock Layer'">
                                <i :class="layer.locked ? 'fas fa-lock' : 'fas fa-lock-open'"></i>
                            </button>
                            <template v-if="layer.type === 'vector' || layer.type === 'manual'">
                                <el-dropdown trigger="click" :teleported="false">
                                    <button class="layer-settings" title="Layer Settings"
                                        :disabled="layer.isSettingStudyArea">
                                        <i :class="[
                                            'fas',
                                            layer.isSettingStudyArea || layer.isExporting ? 'fa-spinner fa-spin' : 'fa-cog'
                                        ]"></i>
                                        <!-- {{ layer.isSettingStudyArea ? '设置中...' : '' }} -->
                                    </button>
                                    <template #dropdown>
                                        <el-dropdown-menu>
                                            <el-dropdown-item
                                                v-if="layer.geometryType === 'Polygon' || layer.type === 'vector'"
                                                @click="toggleStudyArea(layer)" tabindex="0">
                                                <i
                                                    :class="layer.isStudyArea ? MENU_ICONS.STUDY_AREA_ACTIVE : MENU_ICONS.STUDY_AREA"></i>
                                                {{ layer.isStudyArea ? 'Cancel Study Area' : 'Set as Study Area' }}
                                            </el-dropdown-item>
                                            <el-dropdown-item
                                                v-if="layer.geometryType === 'Polygon' || layer.type === 'vector' || layer.geometryType === 'Point'"
                                                @click="toggleSample(layer)" tabindex="0">
                                                <i
                                                    :class="layer.isSample ? MENU_ICONS.SAMPLE_ACTIVE : MENU_ICONS.SAMPLE"></i>
                                                {{ layer.isSample ? 'Cancel Sample' : 'Set as Sample' }}
                                            </el-dropdown-item>
                                            <el-dropdown-item @click="openVectorStyleSettings(layer)" tabindex="0">
                                                <i :class="MENU_ICONS.STYLE"></i>
                                                Settings
                                            </el-dropdown-item>
                                            <el-dropdown-item @click="openRenameDialog(layer)" tabindex="0">
                                                <i :class="MENU_ICONS.EDIT"></i>
                                                Rename
                                            </el-dropdown-item>
                                            <el-dropdown-item @click="exportLayer(layer)" tabindex="0">
                                                <i :class="[
                                                    layer.isExporting ? 'fas fa-spinner fa-spin' : MENU_ICONS.EXPORT
                                                ]"></i>
                                                Export
                                            </el-dropdown-item>
                                        </el-dropdown-menu>
                                    </template>
                                </el-dropdown>
                            </template>
                            <template v-else>
                                <el-dropdown trigger="click" :teleported="false">
                                    <button class="layer-settings" title="Layer settings"
                                        :disabled="layer.isLoadingProperties || layer.isExporting">
                                        <i :class="[
                                            'fas',
                                            layer.isLoadingProperties || layer.isExporting ? 'fa-spinner fa-spin' : 'fa-cog'
                                        ]"></i>
                                    </button>
                                    <template #dropdown>
                                        <el-dropdown-menu>
                                            <el-dropdown-item @click="openRenameDialog(layer)" tabindex="0">
                                                <i :class="MENU_ICONS.EDIT"></i>
                                                Rename
                                            </el-dropdown-item>
                                            <el-dropdown-item @click="openLayerSettings(layer)" tabindex="0">
                                                <i :class="MENU_ICONS.SETTINGS"></i>
                                                Settings
                                            </el-dropdown-item>
                                            <el-dropdown-item @click="showLayerProperties(layer)" tabindex="0">
                                                <i :class="MENU_ICONS.INFO"></i>
                                                Properties
                                            </el-dropdown-item>
                                            <el-dropdown-item @click="exportLayer(layer)" tabindex="0">
                                                <i :class="[
                                                    layer.isExporting ? 'fas fa-spinner fa-spin' : MENU_ICONS.EXPORT
                                                ]"></i>
                                                Export
                                            </el-dropdown-item>
                                        </el-dropdown-menu>
                                    </template>
                                </el-dropdown>
                            </template>
                            <button class="remove-layer" @click="removeLayer(layer.id)" title="Remove Layer">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <input type="range" v-model="layer.opacity" min="0" max="1" step="0.1" class="opacity-slider"
                        v-if="layer.visible">
                </div>
            </div>
        </div>

        <!-- 底图设置对话框 -->
        <el-dialog v-model="showBaseMapSettings" title="Base Map Settings" width="300px">
            <div class="basemap-settings">
                <div class="setting-item">
                    <label>Base Map Type</label>
                    <el-select v-model="selectedBaseMap" @change="changeBaseMap">
                        <el-option v-for="map in baseMaps" :key="map.id" :label="map.name" :value="map.id" />
                    </el-select>
                </div>
            </div>
        </el-dialog>

        <!-- 修改图层设置对话框 -->
        <el-dialog v-model="showLayerSettings" title="Layer Settings" width="500px">
            <div class="layer-settings-content" v-if="currentLayer">
                <!-- 波段显示模式选择 -->
                <div class="band-mode-selector">
                    <el-radio-group v-model="bandMode">
                        <el-radio :value="1">1 band (Grayscale)</el-radio>
                        <el-radio :value="3">3 bands (RGB)</el-radio>
                    </el-radio-group>
                </div>

                <!-- 波段选择区域 -->
                <div class="band-selection" v-if="bandMode === 1">
                    <div class="band-select">
                        <label>Band</label>
                        <el-select v-model="visParams.bands[0]">
                            <el-option v-for="band in currentLayer.bandInfo" :key="band" :label="band" :value="band" />
                        </el-select>
                    </div>

                    <!-- 只在单波段模式下显示调色板选择器 -->
                    <div class="palette-select" style="margin-top: 10px;">
                        <label>Color Palette</label>
                        <el-select v-model="selectedPalette" style="width: 100%;"
                            popper-class="palette-select-dropdown">
                            <el-option v-for="(colors, name) in palettes" :key="name" :label="name" :value="name">
                                <div class="palette-preview-item">
                                    <div class="palette-preview" :style="toolManager.getPalettePreviewStyle(colors)">
                                    </div>
                                    <span>{{ name }}</span>
                                </div>
                            </el-option>
                        </el-select>
                    </div>
                </div>

                <!-- 多波段选择区域 -->
                <div class="band-selection" v-else>
                    <!-- 原有的RGB波段选择不变 -->
                    <div class="band-select">
                        <label>vis-red</label>
                        <el-select v-model="visParams.bands[0]">
                            <el-option v-for="band in availableBands" :key="band" :label="band" :value="band" />
                        </el-select>
                    </div>
                    <div class="band-select">
                        <label>vis-green</label>
                        <el-select v-model="visParams.bands[1]">
                            <el-option v-for="band in availableBands" :key="band" :label="band" :value="band" />
                        </el-select>
                    </div>
                    <div class="band-select">
                        <label>vis-blue</label>
                        <el-select v-model="visParams.bands[2]">
                            <el-option v-for="band in availableBands" :key="band" :label="band" :value="band" />
                        </el-select>
                    </div>
                </div>

                <!-- 拉伸方式选择 -->
                <div class="stretch-selection">
                    <label>Stretch:</label>
                    <el-select v-model="stretchType" style="width: 100%">
                        <el-option label="None" value="none" />
                        <el-option label="Custom" value="custom" />
                        <el-option label="Standard Deviation" value="std" />
                        <el-option label="Histogram Equalization" value="hist" />
                    </el-select>
                </div>

                <!-- 数值范围设置 -->
                <div class="range-setting">
                    <label>Range:</label>
                    <el-slider v-model="visParams.range" range :min="currentLayer.min" :max="currentLayer.max"
                        :step="toolManager.getSliderStep(currentLayer.satellite)"
                        :format-tooltip="val => toolManager.formatSliderValue(val)" @change="handleRangeChange" />
                    <div class="range-values">
                        {{ toolManager.formatSliderValue(visParams.range[0]) }} – {{
                            toolManager.formatSliderValue(visParams.range[1]) }}
                    </div>
                </div>

                <!-- 不透明度设置 -->
                <div class="opacity-setting">
                    <label>Opacity:</label>
                    <el-slider v-model="currentLayer.opacity" :min="0" :max="1" :step="0.01"
                        :format-tooltip="val => (val * 100).toFixed(0) + '%'" />
                    <div class="opacity-value">{{ (currentLayer.opacity * 100).toFixed(0) }}%</div>
                </div>

                <!-- Gamma值设置 -->
                <div class="gamma-setting">
                    <label>Gamma:</label>
                    <el-slider v-model="visParams.gamma" :min="0.1" :max="2.0" :step="0.1"
                        :format-tooltip="val => val.toFixed(1)" />
                    <div class="gamma-value">{{ visParams.gamma.toFixed(1) }}</div>
                </div>

                <!-- 按钮区域 -->
                <div class="button-group">
                    <el-button @click="importSettings">Import</el-button>
                    <el-button type="primary" @click="applyVisParams">Apply</el-button>
                </div>
            </div>
        </el-dialog>

        <!-- 添加矢量样式设置对话框 -->
        <el-dialog v-model="showVectorStyleDialog" title="Vector Layer Style Settings" width="400px">
            <div class="vector-style-settings">
                <div class="style-item">
                    <span>Border Color</span>
                    <el-color-picker v-model="vectorStyle.color" show-alpha popper-class="color-picker-popper" />
                </div>
                <div class="style-item">
                    <span>Border Width</span>
                    <el-slider v-model="vectorStyle.weight" :min="0" :max="10" :step="0.01" />
                </div>
                <div class="style-item">
                    <span>Border Opacity</span>
                    <el-slider v-model="vectorStyle.opacity" :min="0" :max="1" :step="0.01" />
                </div>
                <div class="style-item">
                    <span>Fill Opacity</span>
                    <el-slider v-model="vectorStyle.fillOpacity" :min="0" :max="1" :step="0.01" />
                </div>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showVectorStyleDialog = false">Cancel</el-button>
                    <el-button type="primary" @click="applyVectorStyle" :loading="isApplyingStyle">
                        {{ isApplyingStyle ? 'Applying...' : 'Apply' }}
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 添加样本类别输入对话框 -->
        <el-dialog v-model="showSampleDialog" title="Set Sample Class" width="400px">
            <div class="sample-settings">
                <el-form :model="sampleForm">
                    <el-form-item label="Sample Class">
                        <el-input v-model="sampleForm.className"
                            placeholder="Please enter the sample class (e.g., water, building, vegetation, etc.)"></el-input>
                    </el-form-item>
                </el-form>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showSampleDialog = false">Cancel</el-button>
                    <el-button type="primary" @click="confirmSetSample">Confirm</el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 添加属性查看对话框 -->
        <el-dialog v-model="showPropertiesDialog" :title="`${currentLayer?.name || ''} Properties`" width="600px">
            <div class="properties-container" v-if="layerProperties">
                <el-table :data="layerProperties" style="width: 100%">
                    <el-table-column prop="name" label="Property Name" width="200" />
                    <el-table-column prop="value" label="Property Value" />
                </el-table>
            </div>
        </el-dialog>

        <!-- 添加重命名对话框 -->
        <el-dialog v-model="showRenameDialog" title="Rename Layer" width="300px">
            <el-input v-model="newLayerName" placeholder="Please enter the new layer name" />
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showRenameDialog = false">Cancel</el-button>
                    <el-button type="primary" @click="renameLayer">Confirm</el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 添加导出设置对话框 -->
        <el-dialog v-model="showExportDialog" title="Export Layer" width="400px">
            <div class="export-form">
                <el-form label-width="100px">
                    <!-- 添加导出类型选择 -->
                    <el-form-item label="Export Type">
                        <el-radio-group v-model="exportType">
                            <el-radio label="drive">Export to Cloud Drive</el-radio>
                            <el-radio label="asset">Export to Asset</el-radio>
                        </el-radio-group>
                    </el-form-item>

                    <!-- 云盘导出选项 -->
                    <template v-if="exportType === 'drive'">
                        <el-form-item label="Export Folder">
                            <el-input v-model="exportFolder" placeholder="Please enter the export folder name" />
                        </el-form-item>
                    </template>

                    <!-- 资产导出选项 -->
                    <template v-if="exportType === 'asset'">
                        <el-form-item label="Asset ID">
                            <el-input v-model="assetId" placeholder="Please enter the asset ID" />
                        </el-form-item>
                        <el-form-item label="Description">
                            <el-input v-model="assetDescription" placeholder="Please enter the description" />
                        </el-form-item>
                    </template>

                    <!-- 添加分辨率选择 -->
                    <el-form-item label="Export Resolution">
                        <el-select v-model="exportScale" placeholder="Select Resolution">
                            <el-option label="10m" :value="10" />
                            <el-option label="20m" :value="20" />
                            <el-option label="30m" :value="30" />
                            <el-option label="60m" :value="60" />
                            <el-option label="100m" :value="100" />
                        </el-select>
                        <div class="scale-hint">Note: The minimum resolution supported by different satellite data
                            sources may
                            be different</div>
                    </el-form-item>
                </el-form>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showExportDialog = false">Cancel</el-button>
                    <el-button type="primary" @click="confirmExport" :loading="currentExportLayer?.isExporting">
                        {{ currentExportLayer?.isExporting ? 'Exporting...' : 'Confirm Export' }}
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick, reactive, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
// 引入底图配置
import { baseMaps, palettes } from '../config/map-config'
import { normalizeRange, layerChangeRemove } from '../util/methods'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import '@fortawesome/fontawesome-free/css/all.css'
import 'leaflet-draw'
import 'leaflet-draw/dist/leaflet.draw.css'
import { API_ROUTES } from '../api/routes'
import { layerManager, baseMapManager, toolManager, handleSample, handleStudyArea, handleStyle } from '../service/mapview'
import { MENU_ICONS } from '../service/mapview'
import { exportManager } from '../service/mapview'

const props = defineProps({
    mapData: {
        type: Object,
        default: () => ({})
    }
})

// 状态变量
const layers = ref([])
const showLayerControl = ref(false)//图层显示控制
const isPixelToolActive = ref(false)//像素工具
const pixelValues = ref(null)//像素值
const baseLayerVisible = ref(true)//底图显示控制
const showBaseMapSettings = ref(false)//底图设置
const showLayerSettings = ref(false)//图层设置
const selectedBaseMap = ref('satellite')//底图选择
const currentLayer = ref(null)//当前图层
const availableBands = ref([])//可用波段
const bandMode = ref(3)//波段模式
const stretchType = ref('custom')//拉伸方式
// reactive() 用于创建一个响应式对象，当对象的属性发生变化时会自动触发视图更新
const visParams = reactive({
    bands: ['B4', 'B3', 'B2'],  // 显示的波段组合
    range: [0, 100],            // 数值范围
    min: 0,                     // 最小值
    max: 0.3,                   // 最大值
    gamma: 1.4                  // 伽马值(用于调整亮度)
})

const map = ref(null)
let baseLayer = null

// 添加调色板状态
const selectedPalette = ref('default')//调色板

// 添加绘制控制相关的状态
const drawnItems = ref(null)//绘制项
const drawControl = ref(null)//绘制控件

// 添加新的状态变量
const showVectorStyleDialog = ref(false)//矢量样式对话框
const currentVectorLayer = ref(null)//当前矢量图层
const vectorStyle = ref({
    color: '#3388ff',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.2
})//矢量样式

//样本数据
const showSampleDialog = ref(false);//样本对话框
const sampleForm = ref({
    className: ''
});//样本表单
const currentSampleLayer = ref(null);//当前样本图层

// 在 script setup 顶部添加计数器
const pointLayerCounter = ref(-1);

// 属性查看相关的响应式变量
const showPropertiesDialog = ref(false)
const layerProperties = ref([])

// 添加重命名相关的响应式变量
const showRenameDialog = ref(false)//重命名对话框
const newLayerName = ref('')
const currentRenameLayer = ref(null)

// 添加加载状态变量
const isApplyingStyle = ref(false);//应用样式

// 添加导出相关的响应式变量
const showExportDialog = ref(false)//导出对话框
const exportFolder = ref('EarthEngine_Exports')  // 默认文件夹名
const exportScale = ref(30)  // 默认30米分辨率
const currentExportLayer = ref(null)//当前导出图层

// 添加新的响应式变量
const exportType = ref('drive')
const assetId = ref('')
const assetDescription = ref('')

// 修改 togglePixelTool 方法
const togglePixelTool = () => {
    toolManager.togglePixelTool(isPixelToolActive, map, pixelValues)
};

// 切换图层控制面板显示
const toggleLayerControl = () => {
    showLayerControl.value = !showLayerControl.value
}

// 添加新图层
const addNewLayer = async (layerName, mapData) => {
    await layerManager.addNewLayer(layerName, mapData, layers, map, API_ROUTES)
}

// 移除图层
const removeLayer = async (layerId) => {
    await layerManager.removeLayer(layerId, layers, map, API_ROUTES)
}

// 重命名图层
const renameLayer = async () => {
    if (await layerManager.renameLayer(currentRenameLayer.value, newLayerName.value, API_ROUTES)) {
        showRenameDialog.value = false
    }
}

// 监听图层变化时使用防抖
watch(layers, toolManager.debounce((newLayers) => {
    if (!map) return;

    nextTick(() => {
        newLayers.forEach(layer => {
            if (layer.leafletLayer) {
                if (layer.type === 'vector' || layer.type === 'manual') {
                    if (layer.visible) {
                        if (!map.value.hasLayer(layer.leafletLayer)) {
                            layer.leafletLayer.addTo(map.value)
                        }
                        // 使用保存的样式
                        if (layer.vectorStyle) {
                            layer.leafletLayer.setStyle({
                                ...layer.vectorStyle,
                                opacity: layer.opacity,
                                fillOpacity: layer.opacity * layer.vectorStyle.fillOpacity
                            })
                        }
                    } else {
                        if (map.value.hasLayer(layer.leafletLayer)) {
                            map.value.removeLayer(layer.leafletLayer)
                        }
                    }
                } else {
                    // 对于栅格图层，使用 setOpacity
                    layer.leafletLayer.setOpacity(layer.opacity)

                    if (layer.visible) {
                        if (!map.value.hasLayer(layer.leafletLayer)) {
                            layer.leafletLayer.addTo(map.value)
                        }
                        layer.leafletLayer.setZIndex(1000 + newLayers.indexOf(layer))
                    } else {
                        // 如果图层应该隐藏遍历查找并移除                            
                        layerChangeRemove(map.value, layer.leafletLayer)
                    }
                }
            }
        })
    })
}, 100), { deep: true })



// 修改 changeBaseMap 函数
const changeBaseMap = () => {
    baseLayer = baseMapManager.changeBaseMap(map, baseLayer, baseMaps, selectedBaseMap, baseLayerVisible)
}

// 修改底图可见性监听
watch(baseLayerVisible, (newValue) => {
    nextTick(() => {
        if (baseLayer) {
            if (newValue) {
                // 确保不会重复添加
                if (!map.value.hasLayer(baseLayer)) {
                    baseLayer.addTo(map.value)
                    baseLayer.setZIndex(0)
                }
            } else {
                if (map.value.hasLayer(baseLayer)) {
                    baseLayer.remove()
                }
            }
        }
    })
})

// 监听底图类型变化
watch(selectedBaseMap, () => {
    if (map.value) {
        changeBaseMap()
    }
})

// 在 onMounted 中只需要调用这个函
onMounted(async () => {
    try {
        // 创建地图实例时直接赋给 ref
        map.value = L.map('map', {
            center: [20, 0],
            zoom: 3,
            zoomAnimation: true,
            fadeAnimation: true,
            preferCanvas: true,
            wheelDebounceTime: 150,
            wheelPxPerZoomLevel: 120,
            // 添加投影关配置
            crs: L.CRS.EPSG3857,  // 明确定投影系统
            continuousWorld: true, // 确保连续的世界地图
            worldCopyJump: true,   // 允许在经度方向
            maxBounds: L.latLngBounds(L.latLng(-85.06, -180), L.latLng(85.06, 180)), // 限制范围
            minZoom: 1,
            maxZoom: 20
        })

        // 初始化底图
        changeBaseMap()

        // 初始化绘制控件
        initDrawControl()

        // 添加滚动优化
        map.value.on('zoomstart', () => {
            // 禁用所有图层的画
            layers.value.forEach(layer => {
                if (layer.leafletLayer) {
                    layer.leafletLayer.options.zoomAnimation = false;
                }
            });
        });

        map.value.on('zoomend', () => {
            // 重新启用动画
            setTimeout(() => {
                layers.value.forEach(layer => {
                    if (layer.leafletLayer) {
                        layer.leafletLayer.options.zoomAnimation = true;
                    }
                });
            }, 250);
        });
        // 触发初化完成事件
        emit('map-initialized', map.value)

    } catch (error) {
        console.error('MapView.vue - Error loading map:', error)
    }
})

// 更新图层顺序
const updateLayerOrder = () => {
    layerManager.updateLayerOrder(layers, map)
};

// 监听图层可见性变化
watch(() => layers.value.map(l => l.visible), () => {
    nextTick(updateLayerOrder)
}, { deep: true })

// 暴露方法和属性给父组件
defineExpose({
    layers,
    map: map,  // 使用 readonly 包装，防止外部修改
    addNewLayer,
    removeLayer,
    updateLayerOrder
})

// 添加范围变化处理函数
const handleRangeChange = (value) => {
    // 确保范围不超出限制
    visParams.range = [
        Math.max(value[0], currentLayer.value.min),
        Math.min(value[1], currentLayer.value.max)
    ];
};

// 修改打开层设置方法
const openLayerSettings = async (layer) => {
    try {
        currentLayer.value = layer
        console.log('MapView.vue - openLayerSettings - currentLayer:', currentLayer.value);

        // 如果已经有波段信息，直接使用
        if (layer.bandInfo) {
            availableBands.value = layer.bandInfo

            // 设波段模式
            bandMode.value = layer.visParams.bands.length === 1 ? 1 : 3

            // 更新范围和参数
            Object.assign(visParams, {
                bands: [...layer.visParams.bands],
                min: layer.visParams.min,
                max: layer.visParams.max,
                // 确保范围在限制内
                range: [
                    Math.max(layer.visParams.min, layer.min),
                    Math.min(layer.visParams.max, layer.max)
                ],
                gamma: layer.visParams.gamma || 1.4
            })

            showLayerSettings.value = true
            return
        }
        else {
            console.log('MapView.vue - openLayerSettings - no bandInfo:', layer);
        }

    } catch (error) {
        console.error('MapView.vue - Error opening layer settings:', error)
        ElMessage.error('获取波段信息失败')
    }
}

// 修改更新围函数
const updateRangeBasedOnBands = async (vis) => {
    layerManager.updateRangeBasedOnBands(currentLayer, vis, visParams, API_ROUTES)
}

// 应用可视化参数
const applyVisParams = async () => {
    layerManager.applyVisParams(map, currentLayer, visParams, showLayerSettings, bandMode, palettes, selectedPalette, layers, API_ROUTES)
}

// 修改波段变化的监听
watch(() => visParams.bands, () => {
    if (!currentLayer.value || !currentLayer.value.bandInfo) return

    console.log('MapView-watch', visParams);

    updateRangeBasedOnBands(visParams)
}, { deep: true })

// 在 script setup 中添加 importSettings 函数
const importSettings = () => {
    // TODO: 实现导入设置功能
    console.log('MapView.vue - Import settings clicked')
}

// 修改组件卸载时的清理代码
onUnmounted(() => {
    // 确保所有图层都被正确清理
    layers.value.forEach(layer => {
        if (layer.leafletLayer) {
            try {
                // 禁用动画
                layer.leafletLayer.options.zoomAnimation = false

                // 移除所有事件监听
                layer.leafletLayer.off()

                // 清除所有瓦片
                if (typeof layer.leafletLayer._removeAllTiles === 'function') {
                    layer.leafletLayer._removeAllTiles()
                }

                // 从地图中移除
                if (map.value && map.value.hasLayer(layer.leafletLayer)) {
                    map.value.removeLayer(layer.leafletLayer)
                }

                layer.leafletLayer = null
            } catch (error) {
                console.error('MapView.vue - Error cleaning up layer:', error)
            }
        }
    })

    // 清理图
    if (baseLayer) {
        try {
            baseLayer.options.zoomAnimation = false
            baseLayer.off()
            if (typeof baseLayer._removeAllTiles === 'function') {
                baseLayer._removeAllTiles()
            }
            if (map.value && map.value.hasLayer(baseLayer)) {
                map.value.removeLayer(baseLayer)
            }
            baseLayer = null
        } catch (error) {
            console.error('MapView.vue - Error cleaning up base layer:', error)
        }
    }

    // 移除地图事件监听
    if (map.value) {
        map.value.off()
        map.value.remove()
        map.value = null
    }

    // 清理绘制相关的内容
    if (drawnItems.value) {
        map.value.removeLayer(drawnItems.value)
    }
    if (drawControl.value) {
        map.value.removeControl(drawControl.value)
    }
})

// 初始化绘制控件
const initDrawControl = () => {
    // 创建绘制图层组
    drawnItems.value = new L.FeatureGroup()

    // 配置绘制控件
    const drawOptions = {
        position: 'topleft',
        draw: {
            polyline: false,
            polygon: {
                allowIntersection: false,
                drawError: {
                    color: '#e1e100',
                    message: '<strong>误：</strong>多边形不自相交！'
                },
                shapeOptions: {
                    color: '#bada55',
                    fillOpacity: 0.5,
                }
            },
            circle: false,
            circlemarker: false,
            rectangle: {
                showArea: false,
                shapeOptions: {
                    color: '#4a80f5',
                    fill: false,
                    weight: 5,
                    clickable: true,
                },
                repeatMode: false,
                metric: false
            },
            marker: {
                icon: new L.Icon.Default(),
                repeatMode: true,
            }
        },
        edit: false
    };

    // 创建绘制控件
    drawControl.value = new L.Control.Draw(drawOptions);

    map.value.addControl(drawControl.value)

    // 修改绘制完成事件处理
    map.value.on(L.Draw.Event.CREATED, async (event) => {
        toolManager.createShape(event, layers, drawnItems, map, pointLayerCounter)
    });

    // 添加地图点击事件
    map.value.on('click', (e) => {
        toolManager.getPointLayer(layers, e, map)

    });
}

// 在 script setup 中添加
const emit = defineEmits(['map-initialized'])

// 添加矢量图层相关方法
const toggleSample = (layer) => {
    console.log('MapView.vue - toggleSample - layer:', layer);
    handleSample.toggleSample(layer, showSampleDialog, currentSampleLayer);
};

// 确认设置样本
const confirmSetSample = async () => {
    await handleSample.confirmSetSample(sampleForm, currentSampleLayer, showSampleDialog);
};

const toggleStudyArea = async (layer) => {
    try {
        // 设置加载状态
        layer.isSettingStudyArea = true
        const button = document.querySelector(`[data-layer-id="${layer.id}"] .layer-settings`)
        if (button) {
            button.disabled = true
        }

        await handleStudyArea.toggleStudyArea(layer)
    } finally {
        // 清除加载状态
        layer.isSettingStudyArea = false
        const button = document.querySelector(`[data-layer-id="${layer.id}"] .layer-settings`)
        if (button) {
            button.disabled = false
        }
    }
}

const openVectorStyleSettings = (layer) => {
    handleStyle.openVectorStyleSettings(layer, currentVectorLayer, vectorStyle, showVectorStyleDialog);
};

const applyVectorStyle = async () => {
    isApplyingStyle.value = true;
    try {
        await handleStyle.applyVectorStyle(currentVectorLayer, vectorStyle, showVectorStyleDialog, map.value);
    } finally {
        isApplyingStyle.value = false;
    }
};

// 显示图层属性方法
const showLayerProperties = async (layer) => {
    try {
        // 设置加载状态
        layer.isLoadingProperties = true
        const button = document.querySelector(`[data-layer-id="${layer.id}"] .layer-settings`)
        if (button) {
            button.disabled = true
        }

        currentLayer.value = layer
        const response = await fetch(`${API_ROUTES.LAYER.GET_PROPERTIES}?id=${layer.id}`)
        const data = await response.json()

        if (data.success) {
            layerProperties.value = Object.entries(data.properties).map(([name, value]) => ({
                name,
                value: typeof value === 'object' ? JSON.stringify(value) : value
            }))
            showPropertiesDialog.value = true
        } else {
            ElMessage.error(data.message || '获取图层属性失败')
        }
    } catch (error) {
        console.error('Error getting layer properties:', error)
        ElMessage.error('获取图层属性失败')
    } finally {
        // 清除加载状态
        layer.isLoadingProperties = false
        const button = document.querySelector(`[data-layer-id="${layer.id}"] .layer-settings`)
        if (button) {
            button.disabled = false
        }
    }
}

// 打开重命名对话框
const openRenameDialog = (layer) => {
    currentRenameLayer.value = layer
    newLayerName.value = layer.name
    showRenameDialog.value = true
}

// 导出图层方法
const exportLayer = (layer) => {
    currentExportLayer.value = layer
    showExportDialog.value = true
}

// 修改导出方法
const confirmExport = async () => {
    const layer = currentExportLayer.value
    if (!layer) return

    layer.isExporting = true

    try {
        if (exportType.value === 'drive') {
            await exportManager.exportToCloud(
                layer,
                API_ROUTES,
                exportFolder.value,
                exportScale.value
            )
        } else if (exportType.value === 'asset') {
            await exportManager.exportToAsset(
                layer,
                API_ROUTES,
                assetId.value,
                assetDescription.value,
                exportScale.value
            )
        }

        showExportDialog.value = false
        currentExportLayer.value.isExporting = false
    } catch (error) {
        currentExportLayer.value.isExporting = false
        ElMessage.error('导出图层失败')
        layer.isExporting = false
    }
}

// 在组件卸载时清理事件监听
onUnmounted(() => {
    if (map.value) {
        map.value.off('click');
    }
});

</script>

<style src="../styles/map-view.css"></style>
