import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Message, SendMessagePayload, ChatMessage, ProcessedChatMessage } from '@/types/index'
import { chatApi } from '@/api/chat'
import { v4 as uuidv4 } from 'uuid'
import { API_BASE_URL } from '@/api/config'
import { useNotificationStore } from '@/stores/notification'
import { t } from '@/i18n'

// 动态获取WebSocket基础URL
const getWsBaseUrl = () => {
  const apiUrl = API_BASE_URL
  return apiUrl.replace('http://', 'ws://').replace('https://', 'wss://').replace('/api', '')
}

// 从环境变量或动态获取WebSocket配置
const WS_BASE_URL = getWsBaseUrl()

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const currentModel = ref<string | null>(localStorage.getItem('selectedModel'))
  const currentConversationId = ref<string>('')
  const isGenerating = ref<boolean>(false)
  const error = ref<string | null>(null)
  const currentWebSocket = ref<WebSocket | null>(null)
  const abortController = ref<AbortController | null>(null)

  async function sendMessage(payload: SendMessagePayload): Promise<void> {
    if (!payload.content.trim() || !currentModel.value || isGenerating.value || !currentConversationId.value) {
      console.error('Invalid message payload:', {
        content: !!payload.content.trim(),
        model: !!currentModel.value,
        isGenerating: isGenerating.value,
        conversationId: !!currentConversationId.value
      });
      error.value = '无效的消息内容或配置';
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: payload.content.trim(),
      timestamp: new Date().toISOString(),
      model: currentModel.value,
      image: payload.image,
      images: payload.image ? [payload.image] : undefined,
      document: payload.document,
      showDocument: false
    }
    messages.value.push(userMessage)

    // Add empty assistant message that will be updated
    const assistantMessageIndex = messages.value.length
    const assistantMessage: Message = {
      id: uuidv4(),
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      model: currentModel.value,
      images: undefined,
      document: undefined,
      showDocument: false
    }
    messages.value.push(assistantMessage)

    isGenerating.value = true
    error.value = null

    let ws: WebSocket | null = null;
    try {
      console.log('Connecting to WebSocket...');
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No authentication token found');
        error.value = '未找到认证token';
        isGenerating.value = false;
        return;
      }

      const wsUrl = `${WS_BASE_URL}/api/chat/conversations/${currentConversationId.value}/ws?token=${token}`;
      console.log('WebSocket URL:', wsUrl);
      ws = new WebSocket(wsUrl);
      currentWebSocket.value = ws;
      
      // 创建新的 AbortController
      abortController.value = new AbortController();
      
      // 添加连接超时处理和重试机制
      let retryCount = 0;
      const maxRetries = 3;
      const connectionTimeout = setTimeout(() => {
        if (ws && ws.readyState !== WebSocket.OPEN) {
          console.error('WebSocket connection timeout');
          
          // 尝试重连
          if (retryCount < maxRetries) {
            retryCount++;
            console.log(`重试连接 (${retryCount}/${maxRetries})...`);
            // 关闭当前连接并重新连接
            ws.close();
            // 使用递减的超时时间进行重试
            setTimeout(() => {
              const notificationStore = useNotificationStore();
              notificationStore.show({
                type: 'INFO',
                message: t('chat.errors.retry_connecting', { count: retryCount, max: maxRetries })
              });
              // 重新连接 (这里会递归调用sendMessage)
              sendMessage(payload);
            }, 1000 * retryCount);
          } else {
            error.value = t('chat.errors.connection_timeout');
            isGenerating.value = false;
            const notificationStore = useNotificationStore();
            notificationStore.show({
              type: 'ERROR',
              message: t('chat.errors.server_connection_failed')
            });
            ws.close();
          }
        }
      }, 5000);

      ws.onopen = () => {
        if (!ws) return;
        console.log('WebSocket connected');
        clearTimeout(connectionTimeout);

        try {
          // 发送用户消息
          const messageToSend = {
            type: "chat",
            messages: [{
              role: 'user',
              content: userMessage.content,
              image: userMessage.image ? userMessage.image.split(',')[1] : undefined, // 只发送base64数据部分
              document: userMessage.document
            }],
            model: currentModel.value,
            web_search: payload.web_search || false
          };
          
          console.log('Sending message:', {
            ...messageToSend,
            messages: [{
              ...messageToSend.messages[0],
              image: messageToSend.messages[0].image ? '(base64 image data)' : undefined,
              document: messageToSend.messages[0].document ? '(document data)' : undefined
            }]
          });
          ws.send(JSON.stringify(messageToSend));
        } catch (error) {
          console.error('Error sending message:', error);
          throw error;
        }
      };

      // 处理消息响应
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.error) {
            error.value = data.error;
            isGenerating.value = false;
            ws?.close();
            return;
          }

          if (data.message) {
            // 更新最新的消息内容
            const currentContent = messages.value[assistantMessageIndex].content;
            messages.value[assistantMessageIndex].content = currentContent + (data.message.content || '');

            // 如果是最后一条消息，关闭连接
            if (data.done) {
              isGenerating.value = false;
              ws?.close();
            }
          }
        } catch (error) {
          console.error('Error processing message:', error);
        }
      };

      // 处理错误
      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        error.value = t('chat.errors.connection_error');
        isGenerating.value = false;
        
        // 显示错误通知
        const notificationStore = useNotificationStore();
        notificationStore.show({
          type: 'ERROR',
          message: t('chat.errors.connection_error')
        });
      };

      // 处理连接关闭
      ws.onclose = (event) => {
        console.log('WebSocket connection closed', event);
        currentWebSocket.value = null;
        
        // 如果还在生成中但连接关闭了，说明可能是异常关闭
        if (isGenerating.value) {
          isGenerating.value = false;
          
          // 如果是异常关闭且没有错误消息，显示通用错误
          if (event.code !== 1000 && !error.value) {
            error.value = t('chat.errors.connection_closed');
            // 显示错误通知
            const notificationStore = useNotificationStore();
            notificationStore.show({
              type: 'WARNING',
              message: t('chat.errors.connection_closed')
            });
          }
        }
      };

    } catch (error) {
      console.error('Error in sendMessage:', error);
      isGenerating.value = false;
      throw error;
    }
  }

  function setCurrentConversation(conversationId: string) {
    currentConversationId.value = conversationId
  }

  async function clearChat() {
    if (!currentConversationId.value) {
      error.value = '无效的对话ID'
      return
    }
    try {
      // 如果当前有正在生成的消息，先停止生成
      if (isGenerating.value) {
        await stopGenerating()
      }
      
      await chatApi.clearConversation(currentConversationId.value)
      messages.value = []
      error.value = null
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : '清空对话失败'
      error.value = errorMessage
      console.error('Failed to clear chat:', e)
      throw e // 向上传播错误以便UI层处理
    }
  }

  async function loadConversation(conversationId: string): Promise<void> {
    try {
      // 如果当前有正在生成的消息，先停止生成
      if (isGenerating.value) {
        await stopGenerating()
      }
      
      // 先清空消息列表，避免显示旧的对话内容
      messages.value = []
      
      const conversation = await chatApi.getConversation(conversationId)
      if (conversation) {
        // 确保所有消息的时间戳都是 ISO 格式
        messages.value = (conversation.messages || []).map(msg => ({
          ...msg,
          timestamp: msg.timestamp.endsWith('Z') ? msg.timestamp : msg.timestamp + 'Z'
        }))
        if (conversation.model) {
          currentModel.value = conversation.model
          localStorage.setItem('selectedModel', conversation.model)
        }
        currentConversationId.value = conversationId
      } else {
        error.value = '对话不存在'
      }
    } catch (err) {
      console.error('Error loading conversation:', err)
      error.value = '加载对话失败'
    }
  }

  async function setCurrentModel(model: string, conversationId?: string, updateBackend: boolean = false): Promise<void> {
    // 如果当前有正在生成的消息，先停止生成
    if (isGenerating.value) {
      await stopGenerating()
    }
    
    currentModel.value = model
    localStorage.setItem('selectedModel', model)
    
    // 如果需要更新后端，且有对话ID，则调用API更新
    if (updateBackend && conversationId) {
      try {
        await chatApi.updateConversationModel(conversationId, model)
      } catch (err) {
        console.error('Error updating conversation model:', err)
        throw err
      }
    }
  }

  // 更新指定消息
  function updateMessage(message: Message): void {
    const index = messages.value.findIndex(m => m.id === message.id)
    if (index !== -1) {
      messages.value[index] = { ...message }
    }
  }

  // 停止生成
  async function stopGenerating(): Promise<void> {
    let apiRequestSuccessful = false;
    
    try {
      // 1. 发送中止请求到后端
      if (currentConversationId.value) {
        const token = localStorage.getItem('token')
        if (!token) {
          console.warn('未找到认证token，跳过API请求')
        } else {
          try {
            const response = await fetch(`${API_BASE_URL}/chat/conversations/${currentConversationId.value}/abort`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            
            if (response.ok) {
              apiRequestSuccessful = true;
              await response.json();
            } else {
              console.warn(`API请求失败，状态码: ${response.status}，继续关闭WebSocket`);
            }
          } catch (apiError) {
            console.warn('发送停止请求失败，继续关闭WebSocket:', apiError);
          }
        }
      }

      // 2. 关闭当前的 WebSocket 连接
      if (currentWebSocket.value && currentWebSocket.value.readyState === WebSocket.OPEN) {
        currentWebSocket.value.close()
        currentWebSocket.value = null
      }

      // 3. 中止当前的请求
      if (abortController.value) {
        abortController.value.abort()
        abortController.value = null
      }

      isGenerating.value = false
      
      // 显示成功通知
      const notificationStore = useNotificationStore()
      notificationStore.show({
        type: 'SUCCESS',
        message: t('chat.notifications.abort_success')
      })
    } catch (err) {
      console.error('停止生成失败:', err)
      error.value = '停止生成失败'
      
      // 显示错误通知
      const notificationStore = useNotificationStore()
      notificationStore.show({
        type: 'ERROR',
        message: t('chat.notifications.abort_error', { error: err instanceof Error ? err.message : String(err) })
      })
    } finally {
      // 确保状态被重置
      isGenerating.value = false
      currentWebSocket.value = null
      abortController.value = null
    }
  }

  return {
    messages,
    currentModel,
    currentConversationId,
    isGenerating,
    error,
    sendMessage,
    setCurrentConversation,
    clearChat,
    loadConversation,
    setCurrentModel,
    updateMessage,
    stopGenerating
  }
})