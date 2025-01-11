<template>
    <div class="calculator-options">
        <h4>栅格计算器</h4>

        <!-- 添加计算模式选择 -->
        <div class="calc-mode">
            <h5>计算模式:</h5>
            <el-radio-group v-model="calculatorMode">
                <el-radio label="single">单波段计算</el-radio>
                <el-radio label="multi">多图层计算</el-radio>
                <el-radio label="all_bands">多波段计算</el-radio>
            </el-radio-group>
            <div class="mode-hint">
                <template v-if="calculatorMode === 'single'">
                    将同一公式应用到每个选中的波段 (如: B4-B3)
                </template>
                <template v-if="calculatorMode === 'multi'">
                    多个图层之间的计算，生成一个结果 (如: layer1.B4-layer2.B3)
                </template>
                <template v-if="calculatorMode === 'all_bands'">
                    将同一公式应用到所选图层的所有波段 (使用 x 表示波段值，如:
                    {'x*2': ['B1','B2','B3'], 'x/2': ['B5','B6','B7']})
                </template>
            </div>
        </div>

        <!-- 波段列表 -->
        <div class="bands-list">
            <h5>可用波段:</h5>
            <div class="bands-container">
                <div v-for="layerId in selectedLayerName" :key="layerId" class="layer-bands">
                    <div class="layer-name">
                        {{ availableLayers.find(l => l.id === layerId)?.name }}
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
            <h5>运算符:</h5>
            <div class="operator-buttons">
                <div class="operator-group">
                    <h6>算术运算符:</h6>
                    <el-button size="small" @click="insertOperator('+')">+</el-button>
                    <el-button size="small" @click="insertOperator('-')">-</el-button>
                    <el-button size="small" @click="insertOperator('*')">×</el-button>
                    <el-button size="small" @click="insertOperator('/')">/</el-button>
                    <el-button size="small" @click="insertOperator('(')">(</el-button>
                    <el-button size="small" @click="insertOperator(')')">)</el-button>
                </div>
                <div class="operator-group">
                    <h6>比较运算符:</h6>
                    <el-button size="small" @click="insertOperator('==')">=</el-button>
                    <el-button size="small" @click="insertOperator('!=')">&ne;</el-button>
                    <el-button size="small" @click="insertOperator('>')">&gt;</el-button>
                    <el-button size="small" @click="insertOperator('<')">&lt;</el-button>
                    <el-button size="small" @click="insertOperator('>=')">&ge;</el-button>
                    <el-button size="small" @click="insertOperator('<=')">&le;</el-button>
                </div>
                <div class="operator-group">
                    <h6>逻辑运算符:</h6>
                    <el-button size="small" @click="insertOperator('&&')">AND</el-button>
                    <el-button size="small" @click="insertOperator('||')">OR</el-button>
                </div>
            </div>
        </div>

        <!-- 常用函数 -->
        <div class="functions">
            <h5>常用函数:</h5>
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
            <h5>计算表达式:</h5>
            <el-input v-model="calculatorExpression" type="textarea" :rows="4"
                placeholder="点击波段和运算符按钮生成表达式，可手动输入数字" @input="emitExpression" />
            <div class="expression-actions">
                <el-button size="small" @click="clearExpression">清除</el-button>
                <el-button size="small" @click="backspace">回退</el-button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, defineEmits } from 'vue'
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

const emit = defineEmits(['update-expression','update-calcumode']) // 定义事件

const calculatorMode = ref('single') // 计算模式
const calculatorExpression = ref('') // 计算表达式

// 在显示对话框时重置状态
watch(calculatorExpression, () => {
    emitCalculatorMode()
})

const emitExpression = () => {
    console.log('RasterCalculator.vue - emitExpression - calculatorExpression:', calculatorExpression.value)
    emit('update-expression', calculatorExpression.value) // 发出事件
}

const emitCalculatorMode = () => {
    emit('update-calcumode', calculatorMode.value) // 发出事件
}

// 调用calculatorTools.insertOperator方法将运算符插入到当前表达式中
const insertOperator = (operator) => {
    calculatorExpression.value = calculatorTools.insertOperator(calculatorExpression.value, operator)
    emitExpression() // 发出事件
    console.log('当前表达式:', calculatorExpression.value)
}

// 调用calculatorTools.clearExpression方法清空当前表达式
const clearExpression = () => {
    calculatorExpression.value = calculatorTools.clearExpression()
    emitExpression() // 发出事件
}

// 调用calculatorTools.backspace方法智能删除表达式的最后一部分
const backspace = () => {
    calculatorExpression.value = calculatorTools.backspace(calculatorExpression.value)
    emitExpression() // 发出事件
}

// 调用calculatorTools.insertFunction方法将数学函数插入到当前表达式中
const insertFunction = (func) => {
    calculatorExpression.value = calculatorTools.insertFunction(calculatorExpression.value, func)
    emitExpression() // 发出事件
}

// 修改波段点击处理方法
const handleBandClick = (layerId, band) => {
    const layerName = props.availableLayers.find(l => l.id === layerId)?.name || layerId
    console.log('RasterCalculator.vue - handleBandClick - layerName:',layerName)
    console.log('RasterCalculator.vue - handleBandClick - calculatorMode:',calculatorMode.value)
    if (calculatorMode.value === 'multi') {
        // 多图层模式：使用图层名.波段的格式
        calculatorExpression.value += `${layerName}.${band}`
    } else if (calculatorMode.value === 'all_bands') {
        calculatorExpression.value += "'"+ band +"'"
    } else {
        // 单图层模式：直接使用波段名
        calculatorExpression.value += `${band}`
    }
    emitExpression() // 发出事件
    emitCalculatorMode() // 发出事件
}

</script>

<style scoped>
/* 添加样式 */
</style>
