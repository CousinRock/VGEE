// API 路由配置
const BASE_URL = 'http://localhost:5000'

export const API_ROUTES = {
    // 地图相关
    MAP: {
        GET_MAP_DATA: `${BASE_URL}/map-data`,
        FILTER_BY_GEOMETRY: `${BASE_URL}/filter-by-geometry`,
        REMOVE_GEOMETRY: `${BASE_URL}/remove-geometry`,
        REMOVE_LAYER: `${BASE_URL}/remove-layer`,
        COMPUTE_STATS: `${BASE_URL}/compute-stats`
    },

    // 图层相关
    LAYER: {
        GET_LAYER_INFO: `${BASE_URL}/layer-info`,
        UPDATE_VIS_PARAMS: `${BASE_URL}/update-vis-params`
    },

    // 工具相关
    TOOLS: {
        GET_LAYERS: `${BASE_URL}/tools/get-layers`,
        CLOUD_REMOVAL: `${BASE_URL}/tools/cloud-removal`,
        CALCULATE_INDEX: `${BASE_URL}/tools/calculate-index`,
        IMAGE_FILLING: `${BASE_URL}/tools/image-filling`
    }
} 