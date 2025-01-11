// API 路由配置
const BASE_URL = 'http://localhost:5000'

export const API_ROUTES = {
    // 地图相关
    MAP: {
        GET_MAP_DATA: `${BASE_URL}/map-data`,
        FILTER_BY_GEOMETRY: `${BASE_URL}/filter-by-geometry`,
        REMOVE_GEOMETRY: `${BASE_URL}/remove-geometry`,
        REMOVE_LAYER: `${BASE_URL}/remove-layer`,
        COMPUTE_STATS: `${BASE_URL}/compute-stats`,
        GET_SATELLITE_CONFIG: `${BASE_URL}/satellite-config`,
        ADD_SAMPLE: `${BASE_URL}/add-sample`,
        REMOVE_SAMPLE: `${BASE_URL}/remove-sample`,
        GET_SAMPLES: `${BASE_URL}/get-samples`,
        RENAME_LAYER: `${BASE_URL}/rename-layer`,
    },

    // 图层相关
    LAYER: {
        GET_LAYER_INFO: `${BASE_URL}/layer-info`,
        UPDATE_VIS_PARAMS: `${BASE_URL}/update-vis-params`,
        GET_PROPERTIES: `${BASE_URL}/get-properties`,
        EXPORT_TO_CLOUD: `${BASE_URL}/export-to-cloud`
    },

    // 搜索相关
    SEARCH: {
        SEARCH_DATA: `${BASE_URL}/search/search-data`,
        ADD_SATELLITE: `${BASE_URL}/search/add-satellite`
    },

    // 上传相关
    UPLOAD: {
        GET_ASSETS: `${BASE_URL}/upload/get-assets`,
        ADD_VECTOR_ASSET: `${BASE_URL}/upload/add-vector-asset`,
        ADD_IMAGE_ASSET: `${BASE_URL}/upload/add-image-asset`
    },

    // 工具相关
    TOOLS: {
        GET_LAYERS: `${BASE_URL}/tools/get-layers`,
        CLOUD_REMOVAL: `${BASE_URL}/tools/cloud-removal`,
        CALCULATE_INDEX: `${BASE_URL}/tools/calculate-index`,
        IMAGE_FILLING: `${BASE_URL}/tools/image-filling`,
        KMEANS_CLUSTERING: `${BASE_URL}/tools/kmeans-clustering`,
        HISTOGRAM_EQUALIZATION: `${BASE_URL}/tools/histogram-equalization`,
        RANDOM_FOREST: `${BASE_URL}/tools/random-forest`,
        RASTER_CALCULATOR: `${BASE_URL}/tools/raster-calculator`,
        RENAME_BANDS: `${BASE_URL}/tools/rename-bands`
    }
} 