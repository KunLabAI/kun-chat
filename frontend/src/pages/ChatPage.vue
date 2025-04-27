<template>
  <MainLayout>
    <div class="chat-container" ref="chatContainer" :class="{ 'with-drawer': isNoteDrawerOpen }">
      <!-- 消息列表 -->
      <div class="messages-container">
        <div
          v-for="message in chatStore.messages"
          :key="message.timestamp"
          class="message-group"
          :class="message.role === 'user' ? 'message-group-user' : 'message-group-assistant'"
        >
          <!-- 用户头像 -->
          <div v-if="message.role === 'user'" class="avatar-container">
            <div class="user-avatar-background">
              <img :src="userAvatarUrl" alt="User" class="user-avatar" />
            </div>
          </div>
          <!-- AI头像 -->
          <div v-else class="avatar-container">
            <BubbleAvatar />
          </div>
          <div class="message-bubble">
            <!-- 如果是最后一条AI消息且模型正在加载，显示立方体动画 -->
            <div v-if="isLastAssistantMessage(message) && chatStore.aiStatus.model === 'loading'" class="loading-container">
              <div class="spinner">
                <div></div><div></div><div></div><div></div><div></div><div></div>
              </div>
            </div>
            <!-- PDF预览 -->
            <div v-if="message.pdf" class="message-file-preview">
              <div class="file-icon pdf">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="12" y1="18" x2="12" y2="12"/>
                  <line x1="9" y1="15" x2="15" y2="15"/>
                </svg>
              </div>
              <div class="file-info">
                <span class="file-name">{{ message.pdf.name }}</span>
                <span class="file-type">{{ t('chat.file_preview.pdf_document') }}</span>
              </div>
            </div>
            <!-- 显示图片 -->
            <div v-if="message.image_path || message.image || (message.images && message.images.length > 0)" class="message-image">
              <img 
                :src="getMessageImageSrc(message)"
                @load="scrollToBottom"
                @click="openImagePreview(getMessageImageSrc(message))"
                alt="Message image"
              />
            </div>
            <!-- 显示文档 -->
            <div v-if="message.document" class="message-file-preview">
              <div class="file-info">
                <div class="file-icon" :class="getDocumentTypeClass(message.document.type)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                  </svg>
                </div>
                <div class="file-details">
                  <div class="file-name">{{ message.document.name }}</div>
                  <div class="file-meta">
                    <span class="file-type">{{ getFileType(message.document.type) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="message.document && message.showDocument" class="document-content">
              <MarkdownRenderer :content="message.document.content" />
            </div>
            <!-- 网页搜索指示器 - 当工具状态为网页搜索且消息内容为空时显示 -->
            <!-- 注意：只有当模型不在加载中且网页搜索功能已启用时才显示网页搜索动画 -->
            <WebSearchIndicator 
              v-if="message.role === 'assistant' && isLastAssistantMessage(message) && 
                    chatStore.aiStatus.tool === ToolStatus.WEB_SEARCH && 
                    chatStore.aiStatus.model !== ModelStatus.LOADING && 
                    chatStore.aiStatus.webSearchEnabled && 
                    (!message.content || message.content.trim() === '')"
              ref="webSearchIndicatorRef"
            />
            
            <!-- 显示文本内容 -->
            <template v-if="message.content">
              <!-- 思考过程 -->
              <div 
                v-if="message.role === 'assistant' && hasThinkingContent(message.content)" 
                class="thinking-process"
                :class="{ 
                  'thinking-process-active': isActiveThinking(message) || chatStore.aiStatus.thinking === 'thinking',
                  'thinking-process-completed': chatStore.aiStatus.thinking === 'completed'
                }"
              >
                <div class="thinking-process-header">
                  <span class="thinking-title">
                    {{ isActiveThinking(message) ? t('chat.thinking_process.title') : t('chat.thinking_process.title') }}
                    <span class="thinking-time">
                      {{ t('chat.thinking_process.time', [getThinkingTime(message)]) }}
                    </span>
                  </span>
                  <span v-if="isActiveThinking(message) || chatStore.aiStatus.thinking === 'thinking'" class="thinking-dots"></span>
                  <div class="thinking-toggle" @click="toggleThinkingProcess(message)">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'rotate-180': message.showThinking }">
                      <path d="M19 9l-7 7-7-7"/>
                    </svg>
                  </div>
                </div>
                <div v-show="message.showThinking" class="thinking-process-content">
                  {{ formatThinkContent(extractThinkContent(message.content)) }}
                </div>
              </div>
              <div v-if="!hasThinkingContent(message.content) || extractFinalContent(message.content)">
                <!-- 用户消息使用纯文本渲染器 -->
                <PlainTextRenderer 
                  v-if="message.role === 'user'" 
                  :content="message.content" 
                  :max-lines="5" 
                  @contentRendered="handleContentRendered"
                />
                <!-- AI消息使用Markdown渲染器 -->
                <div v-else>
                  <!-- 正常显示内容 -->
                  <MarkdownRenderer 
                    :content="extractFinalContent(message.content) || message.content" 
                    :key="`content-${message.id}`"
                    @contentRendered="handleContentRendered"
                  />
                </div>
              </div>
            </template>
            
            <!-- 消息操作区域 -->
            <div v-if="message.role === 'assistant'" class="message-footer">
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              <!-- 使用独立的操作区域，避免内容更新时重新渲染 -->
              <div class="message-actions">
                <button @click="copyMessage(message.content)" :title="t('chat.message_actions.copy')">
                  <img src="@/assets/icons/chat_copy.svg" :alt="t('chat.message_actions.copy')" />
                </button>
                <button @click="deleteMessage(message)" :title="t('chat.message_actions.delete')">
                  <img src="@/assets/icons/chat_delmessage.svg" :alt="t('chat.message_actions.delete')" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      
      <!-- 滚动到底部按钮 -->
      <div 
        class="scroll-to-bottom" 
        :class="{ visible: !shouldAutoScroll }"
        @click="scrollToBottom(true, true)"
      >
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z" transform="rotate(180 12 12)"/>
        </svg>
      </div>

      <!-- 输入区域 -->
      <ChatInput
        :models="modelsStore.models"
        v-model="chatStore.currentModel"
        :is-generating="chatStore.isGenerating"
        :conversation-id="route.params.conversationId"
        @send="handleSendMessage"
        @clear="showConfirmDialog = true"
      />

      <!-- 确认清空对话弹窗 -->
      <Dialog
        v-model="showConfirmDialog"
        :title="t('chat.confirm_clear.title')"
        :confirmText="t('common.actions.confirm')"
        :cancelText="t('common.actions.cancel')"
        @confirm="handleConfirmClear"
      >
        <p class="text-gray-600 dark:text-gray-300">
          {{ t('chat.confirm_clear.message') }}
        </p>
      </Dialog>
      <!-- 确认刷新页面弹窗 -->
      <Dialog
        v-model="showRefreshConfirmDialog"
        :title="t('chat.confirm_refresh.title')"
        :confirmText="t('common.actions.confirm')"
        :cancelText="t('common.actions.cancel')"
        @confirm="handleConfirmRefresh"
        @update:modelValue="handleRefreshDialogUpdate"
      >
        <p class="text-gray-600 dark:text-gray-300">
          {{ t('chat.confirm_refresh.message') }}
        </p>
      </Dialog>
      
      <!-- 选中文本操作按钮 -->
      <SelectionActionButton 
        container=".message-bubble, .markdown-content" 
        @save-to-note="handleSaveToNote"
      />

      <!-- 图片预览模态框 -->
      <div v-if="showImagePreview" class="image-preview-modal" @click="closeImagePreview">
        <div class="modal-content" @click.stop>
          <img :src="previewImageUrl" alt="图片预览" class="full-size-image" />
          <button class="close-button" @click="closeImagePreview">
            <img src="@/assets/icons/sys_close.svg" alt="关闭" class="close-icon" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- 笔记抽屉组件 - 移到MainLayout下，但在chat-container外部 -->
    <template #drawer>
      <NoteDrawer
        ref="noteDrawerRef"
        :is-open="isNoteDrawerOpen"
        :initial-content="selectedTextForNote"
        :conversation-id="route.params.conversationId"
        @close="isNoteDrawerOpen = false"
        @saved="handleNoteSaved"
      />
    </template>
  </MainLayout>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useChatStore, GenerationStatus, ThinkingStatus, ToolStatus, ModelStatus } from '@/stores/chat'
import { useModelsStore } from '@/stores/models'
import { useNotificationStore } from '@/stores/notification'
import { useAuthStore } from '@/stores/auth'
import { useLocalization } from '@/i18n'
import { hasThinkingContent, extractThinkContent, extractFinalContent, formatThinkContent } from '@/states/aiStates'
import MainLayout from '@/layouts/MainLayout.vue'
import ChatInput from '@/components/chat/InputArea/ChatInput.vue'
import { BubbleAvatar } from '@/components/AIavatar.ts'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import PlainTextRenderer from '@/components/chat/PlainTextRenderer.vue'
import HtmlRenderer from '@/components/common/HtmlRenderer.vue'
import Dialog from '@/components/common/Dialog.vue'
import SelectionActionButton from '@/components/chat/SelectionActionButton.vue'
import NoteDrawer from '@/components/notes/NoteDrawer.vue'
import WebSearchIndicator from '@/components/chat/WebSearchIndicator.vue'
import { API_BASE_URL } from '@/api/config'

const route = useRoute()
const chatStore = useChatStore()
const modelsStore = useModelsStore()
const notificationStore = useNotificationStore()
const authStore = useAuthStore()
const { t } = useLocalization()

// 计算用户头像URL
const userAvatarUrl = computed(() => {
  if (authStore.user?.avatar) {
    // 检查是否是完整URL或相对路径
    if (authStore.user.avatar.startsWith('http')) {
      return authStore.user.avatar
    } else if (authStore.user.avatar.startsWith('/static/')) {
      // 直接使用API_BASE_URL，不需要再添加/api
      return `${API_BASE_URL}${authStore.user.avatar}`
    } else {
      // 添加API基础URL
      return `${API_BASE_URL}${authStore.user.avatar}`
    }
  }
  
  // 直接使用本地静态资源，这样在Electron和Web环境都能正常工作
  return new URL('../assets/default-avatar.jpg', import.meta.url).href
})

// 使用 storeToRefs 获取响应式状态
const { messages, isGenerating, currentModel } = storeToRefs(chatStore)

const chatContainer = ref(null)
const showScrollButton = ref(false)
const autoScroll = ref(true)
const showConfirmDialog = ref(false)
const showRefreshConfirmDialog = ref(false)
const refreshConfirmed = ref(false)

// 笔记抽屉状态
const isNoteDrawerOpen = ref(false)
const selectedTextForNote = ref('')
const noteDrawerRef = ref(null)

// 图片预览相关
const showImagePreview = ref(false)
const previewImageUrl = ref('')

// 网页搜索指示器引用
const webSearchIndicatorRef = ref(null)

// 处理发送消息
async function handleSendMessage(message) {
  if (chatStore.isGenerating) return

  const messageData = {
    role: 'user',
    content: message.content,
    timestamp: new Date().toISOString(),
  }

  // 添加图片数据（如果有）
  if (message.image) {
    messageData.image = message.image
  }
  if (message.image_path) {
    messageData.image_path = message.image_path
  }

  // 添加文档数据（如果有）
  if (message.document) {
    messageData.document = message.document
    messageData.showDocument = false  // 初始状态为收起
  }

  // 添加网页搜索标志（如果有）
  if (message.web_search !== undefined) {
    messageData.web_search = message.web_search
  }

  await chatStore.sendMessage(messageData)
}

// 添加用户滚动跟踪
const shouldAutoScroll = ref(true);
const lastUserScrollPosition = ref(0);
const isNearBottom = ref(true);

// 监听滚动事件
onMounted(() => {
  const container = chatContainer.value;
  if (!container) return;

  // 初始滚动到底部
  scrollToBottom(true, false);
  
  // 加载当前对话
  loadCurrentConversation();
  
  const handleScroll = () => {
    const container = chatContainer.value;
    if (!container) return;
    
    // 记录当前滚动位置
    lastUserScrollPosition.value = container.scrollTop;
    
    // 计算距离底部的距离
    const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    
    // 如果距离底部很近（例如小于50像素），则认为用户想要查看最新消息
    const nearBottom = distanceToBottom < 50;
    
    // 更新自动滚动状态
    shouldAutoScroll.value = nearBottom;
    
    // 更新是否接近底部的状态（用于显示/隐藏"滚动到底部"按钮）
    isNearBottom.value = nearBottom;
  };
  
  container.addEventListener('scroll', handleScroll, { passive: true });
});

// 滚动防抖变量
let scrollDebounceTimer = null;
let isScrolling = false;

// 自动滚动到底部
const scrollToBottom = (force = false, smooth = true) => {
  // 如果正在滚动，则取消之前的滚动请求
  if (scrollDebounceTimer) {
    clearTimeout(scrollDebounceTimer);
  }
  
  // 如果正在滚动，则不执行新的滚动
  if (isScrolling && !force) return;
  
  // 使用防抖处理，减少短时间内的多次滚动
  scrollDebounceTimer = setTimeout(() => {
    const container = chatContainer.value;
    if (!container) return;
    
    // 强制滚动或根据用户滚动状态决定
    if (force || shouldAutoScroll.value) {
      // 标记正在滚动
      isScrolling = true;
      
      // 设置滚动行为
      container.style.scrollBehavior = smooth ? 'smooth' : 'auto';
      
      // 滚动到底部
      container.scrollTop = container.scrollHeight;
      
      // 滚动完成后，如果是强制滚动，则重新启用自动滚动
      if (force) {
        shouldAutoScroll.value = true;
      }
      
      // 滚动结束后重置标记
      setTimeout(() => {
        isScrolling = false;
      }, smooth ? 300 : 50); // 平滑滚动需要更长的时间
    }
  }, 20); // 短延迟，防抖处理
};

// 记录最后一条AI消息的行数
let lastAssistantMessageLineCount = 0;

// 监听消息变化
watch(() => chatStore.messages, (newMessages, oldMessages) => {
  // 如果是新增消息，直接滚动到底部
  if (!oldMessages || newMessages.length > oldMessages.length) {
    scrollToBottom(true, true);
    // 重置行数计数
    lastAssistantMessageLineCount = 0;
    return;
  }
  
  // 检查最后一条消息是否是AI消息且内容变化
  if (newMessages.length > 0 && oldMessages.length > 0 && 
      newMessages[newMessages.length - 1].role === 'assistant' &&
      newMessages[newMessages.length - 1].content !== oldMessages[oldMessages.length - 1].content) {
    
    // 获取当前消息内容和行数
    const currentContent = newMessages[newMessages.length - 1].content || '';
    const currentLineCount = (currentContent.match(/\n/g) || []).length + 1;
    
    // 如果行数增加了4行或更多，且用户允许自动滚动，则滚动到底部
    if (currentLineCount - lastAssistantMessageLineCount >= 4 && shouldAutoScroll.value) {
      scrollToBottom(false, true);
      lastAssistantMessageLineCount = currentLineCount;
    }
  }
}, { deep: true });

// 加载当前对话
const loadCurrentConversation = async () => {
  const conversationId = route.params.conversationId
  if (conversationId) {
    await chatStore.loadConversation(conversationId)
  }
}

// 处理确认清空对话
function handleConfirmClear() {
  chatStore.clearChat()
    .then(() => {
      notificationStore.success(t('chat.notifications.clear_success'))
    })
    .catch((error) => {
      notificationStore.error(t('chat.notifications.clear_error') + error.message)
    })
    .finally(() => {
      showConfirmDialog.value = false
    })
}

// 处理确认刷新
function handleConfirmRefresh() {
  // 用户确认刷新，设置标志并执行刷新操作
  refreshConfirmed.value = true
  
  // 使用 location.reload() 刷新页面
  window.location.reload()
}

// 处理刷新确认对话框更新
function handleRefreshDialogUpdate(val) {
  if (!val) {
    refreshConfirmed.value = false
  }
}

// 复制消息内容
const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content);
    notificationStore.success('复制成功')
  } catch (err) {
    notificationStore.error('复制失败：' + err.message)
  }
};

// 删除消息
const deleteMessage = (message) => {
  const index = chatStore.messages.indexOf(message);
  if (index > -1) {
    chatStore.messages.splice(index, 1);
    notificationStore.success('消息删除成功')
  }
};

// 格式化时间，只显示时:分
const formatTime = (timestamp) => {
  if (!timestamp) return '';
  // 确保时间字符串包含时区信息
  const date = new Date(timestamp);  // timestamp 已经是 ISO 格式，包含时区信息
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false,
    timeZone: 'Asia/Shanghai'  // 明确指定时区
  });
};

// 监听路由参数变化，重新加载对话
watch(
  () => route.params.conversationId,
  (newId, oldId) => {
    // 如果是新的对话ID，先清空消息列表，避免显示旧的对话内容
    if (newId !== oldId) {
      chatStore.messages = []
    }
    // 然后加载新对话
    loadCurrentConversation()
  },
  { immediate: true }
)

onMounted(() => {
  loadCurrentConversation()
  modelsStore.fetchChatModels()
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('beforeunload', handleBeforeUnload)
  
  // 监听模型状态变化
  watch(() => chatStore.aiStatus.model, (newValue, oldValue) => {
    console.log(`[ChatPage] 模型状态变化: ${oldValue} -> ${newValue}`);
  });
})

// 监听模型变化
watch(() => chatStore.currentModel, (newModel) => {
  if (newModel) {
    modelsStore.setLastUsedChatModel(newModel)
  }
})

// 组件卸载时移除事件监听器
onUnmounted(() => {
  const container = chatContainer.value;
  if (container) {
    container.removeEventListener('scroll', handleScroll);
  }
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('beforeunload', handleBeforeUnload)
});

// 替换isActiveThinking方法，删除重复逻辑
const isActiveThinking = (message) => {
  if (!message.content) return false;
  
  // 检查是否包含未闭合的<think>标签
  const hasOpenThink = message.content.includes('<think>');
  const hasCloseThink = message.content.includes('</think>');
  
  if (hasOpenThink && !hasCloseThink && chatStore.aiStatus.thinking === 'thinking') {
    // 确保已开始思考计时
    if (!message.currentThinkStartTime) {
      chatStore.startMessageThinking(message);
    }
    return true;
  }
  
  // 思考结束时
  if (hasOpenThink && hasCloseThink && message.currentThinkStartTime && !message.currentThinkEndTime) {
    chatStore.endMessageThinking(message);
  }
  
  return false;
};

// 计算思考时间 - 使用store方法
const getThinkingTime = (message) => {
  return chatStore.getThinkingTime(message);
};

// 删除这两个重复的localStorage操作方法，改为使用以下更简单的方法
const toggleThinkingProcess = (message) => {
  message.showThinking = !message.showThinking;
};

// 处理 base64 图片
function formatBase64Image(base64String) {
  if (!base64String) return '';
  
  // 如果已经包含前缀，直接返回
  if (base64String.startsWith('data:image/')) {
    return base64String;
  }
  
  // 检测图片类型
  // 解码 base64 字符串的前几个字节来判断图片类型
  try {
    const prefix = atob(base64String.substring(0, 8));
    let imageType = 'image/jpeg'; // 默认为 JPEG
    
    // 检查文件签名
    if (prefix.charCodeAt(0) === 0x89 && prefix.charCodeAt(1) === 0x50) {
      // PNG 文件以 89 50 4E 47 开头
      imageType = 'image/png';
    } else if (prefix.charCodeAt(0) === 0xFF && prefix.charCodeAt(1) === 0xD8) {
      // JPEG 文件以 FF D8 开头
      imageType = 'image/jpeg';
    }
    
    return `data:${imageType};base64,${base64String}`;
  } catch (e) {
    console.warn('Error detecting image type:', e);
    // 如果检测失败，默认使用 JPEG
    return `data:image/jpeg;base64,${base64String}`;
  }
}

// 获取消息图片源
function getMessageImageSrc(message) {
  if (message.image_path) {
    return `/${message.image_path}`;
  }
  
  if (message.image) {
    return message.image.startsWith('data:image/') ? message.image : formatBase64Image(message.image);
  }
  
  if (message.images) {
    try {
      // 如果 images 是字符串，尝试解析为 JSON
      if (typeof message.images === 'string') {
        const parsedImages = JSON.parse(message.images);
        if (Array.isArray(parsedImages) && parsedImages.length > 0) {
          return formatBase64Image(parsedImages[0]);
        }
        return formatBase64Image(message.images);
      }
      
      // 如果 images 是数组
      if (Array.isArray(message.images) && message.images.length > 0) {
        return formatBase64Image(message.images[0]);
      }
    } catch (e) {
      console.warn('Error parsing images data:', e);
      return formatBase64Image(message.images);
    }
  }
  
  return '';
}

// 切换显示/隐藏文档内容
const toggleDocumentContent = (message) => {
  message.showDocument = !message.showDocument
}

// 获取文件类型
const getFileType = (mimeType) => {
  const types = {
    'application/pdf': t('chat.file_preview.file_types.pdf'),
    'application/msword': t('chat.file_preview.file_types.word'),
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': t('chat.file_preview.file_types.word'),
    'text/plain': t('chat.file_preview.file_types.text'),
    'text/html': t('chat.file_preview.file_types.html'),
    'text/markdown': t('chat.file_preview.file_types.markdown')
  }
  return types[mimeType] || t('chat.file_preview.file_types.document')
}

// 获取文档类型对应的CSS类名
function getDocumentTypeClass(mimeType) {
  if (!mimeType) return '';
  
  if (mimeType.includes('pdf')) {
    return 'pdf-icon';
  } else if (mimeType.includes('word') || mimeType.includes('doc')) {
    return 'word-icon';
  } else if (mimeType.includes('excel') || mimeType.includes('sheet') || mimeType.includes('xls') || mimeType.includes('csv')) {
    return 'excel-icon';
  } else if (mimeType.includes('powerpoint') || mimeType.includes('presentation') || mimeType.includes('ppt')) {
    return 'ppt-icon';
  } else if (mimeType.includes('text') || mimeType.includes('txt')) {
    return 'txt-icon';
  }
  
  return '';
}

// 处理键盘事件
function handleKeyDown(event) {
  // 如果正在生成内容，捕获 F5 或 Ctrl+R
  if (isGenerating.value && (event.key === 'F5' || (event.ctrlKey && event.key === 'r'))) {
    // 显示自定义确认对话框
    showRefreshConfirmDialog.value = true
    
    // 阻止默认刷新行为
    event.preventDefault()
  }
}

// 处理页面刷新前的事件
function handleBeforeUnload(event) {
  // 如果用户已经通过我们的对话框确认了刷新，则不阻止
  if (refreshConfirmed.value) {
    return;
  }
  
  // 如果正在生成内容，显示自定义确认对话框
  if (isGenerating.value) {
    // 返回空字符串会在一些浏览器中显示默认对话框，但这是必要的
    // 因为我们需要阻止刷新直到用户通过我们的对话框确认
    return '';
  }
}

// 判断是否是最后一条消息
function isLastMessage(message) {
  if (!chatStore.messages || chatStore.messages.length === 0) {
    return false;
  }
  
  const lastMessage = chatStore.messages[chatStore.messages.length - 1];
  return message.id === lastMessage.id;
}

// 判断是否是最后一条AI消息
function isLastAssistantMessage(message) {
  if (!chatStore.messages || chatStore.messages.length === 0 || message.role !== 'assistant') {
    return false;
  }
  
  // 从后向前遍历消息，找到第一条AI消息
  for (let i = chatStore.messages.length - 1; i >= 0; i--) {
    if (chatStore.messages[i].role === 'assistant') {
      return message.id === chatStore.messages[i].id;
    }
  }
  
  return false;
}



// 处理保存到笔记
function handleSaveToNote(text) {
  if (!text.trim()) return
  
  // 如果笔记抽屉已经打开，则追加内容
  if (isNoteDrawerOpen.value && noteDrawerRef.value) {
    // 使用appendContent方法追加内容
    noteDrawerRef.value.appendContent(text)
  } else {
    // 如果笔记抽屉未打开，则设置初始内容并打开抽屉
    selectedTextForNote.value = text
    isNoteDrawerOpen.value = true
  }
}

// 笔记保存成功回调
function handleNoteSaved() {
  selectedTextForNote.value = ''
  isNoteDrawerOpen.value = false
}

// 打开图片预览
const openImagePreview = (imageSrc) => {
  previewImageUrl.value = imageSrc;
  showImagePreview.value = true;
  // 防止滚动
  document.body.style.overflow = 'hidden';
};

// 关闭图片预览
const closeImagePreview = () => {
  showImagePreview.value = false;
  // 恢复滚动
  document.body.style.overflow = '';
};

// 获取工具状态文本
const getToolStatusText = (toolStatus) => {
  if (toolStatus === ToolStatus.WEB_SEARCH) return t('chat.tool_status.web_search')
  return ''
}

// 内容渲染完成计数器
let contentRenderedCount = 0;
let contentRenderedTimer = null;

// 处理 Markdown 内容渲染完成事件
const handleContentRendered = () => {
  // 增加计数器
  contentRenderedCount++;
  
  // 清除之前的定时器
  if (contentRenderedTimer) {
    clearTimeout(contentRenderedTimer);
  }
  
  // 使用定时器收集短时间内的多次渲染完成事件，只滚动一次
  contentRenderedTimer = setTimeout(() => {
    // 重置计数器
    contentRenderedCount = 0;
    // 只有当shouldAutoScroll为true时才滚动到底部
    if (shouldAutoScroll.value) {
      scrollToBottom(false, true);
    }
  }, 3);
};
</script>

<style scoped>
@import '@/styles/ChatPage.css';
</style>

