// 在 RASTER_OPERATION 的 children 中修改 extract 配置
extract: {
    id: TOOL_IDS.RASTER_OPERATION.EXTRACT,
    label: 'Extract Values',
    icon: 'fas fa-map-pin',
    component: 'ExtractValues',
    requireLayers: true,
    endpoint: API_ROUTES.TOOLS.EXTRACT,
    description: 'Extract raster values at sample points',
    keepWindowOpen: true,
    processParams: (selectedLayers, mapView, params) => ({
        layer_ids: selectedLayers,
        vis_params: mapView.layers
            .filter(l => selectedLayers.includes(l.id))
            .map(l => ({
                id: l.id,
                visParams: l.visParams
            })),
        params: params
    }),
    processResult: (data, mapView, refs) => {
        if (refs?.extractValuesRef) {
            refs.extractValuesRef.setResult(data.results)
        }
    }
} 