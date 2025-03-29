<template>
    <div class="calculator-options">
        <h4>Raster Calculator</h4>

        <!-- 添加计算模式选择 -->
        <div class="calc-mode">
            <h5>Calculation Mode:</h5>
            <el-radio-group v-model="calculatorParams.mode">
                <el-radio label="single">Single Band Calculation</el-radio>
                <el-radio label="multi">Multi-Layer Calculation</el-radio>
                <el-radio label="all_bands">Multi-Band Calculation</el-radio>
            </el-radio-group>
            <div class="mode-hint">
                <template v-if="calculatorParams.mode === 'single'">
                    Apply the same formula to each selected band (e.g., B4-B3)
                </template>
                <template v-if="calculatorParams.mode === 'multi'">
                    Calculation between multiple layers, generating a result (e.g., layer1.B4-layer2.B3)
                </template>
                <template v-if="calculatorParams.mode === 'all_bands'">
                    Apply the same formula to all bands of the selected layers (use x to represent band values,
                    e.g., {'x*2': ['B1','B2','B3'], 'x/2': ['B5','B6','B7']})
                </template>
            </div>
        </div>

        <!-- 添加结果处理选项 -->
        <el-form-item v-if="calculatorParams.mode === 'single'" label="Result Processing">
            <el-radio-group v-model="calculatorParams.resultMode">
                <el-radio label="new">Create New Layer</el-radio>
                <el-radio label="append">Add to Original Layer</el-radio>
            </el-radio-group>
        </el-form-item>

        <!-- 如果选择添加到原图层，显示新波段名称输入 -->
        <el-form-item v-if="calculatorParams.resultMode === 'append'" label="New Band Name">
            <el-input v-model="calculatorParams.newBandName" placeholder="Please enter the new band name" />
        </el-form-item>

        <!-- 波段列表 -->
        <div class="bands-list">
            <h5>Available Bands:</h5>
            <div class="bands-container">
                <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-bands">
                    <div class="layer-name">
                        {{availableLayers.find(l => l.id === layerId)?.name}}
                    </div>
                    <div class="band-buttons">
                        <el-button v-for="band in layerBands[layerId]" :key="band" size="small"
                            @click="handleBandClick(layerId, band)">
                            {{ band }}
                        </el-button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 运算符 -->
        <div class="operators">
            <h5>Operators:</h5>
            <div class="operator-buttons">
                <div class="operator-group">
                    <h6>Arithmetic Operators:</h6>
                    <el-button size="small" @click="insertOperator('+')">+</el-button>
                    <el-button size="small" @click="insertOperator('-')">-</el-button>
                    <el-button size="small" @click="insertOperator('*')">×</el-button>
                    <el-button size="small" @click="insertOperator('/')">/</el-button>
                    <el-button size="small" @click="insertOperator('(')">(</el-button>
                    <el-button size="small" @click="insertOperator(')')">)</el-button>
                </div>
                <div class="operator-group">
                    <h6>Comparison Operators:</h6>
                    <el-button size="small" @click="insertOperator('==')">=</el-button>
                    <el-button size="small" @click="insertOperator('!=')">&ne;</el-button>
                    <el-button size="small" @click="insertOperator('>')">&gt;</el-button>
                    <el-button size="small" @click="insertOperator('<')">&lt;</el-button>
                    <el-button size="small" @click="insertOperator('>=')">&ge;</el-button>
                    <el-button size="small" @click="insertOperator('<=')">&le;</el-button>
                </div>
                <div class="operator-group">
                    <h6>Logical Operators:</h6>
                    <el-button size="small" @click="insertOperator('&&')">AND</el-button>
                    <el-button size="small" @click="insertOperator('||')">OR</el-button>
                </div>
            </div>
        </div>

        <!-- 常用函数 -->
        <div class="functions">
            <h5>Common Functions:</h5>
            <div class="function-buttons">
                <el-button size="small" @click="insertFunction('sqrt')">sqrt</el-button>
                <el-button size="small" @click="insertFunction('pow')">pow</el-button>
                <el-button size="small" @click="insertFunction('exp')">exp</el-button>
                <el-button size="small" @click="insertFunction('log')">log</el-button>
                <el-button size="small" @click="insertFunction('abs')">abs</el-button>
            </div>
        </div>

        <!-- 计算表达式输入框 -->
        <div class="expression-input">
            <h5>Calculation Expression:</h5>
            <el-input v-model="calculatorParams.expression" type="textarea" :rows="4"
                placeholder="Click the band and operator buttons to generate the expression, or manually enter the number" />
            <div class="expression-actions">
                <el-button size="small" @click="clearExpression">Clear</el-button>
                <el-button size="small" @click="backspace">Backspace</el-button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { calculatorTools } from '../../service/headTools/rasterCalculator'

const props = defineProps({
    selectedLayerName: {
        type: Array,
        required: true
    },
    availableLayers: {
        type: Array,
        required: true
    },
    layerBands: {
        type: Object,
        required: true
    }
})

// 统一管理计算器参数
const calculatorParams = ref({
    mode: 'single',      // 计算模式
    expression: '',      // 计算表达式
    resultMode: 'new',   // 结果处理模式：'new' 或 'append'
    newBandName: ''     // 新波段名称
})

// 监听参数变化
watch(calculatorParams, (newVal) => {
    console.log('RasterCalculator.vue - watch - calculatorParams:', newVal)
}, { deep: true })

// 操作方法
const insertOperator = (operator) => {
    calculatorParams.value.expression = calculatorTools.insertOperator(
        calculatorParams.value.expression,
        operator
    )
}

const clearExpression = () => {
    calculatorParams.value.expression = ''
}

const backspace = () => {
    calculatorParams.value.expression = calculatorTools.backspace(
        calculatorParams.value.expression
    )
}

const insertFunction = (func) => {
    calculatorParams.value.expression = calculatorTools.insertFunction(
        calculatorParams.value.expression,
        func
    )
}

const handleBandClick = (layerId, band) => {
    const layerName = props.availableLayers.find(l => l.id === layerId)?.name || layerId
    if (calculatorParams.value.mode === 'multi') {
        calculatorParams.value.expression += `${layerName}.${band}`
    } else if (calculatorParams.value.mode === 'all_bands') {
        calculatorParams.value.expression += "'" + band + "'"
    } else {
        calculatorParams.value.expression += `${band}`
    }
}

// 暴露方法和状态给父组件
defineExpose({
    calculatorParams
})
</script>
