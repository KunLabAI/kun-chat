<template>
  <div class="input-container">
      <!-- 图片预览区域 -->
      <div v-if="uploadedImage" class="image-preview">
        <img :src="uploadedImage" :alt="t('chat.input.upload_options.image')" />
        <button class="remove-image" @click="removeImage" :title="t('chat.input.remove_file')">
          <img src="@/assets/icons/chat_delmessage.svg" alt="remove-image" />
        </button>
      </div>

      <!-- 文档预览区域 -->
      <div v-if="documentContent" class="document-preview">
        <div class="file-info">
          <div class="file-icon" :class="getDocumentTypeClass">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
          </div>
          <div class="file-details">
            <div class="file-name">{{ uploadedDocument?.name }}</div>
            <div class="file-meta">
              <span class="file-type">{{ getDocumentTypeLabel }}</span>
              <span class="file-size">{{ formatFileSize(uploadedDocument?.size || 0) }}</span>
            </div>
          </div>
        </div>
        <button class="remove-document" @click="removeDocument" :title="t('chat.input.remove_file')">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="input-area">
        <!-- 主输入区域 -->
        <div class="input-controls">
          <textarea
            v-model="messageInput"
            rows="1"
            :placeholder="t('chat.input.placeholder')"
            class="message-input"
            @keydown.enter.exact.prevent="handleEnterKey"
            @keydown.enter.shift.exact.prevent="messageInput += '\n'"
            @input="handleInput"
            @keydown="handleKeyDown"
            ref="textareaRef"
          ></textarea>
          <button 
            class="send-button"
            :class="{ 'stop-button': props.isGenerating }"
            :disabled="!messageInput.trim() && !documentContent && !props.modelValue"
            @click="props.isGenerating ? stopGenerating() : sendMessage()"
            :title="props.isGenerating ? t('chat.input.stop') : t('chat.input.send')"
          >
            <svg v-if="!props.isGenerating" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="6" y="4" width="4" height="16"/>
              <rect x="14" y="4" width="4" height="16"/>
            </svg>
          </button>
        </div>

        <!-- 功能区域 -->
        <div class="function-area">
          <div class="left-functions">
            <button 
              class="model-select-btn" 
              @click="toggleModelSelect"
              :class="{ 'active': showModelSelect }"
              :data-tooltip="t('chat.input.model_select')"
            >
            <img src="@/assets/icons/chat_models.svg" alt="model-select" />

              <span>{{ getCurrentModelDisplayName }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="chevron-icon">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>
          </div>
          <div class="right-functions">
            <button 
              class="web-search-btn" 
              @click="toggleWebSearch" 
              :class="{ 'active': webSearchEnabled }" 
              :data-tooltip="t('chat.input.web_search')"
            >
              <img src="@/assets/icons/chat_websearch.svg" alt="Web Search" />
            </button>
            <div class="upload-group">
              <input type="file" ref="fileInput" accept=".jpg,.jpeg,.png,image/jpeg,image/jpg,image/png" style="display: none" @change="handleImageUpload" />
              <input 
                type="file" 
                ref="documentInput" 
                accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.csv,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv,text/plain" 
                style="display: none" 
                @change="handleDocumentUpload" 
              />
              <button 
                class="upload-btn" 
                @click="toggleUploadSelect" 
                :class="{ 'active': showUploadSelect }" 
                :data-tooltip="t('chat.input.upload_file')"
              >
                <img src="@/assets/icons/sys_fileupload.svg" alt="Upload File" />
              </button>
            </div>
            <button @click="clearConversation" class="clear-btn" :data-tooltip="t('chat.input.clear_conversation')">
              <img src="@/assets/icons/model_delete.svg" alt="clear message" />
            </button>
          </div>
        </div>

        <!-- 上传选择弹出层 -->
        <Transition name="fade">
          <div v-if="showUploadSelect" class="upload-popup">
            <div 
              class="upload-option" 
              @click="triggerImageUpload"
              :data-tooltip="t('chat.input.upload_options.image_tooltip')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <span>{{ t('chat.input.upload_options.image') }}</span>
            </div>
            <div 
              class="upload-option" 
              @click="triggerDocumentUpload"
              :data-tooltip="t('chat.input.upload_options.document_tooltip')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="9" y1="15" x2="15" y2="15"/>
              </svg>
              <span>{{ t('chat.input.upload_options.document') }}</span>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 模型选择弹出层 -->
      <Transition name="fade">
        <div v-if="showModelSelect" class="model-popup">
          <div 
            v-for="model in props.models" 
            :key="model.name"
            class="model-item"
            @click="selectModel(model)"
            :class="{ 'active': model.name === props.modelValue }"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
              <polyline points="7.5 19.79 7.5 14.6 3 12"/>
              <polyline points="21 12 16.5 14.6 16.5 19.79"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
            <span>{{ model.display_name || model.name }}</span>
          </div>
        </div>
      </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { chatApi } from '@/api/chat'
import type { Model } from '@/types/models'
import { useNotificationStore } from '@/stores/notification'
import { useChatStore } from '@/stores/chat'
import { useLocalization } from '@/i18n'
import { API_URL } from '@/api/config'

interface Props {
  models: Model[]
  modelValue: string | null
  conversationId?: string
  isGenerating?: boolean
}

interface Emits {
  'update:modelValue': [value: string | null]
  'send': [message: {
    content: string
    image?: string
    document?: {
      name: string
      type: string
      content: string
    }
  }]
  'clear': []
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const notificationStore = useNotificationStore()
const chatStore = useChatStore()
const { t } = useLocalization()

const messageInput = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const uploadedImage = ref('')
const currentImagePath = ref(null) // 
const fileInput = ref<HTMLInputElement | null>(null)
const documentInput = ref<HTMLInputElement | null>(null)
const showModelSelect = ref(false)
const showUploadSelect = ref(false)
const uploadedDocument = ref<File | null>(null)
const documentContent = ref('')
const webSearchEnabled = ref(false)

// 根据对话ID获取网页搜索状态
const updateWebSearchState = () => {
  if (props.conversationId) {
    const conversationSearchSettings = JSON.parse(localStorage.getItem('conversationWebSearchSettings') || '{}')
    webSearchEnabled.value = conversationSearchSettings[props.conversationId] === true
  } else {
    webSearchEnabled.value = false
  }
}

// 初始化时更新网页搜索状态
updateWebSearchState()

// 监听对话ID变化，更新网页搜索状态
watch(() => props.conversationId, () => {
  updateWebSearchState()
})

// 监听变化并保存到 localStorage
watch(webSearchEnabled, (newValue) => {
  if (props.conversationId) {
    const conversationSearchSettings = JSON.parse(localStorage.getItem('conversationWebSearchSettings') || '{}')
    conversationSearchSettings[props.conversationId] = newValue
    localStorage.setItem('conversationWebSearchSettings', JSON.stringify(conversationSearchSettings))
  }
})

// 获取当前选中的模型
const currentModel = computed(() => {
  return props.models.find(model => model.name === props.modelValue)
})

// 获取当前模型的显示名称
const getCurrentModelDisplayName = computed(() => {
  return currentModel.value?.display_name || currentModel.value?.name || '选择模型'
})

// 处理输入
const handleInput = (event: Event) => {
  const textarea = event.target as HTMLTextAreaElement
  messageInput.value = textarea.value
  adjustTextareaHeight()
}

// 处理键盘事件
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    showModelSelect.value = false
    showUploadSelect.value = false
    return
  }

  if (event.key === 'Enter' && !event.shiftKey) {
    if (showModelSelect.value || showUploadSelect.value) {
      event.preventDefault()
      showModelSelect.value = false
      showUploadSelect.value = false
      return
    }
  }
}

// 选择模型
const selectModel = async (model: Model) => {
  try {
    emit('update:modelValue', model.name)
    // 更新当前模型，并同步到后端
    await chatStore.setCurrentModel(
      model.name, 
      chatStore.currentConversationId, 
      true // 更新后端
    )
    showModelSelect.value = false
    notificationStore.success(t('chat.notifications.model_switch_success', { model: model.display_name || model.name }))
  } catch (err) {
    const error = err instanceof Error ? err.message : '未知错误'
    notificationStore.error(t('chat.notifications.model_switch_error', { error }))
  }
}

// 切换模型选择弹出层
const toggleModelSelect = () => {
  showModelSelect.value = !showModelSelect.value
  if (showModelSelect.value) {
    showUploadSelect.value = false
  }
}

// 切换上传选择弹出层
const toggleUploadSelect = () => {
  showUploadSelect.value = !showUploadSelect.value
  if (showUploadSelect.value) {
    showModelSelect.value = false
  }
}

// 触发文件选择
const triggerImageUpload = () => {
  fileInput.value?.click()
  showUploadSelect.value = false
}

// 触发文档上传
const triggerDocumentUpload = () => {
  documentInput.value?.click()
  showUploadSelect.value = false
}

// 移除图片
const removeImage = () => {
  uploadedImage.value = ''
  if (messageInput.value.startsWith('![')) {
    const endIndex = messageInput.value.indexOf(')')
    if (endIndex !== -1) {
      messageInput.value = messageInput.value.substring(endIndex + 1).trim()
    }
  }
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  currentImagePath.value = null // 
}

// 移除文档
const removeDocument = () => {
  uploadedDocument.value = null
  documentContent.value = ''
  if (documentInput.value) {
    documentInput.value.value = ''
  }
}

// 处理图片上传
async function handleImageUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  try {
    const file = input.files[0]
    showUploadSelect.value = false

    // 构建FormData
    const formData = new FormData()
    formData.append('file', file)

    // 使用完整的 API URL 而不是相对路径
    const response = await fetch(`${API_URL}/images/upload`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error('上传失败')
    }

    const data = await response.json()
    if (data.success) {
      uploadedImage.value = data.image_data
      currentImagePath.value = null // 
      notificationStore.success(t('chat.notifications.image_upload_success'))
    } else {
      throw new Error('上传失败')
    }
  } catch (error) {
    console.error('图片上传错误:', error)
    notificationStore.error(t('chat.notifications.image_upload_error'))
  } finally {
    // 重置文件输入，允许重新选择相同的文件
    fileInput.value = null
  }
}

// 处理文档上传
const handleDocumentUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  const file = input.files[0]
  try {
    if (!props.conversationId) {
      throw new Error('会话ID不存在')
    }
    const result = await chatApi.convertDocument(file, props.conversationId)
    uploadedDocument.value = file
    documentContent.value = result.content
    // 重置文件输入，允许重新选择相同的文件
    documentInput.value = null
    notificationStore.success(t('chat.notifications.document_upload_success'))
  } catch (error) {
    console.error('文档转换失败:', error)
    notificationStore.error(t('chat.notifications.document_upload_error'))
  }
}

// 处理回车键
const handleEnterKey = () => {
  // 如果模型选择框打开，选择当前选中的模型
  if (showModelSelect.value && props.models.length > 0) {
    selectModel(props.models[0])
    return
  }
  
  // 否则发送消息
  if ((messageInput.value.trim() || documentContent.value) && props.modelValue && !props.isGenerating) {
    sendMessage()
  }
}

// 监听 messageInput 的变化，实时调整高度
watch(messageInput, () => {
  adjustTextareaHeight()
})

// 调整textarea高度
const adjustTextareaHeight = () => {
  const textarea = textareaRef.value
  if (!textarea) return
  
  // 如果内容为空，直接设置为初始高度
  if (!messageInput.value.trim()) {
    textarea.style.height = 'calc(1.6rem + 16px)'
    return
  }
  
  // 临时设置高度为0，以便正确计算 scrollHeight
  textarea.style.height = '0'
  
  // 计算内容实际需要的高度
  const contentHeight = textarea.scrollHeight
  const maxHeight = parseInt(getComputedStyle(textarea).maxHeight)
  const minHeight = parseInt(getComputedStyle(textarea).minHeight)
  
  // 根据内容设置合适的高度
  const newHeight = Math.min(Math.max(contentHeight, minHeight), maxHeight)
  textarea.style.height = `${newHeight}px`
}

// 发送消息函数
const sendMessage = async (): Promise<void> => {
  if (!messageInput.value.trim() && !documentContent.value) return
  if (!props.modelValue || props.isGenerating) return

  const messageData: {
    content: string
    image?: string
    document?: {
      name: string
      content: string
      type: string
    }
    web_search?: boolean
  } = {
    content: messageInput.value.trim(),
    web_search: webSearchEnabled.value
  }

  if (uploadedImage.value) {
    messageData.image = uploadedImage.value
  }

  if (documentContent.value && uploadedDocument.value) {
    messageData.document = {
      name: uploadedDocument.value.name,
      content: documentContent.value,
      type: uploadedDocument.value.type
    }
  }

  emit('send', messageData)
  messageInput.value = ''
  uploadedImage.value = ''
  currentImagePath.value = null // 
  uploadedDocument.value = null
  documentContent.value = ''
  
  // 重置输入框高度
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
}

// 停止生成
const stopGenerating = () => {
  chatStore.stopGenerating()
}

// 清空对话
const clearConversation = () => {
  try {
    emit('clear')
  } catch {
  }
}

// 添加提示框位置更新函数
const updateTooltipPosition = (event: MouseEvent) => {
  // 不再需要复杂的定位逻辑
  // 所有提示框现在都使用相对于父元素的固定位置
}

// 点击外部区域关闭弹窗
const handleClickOutsideModel = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  const popup = document.querySelector('.model-popup')
  const button = target.closest('button')
  
  if (popup && !popup.contains(target) && !button?.classList.contains('model-select-btn')) {
    showModelSelect.value = false
  }
}

const handleClickOutsideUpload = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  const popup = document.querySelector('.upload-popup')
  const button = target.closest('button')
  
  if (popup && !popup.contains(target) && !button?.classList.contains('upload-btn')) {
    showUploadSelect.value = false
  }
}

const handleEscKeyModel = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    showModelSelect.value = false
  }
}

const handleEscKeyUpload = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    showUploadSelect.value = false
  }
}

// 监听模型选择弹窗的显示状态
watch(() => showModelSelect.value, (newValue) => {
  if (newValue) {
    document.addEventListener('click', handleClickOutsideModel)
    document.addEventListener('keydown', handleEscKeyModel)
  } else {
    document.removeEventListener('click', handleClickOutsideModel)
    document.removeEventListener('keydown', handleEscKeyModel)
  }
})

// 监听上传弹窗的显示状态
watch(() => showUploadSelect.value, (newValue) => {
  if (newValue) {
    document.addEventListener('click', handleClickOutsideUpload)
    document.addEventListener('keydown', handleEscKeyUpload)
  } else {
    document.removeEventListener('click', handleClickOutsideUpload)
    document.removeEventListener('keydown', handleEscKeyUpload)
  }
})

const toggleWebSearch = () => {
  webSearchEnabled.value = !webSearchEnabled.value
  if (webSearchEnabled.value) {
      notificationStore.info(t('chat.notifications.web_search_enabled'))
  } else {
    notificationStore.info(t('chat.notifications.web_search_disabled'))
  }
}

const getDocumentTypeClass = computed(() => {
  if (!uploadedDocument.value) return ''
  const type = uploadedDocument.value.type
  if (type.startsWith('image/')) return 'image-icon'
  if (type.startsWith('application/pdf')) return 'pdf-icon'
  if (type.startsWith('application/msword') || type.startsWith('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) return 'word-icon'
  if (type.startsWith('application/vnd.ms-powerpoint') || type.startsWith('application/vnd.openxmlformats-officedocument.presentationml.presentation')) return 'ppt-icon'
  if (type.startsWith('application/vnd.ms-excel') || type.startsWith('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) return 'excel-icon'
  if (type.startsWith('text/plain') || type.startsWith('text/txt')) return 'txt-icon'
  return 'file-icon'
})

const getDocumentTypeLabel = computed(() => {
  if (!uploadedDocument.value) return ''
  const type = uploadedDocument.value.type
  if (type.startsWith('application/pdf')) return t('chat.file_preview.file_types.pdf')
  if (type.startsWith('application/msword') || type.startsWith('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) return t('chat.file_preview.file_types.word')
  if (type.startsWith('application/vnd.ms-powerpoint') || type.startsWith('application/vnd.openxmlformats-officedocument.presentationml.presentation')) return t('chat.file_preview.file_types.ppt')
  if (type.startsWith('application/vnd.ms-excel') || type.startsWith('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) return t('chat.file_preview.file_types.excel')
  if (type.startsWith('text/csv')) return t('chat.file_preview.file_types.csv')
  if (type.startsWith('text/plain')) return t('chat.file_preview.file_types.text')
  return t('chat.file_preview.file_types.document')
})

const formatFileSize = (size: number) => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(2)} MB`
  return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`
}
</script>

<style scoped>
@import './ChatInput.css';
</style>
