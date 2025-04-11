<template>
  <Dialog
    v-model="isVisible"
    :title="t('model.gpu_calculator.title')"
    :confirmText="t('model.gpu_calculator.close_button')"
    :hideCancelButton="true"
    @confirm="closeDialog"
  >
    <div class="gpu-calculator">
      <!-- 参数输入区域 -->
      <div class="input-section">
        <div class="param-input">
          <label class="input-label">{{ t('model.gpu_calculator.parameter_count') }}</label>
          <div class="input-wrapper">
            <input
              v-model="parameterCount"
              type="number"
              step="0.1"
              class="param-input-field"
              :placeholder="t('model.gpu_calculator.placeholder')"
            />
            <div class="input-suffix">{{ t('model.gpu_calculator.parameter_unit') }}</div>
          </div>
        </div>

        <div class="quant-input">
          <label class="input-label">{{ t('model.gpu_calculator.quantization_bits') }}: <span class="highlight">{{ quantizationBits }}bit</span></label>
          <div class="slider-container">
            <div class="slider-wrapper">
              <input
                v-model="quantizationBits"
                type="range"
                min="1"
                max="32"
                :step="1"
                class="quant-slider"
              />
              <div class="slider-track-bg"></div>
              <div class="slider-track-fill" :style="{ width: `${(quantizationBits - 1) / 31 * 100}%` }"></div>
            </div>
            
            <div class="bits-markers">
              <span>1</span>
              <span>8</span>
              <span>16</span>
              <span>24</span>
              <span>32</span>
            </div>
          </div>
          
          <div class="bit-buttons">
            <button 
              v-for="bit in [1, 2, 3, 4, 8, 16, 32]" 
              :key="bit"
              @click="quantizationBits = bit"
              :class="['bit-btn', quantizationBits === bit ? 'bit-btn-active' : '']"
            >
              {{ bit }}bit
            </button>
          </div>
        </div>
      </div>

      <!-- 结果区域 -->
      <div class="result-section">
        <div class="memory-result">
          <div class="result-label">{{ t('model.gpu_calculator.memory_required') }}</div>
          <div class="result-value">{{ calculatedMemory }}</div>
          <div class="memory-visualization" :style="{ width: `${Math.min(100, getMemoryValue(calculatedMemory.toString()) * 2)}%` }"></div>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, defineExpose } from 'vue'
import Dialog from '@/components/common/Dialog.vue'
import { useLocalization } from '@/i18n/composables'

const { t } = useLocalization()
const isVisible = ref(false)
const parameterCount = ref<number>(0)
const quantizationBits = ref<number>(4) // 默认4位量化

const calculatedMemory = computed(() => {
  if (!parameterCount.value || !quantizationBits.value) return 0
  
  // 计算公式: M = ((P * 4B) / (32/Q)) * 1.2
  // P: 参数数量(十亿)
  // Q: 量化位数
  // 4B: 每个参数占用4字节(全精度)
  // 32: 全精度位数
  // 1.2: 开销因子
  
  // 直接计算GB单位结果
  const memoryGB = ((parameterCount.value * 4) / (32 / quantizationBits.value)) * 1.2
  
  // 格式化显示，根据数值大小选择合适的表示方式
  if (memoryGB >= 1000000) {
    // 超过1000000GB (1000TB, 1PB)，使用PB单位
    return (memoryGB / 1000000).toFixed(2) + 'PB'
  } else if (memoryGB >= 1000) {
    // 超过1000GB (1TB)，使用TB单位
    return (memoryGB / 1000).toFixed(2) + 'TB'
  } else if (memoryGB >= 100) {
    // 超过100GB，保留整数
    return Math.round(memoryGB) + 'GB'
  } else {
    // 小于100GB，保留2位小数
    return memoryGB.toFixed(2) + 'GB'
  }
})

// 打开弹窗
const openDialog = () => {
  isVisible.value = true
}

// 关闭弹窗
const closeDialog = () => {
  isVisible.value = false
}

// 添加提取数值的辅助函数
const getMemoryValue = (memoryString: string): number => {
  // 从结果字符串中提取数值部分
  const numericValue = parseFloat(memoryString.replace(/[^0-9.]/g, ''))
  
  // 根据单位转换为GB进行显示
  if (memoryString.includes('PB')) {
    return numericValue * 1000000 / 1000; // 限制最大显示比例
  } else if (memoryString.includes('TB')) {
    return numericValue * 1000 / 100; // 限制最大显示比例
  }
  
  return Math.min(numericValue, 100); // 限制最大值为100
}

// 暴露方法给父组件调用
defineExpose({
  openDialog,
  closeDialog
})
</script>

<style scoped>
.gpu-calculator {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 8px;
  font-family: var(--font-family);
}

/* 输入区域样式 */
.input-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.param-input, .quant-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.highlight {
  color: var(--primary-600);
  font-weight: 600;
}

.dark .highlight {
  color: var(--primary-400);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.param-input-field {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--bg-color-light);
  color: var(--text-color);
  font-size: 0.95rem;
  transition: all 0.2s ease;
  padding-right: 24px;
}

.dark .param-input-field {
  background-color: var(--gray-800);
  border-color: var(--gray-700);
}

.param-input-field:focus {
  border-color: var(--primary-500);
}

.dark .param-input-field:focus {
  border-color: var(--primary-500);
  background-color: var(--gray-900);
}

.param-input-field::-webkit-inner-spin-button {
  opacity: 1;
  position: absolute;
  right: 8px;
  height: 20px;
}

.input-suffix {
  position: absolute;
  right: 30px;
  color: var(--text-color-light);
  font-size: 0.9rem;
  font-weight: 500;
  pointer-events: none;
}

/* 滑块样式 */
.slider-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.slider-wrapper {
  position: relative;
  height: 36px;
  display: flex;
  align-items: center;
}

.quant-slider {
  appearance: none;
  width: 100%;
  height: 4px;
  background: transparent;
  position: relative;
  z-index: 2;
  cursor: pointer;
}

.slider-track-bg {
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background-color: var(--gray-200);
  transform: translateY(-50%);
  z-index: 1;
}

.dark .slider-track-bg {
  background-color: var(--gray-700);
}

.slider-track-fill {
  position: absolute;
  top: 50%;
  left: 0;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(to right, var(--primary-400), var(--primary-600));
  transform: translateY(-50%);
  z-index: 1;
  transition: width 0.05s ease;
}

.dark .slider-track-fill {
  background: linear-gradient(to right, var(--primary-800), var(--primary-500));
}

.bits-markers {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-color-light);
  margin-top: -4px;
}

.quant-slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary-600);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  z-index: 3;
  transition: all 0.2s ease;
}

.quant-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary-600);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  z-index: 3;
  border: none;
  transition: all 0.2s ease;
}

.dark .quant-slider::-webkit-slider-thumb {
  background: var(--primary-500);
  box-shadow: 0 2px 8px rgba(168, 85, 247, 0.4);
}

.dark .quant-slider::-moz-range-thumb {
  background: var(--primary-500);
  box-shadow: 0 2px 8px rgba(168, 85, 247, 0.4);
}

.quant-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.quant-slider::-moz-range-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 位数按钮 */
.bit-buttons {
  display: flex;
  flex-wrap: wrap;
  margin-top: 6px;
  justify-content:space-between;
}

.bit-btn {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  background-color: var(--gray-100);
  color: var(--text-color-light);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dark .bit-btn {
  background-color: var(--gray-800);
  color: var(--gray-300);
}

.bit-btn:hover {
  background-color: var(--gray-200);
}

.dark .bit-btn:hover {
  background-color: var(--gray-700);
}

.bit-btn-active {
  background-color: var(--primary-500);
  color: white;
}

.bit-btn-active:hover {
  background-color: var(--primary-600);
}

.dark .bit-btn-active {
  background-color: var(--primary-600);
}

.dark .bit-btn-active:hover {
  background-color: var(--primary-700);
}

/* 结果区域样式 */
.result-section {
  background: linear-gradient(to right, var(--primary-50), var(--gray-50));
  border-radius: 12px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--primary-100);
}

.dark .result-section {
  background: linear-gradient(to right, var(--primary-900), var(--gray-900));
  border: 1px solid var(--primary-800);
}

.memory-result {
  position: relative;
  z-index: 2;
}

.result-label {
  font-size: 0.9rem;
  color: var(--text-color-light);
  margin-bottom: 8px;
}

.result-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-700);
  display: flex;
  align-items: baseline;
}

.dark .result-value {
  color: var(--primary-400);
}

.result-unit {
  font-size: 1.2rem;
  color: var(--text-color-light);
  margin-left: 4px;
}

.memory-visualization {
  height: 4px;
  background: linear-gradient(to right, var(--primary-400), var(--primary-600));
  border-radius: 2px;
  margin-top: 12px;
  transition: width 0.5s ease-out;
}

.dark .memory-visualization {
  background: linear-gradient(to right, var(--primary-500), var(--primary-300));
}

/* 公式说明区域 */
.formula-section {
  padding: 16px;
  background-color: var(--bg-color-light);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.dark .formula-section {
  background-color: var(--gray-800);
  border: 1px solid var(--gray-700);
}

.formula-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 12px;
}

.formula-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.formula-expression {
  font-family: var(--font-family-mono);
  font-size: 0.9rem;
  color: var(--text-color);
  background-color: var(--bg-color);
  padding: 10px 14px;
  border-radius: 6px;
  white-space: nowrap;
  overflow-x: auto;
}

.dark .formula-expression {
  background-color: var(--gray-900);
}

.formula-legend {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-color-light);
}

.legend-item {
  display: flex;
  gap: 4px;
}

.legend-item span {
  font-weight: 600;
  color: var(--primary-700);
}

.dark .legend-item span {
  color: var(--primary-400);
}

/* 使计算器在小屏幕上响应式 */
@media (max-width: 480px) {
  .gpu-calculator {
    padding: 0;
  }
  
  .result-value {
    font-size: 1.7rem;
  }
  
  .result-unit {
    font-size: 1rem;
  }
  
  .formula-legend {
    grid-template-columns: 1fr 1fr;
  }
}
</style> 