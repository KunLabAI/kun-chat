<template>
  <Transition name="dialog-fade">
    <div v-if="modelValue" class="kun-dialog-container">
        
      <!-- 弹窗内容 -->
      <div class="kun-dialog-content">
        <!-- 头部 -->
        <div class="kun-dialog-header">
          <h3 class="kun-dialog-title">
            {{ title }}
          </h3>
        </div>

        <!-- 内容区域 -->
        <div class="kun-dialog-body">
          <slot></slot>
        </div>

        <!-- 底部按钮区域 -->
        <div class="kun-dialog-footer">
          <button
            @click="$emit('update:modelValue', false)"
            class="kun-dialog-btn kun-dialog-cancel-btn"
          >
            {{ cancelText }}
          </button>
          <button
            @click="$emit('confirm')"
            class="kun-dialog-btn kun-dialog-confirm-btn"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: 'Dialog'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  }
})

defineEmits(['update:modelValue', 'confirm'])
</script>

<style scoped>
/* 弹窗容器 */
.kun-dialog-container {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
}

/* 弹窗内容 */
.kun-dialog-content {
  position: relative;
  max-width: 28rem;
  width: 100%;
  margin-left: 1rem;
  margin-right: 1rem;
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  transform: scale(1);
  transition: all 0.3s;
  background-color: var(--bg-color-light);
  border: 1px solid var(--border-color);
}

/* 深色模式弹窗内容 */
:global(.dark) .kun-dialog-content {
  background-color: var(--gray-800);
  border-color: var(--gray-700);
}

/* 弹窗头部 */
.kun-dialog-header {
  padding: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--button-secondary-hover);
}

/* 深色模式弹窗头部 */
:global(.dark) .kun-dialog-header {
  border-color: var(--gray-700);
}

/* 弹窗标题 */
.kun-dialog-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

/* 弹窗内容区域 */
.kun-dialog-body {
  padding: 1.5rem;
  color: var(--text-color-light);
}

/* 弹窗底部 */
.kun-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--button-secondary-hover);
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  background-color: var(--bg-color-light);
}

/* 深色模式弹窗底部 */
:global(.dark) .kun-dialog-footer {
  background-color: var(--gray-700);
  border-color: var(--gray-700);
}

/* 按钮基础样式 */
.kun-dialog-btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  transition: all 0.2s;
  cursor: pointer;
}

/* 取消按钮 */
.kun-dialog-cancel-btn {
  color: var(--text-color-light);
  background-color: var(--button-bg);
  border: 1px solid var(--button-border);
}

.kun-dialog-cancel-btn:hover {
  background-color: var(--button-hover-bg);
  border-color: var(--button-hover-border);
}

/* 深色模式取消按钮 */
:global(.dark) .kun-dialog-cancel-btn {
  color: var(--gray-300);
  background-color: var(--gray-700);
  border-color: var(--gray-600);
}

:global(.dark) .kun-dialog-cancel-btn:hover {
  background-color: var(--gray-600);
  border-color: var(--gray-500);
}

/* 确认按钮 */
.kun-dialog-confirm-btn {
  color: white;
  background-color: var(--primary-600);
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid transparent;
}

.kun-dialog-confirm-btn:hover {
  background-color: var(--primary-700);
}

/* 深色模式确认按钮 */
:global(.dark) .kun-dialog-confirm-btn {
  background-color: var(--primary-500);
}

:global(.dark) .kun-dialog-confirm-btn:hover {
  background-color: var(--primary-600);
}

/* 过渡动画 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-from .kun-dialog-content,
.dialog-fade-leave-to .kun-dialog-content {
  transform: scale(0.95) translateY(-20px);
}
</style>
