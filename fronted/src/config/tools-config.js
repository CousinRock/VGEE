export const menuItems = [
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
            // ... 其他工具配置 ...
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