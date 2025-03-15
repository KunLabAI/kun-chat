<template>
  <MainLayout>
    <div ref="chatContainer" class="chat-container">
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
                alt="Message image"
              />
            </div>
            <!-- 显示文档 -->
              <div v-if="message.document" class="message-file-preview">
                <div class="file-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                  </svg>
                </div>
                <div class="file-info">
                  <span class="file-name">{{ message.document.name }}</span>
                  <span class="file-type">{{ getFileType(message.document.type) }}</span>
                </div>
                <button class="file-preview-btn" @click="toggleDocumentContent(message)">
                  {{ message.showDocument ? t('chat.file_preview.hide_content') : t('chat.file_preview.show_content') }}
                </button>
              </div>
            <div v-if="message.document && message.showDocument" class="document-content">
              <MarkdownRenderer :content="message.document.content" />
            </div>
            <!-- 显示文本内容 -->
            <template v-if="message.content">
              <!-- 思考过程 -->
              <div 
                v-if="message.role === 'assistant' && hasThinkingContent(message.content)" 
                class="thinking-process"
                :class="{ 'thinking-process-active': isActiveThinking(message) }"
              >
                <div class="thinking-process-header">
                  <span class="thinking-title">
                    {{ isActiveThinking(message) ? t('chat.thinking_process.title') : t('chat.thinking_process.title') }}
                    <span class="thinking-time">
                      {{ t('chat.thinking_process.time', [getThinkingTime(message)]) }}
                    </span>
                  </span>
                  <span v-if="isActiveThinking(message)" class="thinking-dots"></span>
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
                <PlainTextRenderer v-if="message.role === 'user'" :content="message.content" />
                <!-- AI消息使用Markdown渲染器 -->
                <MarkdownRenderer v-else :content="extractFinalContent(message.content) || message.content" />
              </div>
            </template>
            <div 
              v-if="chatStore.isGenerating && message === chatStore.messages[chatStore.messages.length - 1] && message.role === 'assistant'"
              class="loading-container"
            >
              <div class="spinner">
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
              </div>
            </div>
            <div v-if="message.role === 'assistant'" class="message-footer">
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
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
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import { useModelsStore } from '@/stores/models'
import { useNotificationStore } from '@/stores/notification'
import { useAuthStore } from '@/stores/auth'
import { useLocalization } from '@/i18n'
import MainLayout from '@/layouts/MainLayout.vue'
import ChatInput from '@/components/chat/InputArea/ChatInput.vue'
import { BubbleAvatar } from '@/components/AIavatar.ts'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import PlainTextRenderer from '@/components/common/PlainTextRenderer.vue'
import Dialog from '@/components/common/Dialog.vue'
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
  return `${API_BASE_URL}/static/default-avatar.jpg`
})

// 使用 storeToRefs 获取响应式状态
const { messages, isGenerating, currentModel } = storeToRefs(chatStore)

const chatContainer = ref(null)
const showScrollButton = ref(false)
const autoScroll = ref(true)
const showConfirmDialog = ref(false)
const showRefreshConfirmDialog = ref(false)
const refreshConfirmed = ref(false)

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
  loadCurrentConversation().then(() => {
    // 加载所有消息的思考时间数据
    if (chatStore.messages && chatStore.messages.length > 0) {
      chatStore.messages.forEach(message => {
        if (message.role === 'assistant') {
          loadThinkingTimesFromLocalStorage(message);
        }
      });
    }
  });
  
  const handleScroll = () => {
    const { scrollTop, scrollHeight, clientHeight } = container;
    const currentScroll = scrollTop + clientHeight;
    isNearBottom.value = scrollHeight - currentScroll < 100;
    
    // 检测滚动方向
    const isScrollingUp = scrollTop < lastUserScrollPosition.value;
    lastUserScrollPosition.value = scrollTop;
    
    // 只有在接近底部时才启用自动滚动
    if (isScrollingUp) {
      shouldAutoScroll.value = false;
    } else if (isNearBottom.value) {
      shouldAutoScroll.value = true;
    }
  };
  
  container.addEventListener('scroll', handleScroll, { passive: true });
});

// 自动滚动到底部
const scrollToBottom = (force = false, smooth = true) => {
  nextTick(() => {
    const container = chatContainer.value;
    if (!container) return;
    
    if (force || shouldAutoScroll.value) {
      container.scrollTop = container.scrollHeight;
    }
  });
};

// 监听消息变化
watch(() => chatStore.messages, (newMessages) => {
  nextTick(() => {
    scrollToBottom();
    
    // 保存所有AI消息的思考时间数据
    if (newMessages && newMessages.length > 0) {
      newMessages.forEach(message => {
        if (message.role === 'assistant') {
          saveThinkingTimesToLocalStorage(message);
        }
      });
    }
  });
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

// 检查是否有思考内容
const hasThinkingContent = (content) => {
  if (!content) return false;
  // 如果正在生成中且包含未闭合的think标签，显示思考过程
  if (content.includes('<think>') && !content.includes('</think>')) {
    return true;
  }
  // 如果思考过程已完成，检查内容是否为空
  const thinkMatch = content.match(/<think>([\s\S]*?)<\/think>/);
  return thinkMatch && thinkMatch[1].trim().length > 0;
};

// 提取思考过程内容
const extractThinkContent = (content) => {
  if (!content) return '';
  const match = content.match(/<think>([\s\S]*?)(?:<\/think>|$)/);
  return match ? match[1].trim() : '';
};

// 提取最终回答内容
const extractFinalContent = (content) => {
  if (!content) return content;
  // 如果没有结束标签，说明还在思考中，不显示最终内容
  if (content.includes('<think>') && !content.includes('</think>')) {
    return '';
  }
  return content.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
};

// 检查是否正在思考中
const isActiveThinking = (message) => {
  if (!message.content) return false;
  
  // 检查是否包含未闭合的<think>标签
  const hasOpenThink = message.content.includes('<think>');
  const hasCloseThink = message.content.includes('</think>');
  
  if (hasOpenThink && !hasCloseThink && chatStore.isGenerating) {
    // 如果是新的思考过程，记录开始时间
    if (!message.currentThinkStartTime) {
      message.currentThinkStartTime = Date.now();
      // 保存到消息的元数据中
      message.metadata = message.metadata || {};
      message.metadata.thinkTimes = message.metadata.thinkTimes || [];
      message.metadata.thinkTimes.push({
        startTime: message.currentThinkStartTime
      });
      
      // 保存更新后的消息到store
      chatStore.updateMessage(message);
      
      // 保存思考时间到localStorage
      saveThinkingTimesToLocalStorage(message);
    }
    return true;
  }
  
  // 当思考结束时（检测到</think>标签），记录结束时间
  if (hasOpenThink && hasCloseThink && message.currentThinkStartTime && !message.currentThinkEndTime) {
    message.currentThinkEndTime = Date.now();
    // 更新消息元数据中的思考时间
    if (message.metadata?.thinkTimes?.length > 0) {
      const currentThink = message.metadata.thinkTimes[message.metadata.thinkTimes.length - 1];
      if (!currentThink.endTime) {
        currentThink.endTime = message.currentThinkEndTime;
        currentThink.duration = message.currentThinkEndTime - currentThink.startTime;
        // 保存更新后的消息到store
        chatStore.updateMessage(message);
        
        // 保存思考时间到localStorage
        saveThinkingTimesToLocalStorage(message);
      }
    }
    // 重置当前思考时间，为下一次思考做准备
    message.currentThinkStartTime = null;
    message.currentThinkEndTime = null;
  }
  
  return false;
};

// 计算思考时间
const getThinkingTime = (message) => {
  if (!message.content) return '';
  
  // 尝试从localStorage加载思考时间
  loadThinkingTimesFromLocalStorage(message);
  
  // 如果正在思考中
  if (isActiveThinking(message)) {
    const currentTime = Date.now();
    const currentThinkTime = Math.floor((currentTime - message.currentThinkStartTime) / 1000);
    // 计算历史思考时间总和
    const historicalTime = message.metadata?.thinkTimes?.reduce((total, think) => {
      if (think.endTime) {
        return total + Math.floor((think.endTime - think.startTime) / 1000);
      }
      return total;
    }, 0) || 0;
    return `${historicalTime + currentThinkTime}秒`;
  } 
  // 如果思考已结束
  else if (message.metadata?.thinkTimes?.length > 0) {
    // 计算所有思考时间的总和
    const totalTime = message.metadata.thinkTimes.reduce((total, think) => {
      if (think.endTime) {
        return total + Math.floor((think.endTime - think.startTime) / 1000);
      }
      return total;
    }, 0);
    return `${totalTime}秒`;
  }
  
  return '';
};

// 保存思考时间到localStorage
const saveThinkingTimesToLocalStorage = (message) => {
  try {
    if (!message.metadata?.thinkTimes) return;
    
    // 获取当前对话ID
    const conversationId = route.params.conversationId?.toString();
    if (!conversationId) return;
    
    // 使用消息内容的前100个字符作为标识符
    const contentIdentifier = message.content ? message.content.substring(0, 100) : '';
    
    // 构建存储键
    const storageKey = `thinkTimes_${conversationId}_${contentIdentifier}`;
    
    // 保存思考时间数据
    localStorage.setItem(storageKey, JSON.stringify(message.metadata.thinkTimes));
    console.log('已保存思考时间数据:', storageKey);
  } catch (error) {
    console.error('保存思考时间到localStorage失败:', error);
  }
};

// 从localStorage加载思考时间
const loadThinkingTimesFromLocalStorage = (message) => {
  try {
    // 获取当前对话ID
    const conversationId = route.params.conversationId?.toString();
    if (!conversationId) return;
    
    // 使用消息内容的前100个字符作为标识符
    const contentIdentifier = message.content ? message.content.substring(0, 100) : '';
    
    // 构建存储键
    const storageKey = `thinkTimes_${conversationId}_${contentIdentifier}`;
    
    // 从localStorage获取数据
    const storedData = localStorage.getItem(storageKey);
    if (!storedData) return;
    
    console.log('已加载思考时间数据:', storageKey);
    
    // 解析数据并更新消息
    const thinkTimes = JSON.parse(storedData);
    if (Array.isArray(thinkTimes) && thinkTimes.length > 0) {
      // 只有当消息没有思考时间数据或数据不完整时才更新
      if (!message.metadata) {
        message.metadata = {};
      }
      if (!message.metadata.thinkTimes || message.metadata.thinkTimes.length < thinkTimes.length) {
        message.metadata.thinkTimes = thinkTimes;
      }
    }
  } catch (error) {
    console.error('从localStorage加载思考时间失败:', error);
  }
};

// 格式化思考内容，处理换行和缩进
const formatThinkContent = (content) => {
  return content
    .split('\n')
    .map(line => line.trim())
    .filter(line => line)
    .join('\n');
};

// 切换显示/隐藏思考过程
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
</script>

<style scoped>
@import '@/styles/ChatPage.css';

</style>
