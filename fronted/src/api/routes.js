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
        GET_PIXEL_VALUE: `${BASE_URL}/get-pixel-value`,
        EXPORT_TO_CLOUD: `${BASE_URL}/export-to-cloud`,
        EXPORT_TO_ASSET: `${BASE_URL}/export-to-asset`,
        UPDATE_LAYER_ORDER: `${BASE_URL}/update-layer-order`,
        GEOCODE: `${BASE_URL}/map/geocode`
    },

    // 图层相关
    LAYER: {
        GET_LAYER_INFO: `${BASE_URL}/layer-info`,
        UPDATE_VIS_PARAMS: `${BASE_URL}/update-vis-params`,
        GET_PROPERTIES: `${BASE_URL}/get-properties`

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
        ADD_IMAGE_ASSET: `${BASE_URL}/upload/add-image-asset`,
        ADD_LANDSAT_TIMESERIES: `${BASE_URL}/upload/add-landsat-timeseries`,
        ADD_SENTINEL_TIMESERIES: `${BASE_URL}/upload/add-sentinel-timeseries`,
        ADD_MODIS_TIMESERIES: `${BASE_URL}/upload/add-modis-timeseries`,
        DELETE_ASSET: `${BASE_URL}/upload/delete-asset`,
        RENAME_ASSET: `${BASE_URL}/upload/rename-asset`
    },

    // 工具相关
    TOOLS: {
        //preprocessing
        GET_LAYERS: `${BASE_URL}/tools/get-layers`,
        CLOUD_REMOVAL: `${BASE_URL}/tools/cloud-removal`,
        CALCULATE_INDEX: `${BASE_URL}/tools/calculate-index`,
        IMAGE_FILLING: `${BASE_URL}/tools/image-filling`,
        RENAME_BANDS: `${BASE_URL}/tools/rename-bands`,
        HISTOGRAM_EQUALIZATION: `${BASE_URL}/tools/histogram-equalization`,
        GENERATE_RANDOM_POINTS:`${BASE_URL}/tools/generate-random-points`,
        //machine learning
        KMEANS_CLUSTERING: `${BASE_URL}/tools/kmeans-clustering`,
        RANDOM_FOREST: `${BASE_URL}/tools/random-forest`,
        SVM: `${BASE_URL}/tools/svm`,
        //raster operation
        RASTER_CALCULATOR: `${BASE_URL}/tools/raster-calculator`,
        MOSAIC: `${BASE_URL}/tools/mosaic`,
        CLIP: `${BASE_URL}/tools/clip`,
        STATISTICS: `${BASE_URL}/tools/statistics`,
        OTSU:`${BASE_URL}/tools/otsu`,
        EXTRACT: `${BASE_URL}/tools/extract`,
        CANNY: `${BASE_URL}/tools/canny`,
        TIF2VECTOR: `${BASE_URL}/tools/tif2vector`,
        //terrain operation
        TERRAIN: `${BASE_URL}/tools/terrain`
        
    },
    AI: {
        TEXT_SEGMENT: `${BASE_URL}/ai/text_segment`,
        POINT_SEGMENT: `${BASE_URL}/ai/point_segment`
    }

} 