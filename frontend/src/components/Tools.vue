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