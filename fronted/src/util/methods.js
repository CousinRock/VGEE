// 添加一个范围标准化函数
export const normalizeRange = (min, max) => {
    // 确保min和max是数字
    min = Number(min);
    max = Number(max);

    // 处理无效值
    if (isNaN(min) || isNaN(max)) {
        return { min: 0, max: 1 }; // 默认返回0-1范围
    }

    // 如果最大值小于最小值，交换它们
    if (max < min) {
        [min, max] = [max, min];
    }

    // 计算数值范围
    const range = max - min;
    console.log('normalizeRange - range', range);

    // 计算最接近的2的幂次方
    const magnitude = Math.floor(Math.log2(range));
    console.log('normalizeRange - magnitude', magnitude);

    // 根据2的幂次方调整范围
    const step = Math.pow(2, magnitude);
    console.log('normalizeRange - step', step);

    // 向下和向上取整到最近的2的幂次方的倍数
    const normalizedMin = Math.floor(min / step) * step;
    console.log('normalizeRange - normalizedMin', normalizedMin);
    const normalizedMax = Math.ceil(max / step) * step;
    console.log('normalizeRange - normalizedMax', normalizedMax);

    console.log(`Original range: ${min} to ${max}`);
    console.log(`Normalized range: ${normalizedMin} to ${normalizedMax}`);

    return {
        min: normalizedMin,
        max: normalizedMax
    };
};

//彻底移除图层实例
export const layerChangeRemove = (map, layer) => {
    let mapLayers = Object.values(map._layers);
    mapLayers.forEach((mapLayer) => {
        if (mapLayer instanceof L.TileLayer &&
            mapLayer !== layer &&
            mapLayer._leaflet_id === layer._leaflet_id) {
            map.removeLayer(mapLayer)
        }
    });
}