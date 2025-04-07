<template>
  <div 
    v-if="isVisible" 
    class="selection-actions"
    :style="buttonStyle"
  >
    <button class="selection-action-button copy-button" @click="copySelectedText">
      <img src="@/assets/icons/chat_copy.svg" :alt="t('chat.message_actions.selected_copy')" />
    </button>
    <button class="selection-action-button note-button" @click="saveToNote">
      <img src="@/assets/icons/sys_noteedit.svg" :alt="t('chat.message_actions.selected_save')" />
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { useLocalization } from '@/i18n'

// 防抖函数
const debounce = (fn, delay) => {
  let timeout
  return function(...args) {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn.apply(this, args), delay)
  }
}

const props = defineProps({
  container: {
    type: String,
    default: 'body'
  },
  // 是否显示笔记按钮
  showNoteButton: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['save-to-note'])

const notificationStore = useNotificationStore()
const { t } = useLocalization()

// 按钮状态
const isVisible = ref(false)
const buttonPosition = ref({ x: 0, y: 0 })
const selectedText = ref('')

// 按钮样式
const buttonStyle = computed(() => {
  return {
    top: `${buttonPosition.value.y}px`,
    left: `${buttonPosition.value.x}px`
  }
})

// 处理选择文本事件
const handleSelectionChange = debounce(() => {
  const selection = window.getSelection()
  
  // 判断是否有选中文本，且选区不为空
  if (selection && selection.toString().trim() !== '') {
    selectedText.value = selection.toString()
    
    // 判断选区是否在指定容器内
    if (isSelectionInContainer(selection)) {
      // 计算按钮位置
      updateButtonPosition(selection)
      // 显示按钮
      isVisible.value = true
    } else {
      isVisible.value = false
    }
  } else {
    isVisible.value = false
  }
}, 200)

// 检查选区是否在指定容器内
const isSelectionInContainer = (selection) => {
  if (!selection || selection.rangeCount === 0) {
    return false
  }
  
  // 获取指定容器元素
  const containerElements = document.querySelectorAll(props.container)
  if (!containerElements || containerElements.length === 0) {
    return false
  }
  
  const range = selection.getRangeAt(0)
  const selectionContainer = range.commonAncestorContainer
  
  // 检查选区是否在任一指定容器内
  for (const container of containerElements) {
    if (container.contains(selectionContainer)) {
      return true
    }
  }
  
  return false
}

// 计算按钮位置
const updateButtonPosition = (selection) => {
  if (!selection || selection.rangeCount === 0) return
  
  const range = selection.getRangeAt(0)
  const rect = range.getBoundingClientRect()
  
  // 按钮位置 - 水平居中，垂直在选区上方
  const x = Math.min(
    rect.left + (rect.width / 2) - 35,  // 水平居中
    window.innerWidth - 100  // 确保不超出窗口右边界，为按钮留出空间
  )
  
  // 垂直位置 - 在选区上方
  let y = rect.top - 40
  
  // 确保按钮不超出窗口顶部
  if (y < 10) {
    y = rect.bottom + 10  // 如果上方空间不足，放在选区下方
  }
  
  buttonPosition.value = { x, y }
}

// 复制选中的文本
const copySelectedText = async () => {
  if (!selectedText.value) return
  
  try {
    await navigator.clipboard.writeText(selectedText.value)
    notificationStore.success(t('chat.notifications.copy_success'))
    // 如果没有笔记按钮，复制后隐藏
    if (!props.showNoteButton) {
      isVisible.value = false
      window.getSelection().removeAllRanges()
    }
  } catch (err) {
    notificationStore.error(t('chat.notifications.copy_error'))
  }
}

// 保存选中的文本到笔记
const saveToNote = () => {
  if (!selectedText.value) return
  
  emit('save-to-note', selectedText.value)
  
  // 隐藏按钮
  isVisible.value = false
  // 清除选择
  window.getSelection().removeAllRanges()
}

// 点击其他地方时隐藏按钮
const handleClickOutside = (event) => {
  if (isVisible.value && !event.target.closest('.selection-actions')) {
    isVisible.value = false
  }
}

// 监听页面滚动
const handleScroll = debounce(() => {
  if (isVisible.value) {
    const selection = window.getSelection()
    if (selection && selection.toString().trim() !== '') {
      updateButtonPosition(selection)
    } else {
      isVisible.value = false
    }
  }
}, 100)

// 组件挂载时添加事件监听
onMounted(() => {
  // 添加选择文本事件监听
  document.addEventListener('mouseup', handleSelectionChange)
  document.addEventListener('selectionchange', handleSelectionChange)
  // 添加点击事件监听
  document.addEventListener('click', handleClickOutside)
  // 添加滚动事件监听
  window.addEventListener('scroll', handleScroll, { passive: true })
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  document.removeEventListener('mouseup', handleSelectionChange)
  document.removeEventListener('selectionchange', handleSelectionChange)
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.selection-actions {
  position: fixed;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 32px;
  border-radius: 8px;
  background-color: var(--gray-700);
  cursor: pointer;
  z-index: 1000;
  padding: 0 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.35);
}

.selection-action-button {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  width: 32px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 0.5;
}

.selection-action-button:hover {
  opacity: 1;
}

.selection-action-button img {
  width: 16px;
  height: 16px;
  filter: var(--filter-gray-100);
}

/* 深色主题样式 */
.dark .selection-actions {
  background-color: var(--gray-800);
}
</style> 