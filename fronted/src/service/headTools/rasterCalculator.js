// 添加栅格计算器相关函数
export const calculatorTools = {

    /**
     * 插入运算符到表达式中，确保运算符前后有空格
     * @param {string} expression - 当前表达式
     * @param {string} operator - 要插入的运算符（如 '+', '-', '*', '/' 等）
     * @returns {string} 更新后的表达式
     */
    insertOperator: (expression, operator) => {
        return expression + ` ${operator} `
    },

    /**
     * 插入数学函数到表达式中
     * @param {string} expression - 当前表达式
     * @param {string} func - 要插入的函数名称
     * @returns {string} 更新后的表达式
     * @description 支持的函数：
     * - sqrt: 平方根
     * - pow: 幂运算
     * - exp: 指数函数
     * - log: 对数函数
     * - abs: 绝对值
     */
    insertFunction: (expression, func) => {
        switch (func) {
            case 'sqrt':
                return expression + 'sqrt('
            case 'pow':
                return expression + 'pow('
            case 'exp':
                return expression + 'exp('
            case 'log':
                return expression + 'log('
            case 'abs':
                return expression + 'abs('
            default:
                return expression
        }
    },

    /**
     * 清除整个表达式
     * @returns {string} 空字符串
     */
    clearExpression: () => {
        return ''
    },

    /**
     * 智能回退操作
     * @param {string} expression - 当前表达式
     * @returns {string} 更新后的表达式
     */
    backspace: (expression) => {
        expression = expression.trim();
        // 处理 imgX.BX 格式
        if (expression.match(/img[0-9]+\.B[0-9]+$/)) {
            const lastDotIndex = expression.lastIndexOf('.');
            if (lastDotIndex !== -1) {
                const lastImgIndex = expression.lastIndexOf('img', lastDotIndex);
                if (lastImgIndex !== -1) {
                    return expression.substring(0, lastImgIndex).trim();
                }
            }
        }
        // 处理普通波段引用
        if (expression.match(/B[0-9]+$/)) {
            const lastIndex = expression.lastIndexOf('B');
            if (lastIndex !== -1) {
                return expression.substring(0, lastIndex).trim();
            }
        }
        // 删除最后一个字符
        return expression.slice(0, -1).trim();
    }
}
