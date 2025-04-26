import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type { Message, SendMessagePayload, ChatMessage, ProcessedChatMessage } from '@/types/index'
import { chatApi } from '@/api/chat'
import { v4 as uuidv4 } from 'uuid'
import { API_BASE_URL } from '@/api/config'
import { useNotificationStore } from '@/stores/notification'
import { t } from '@/i18n'
import { 
  ModelStatus, 
  GenerationStatus, 
  ThinkingStatus, 
  ToolStatus, 
  AiStatusState, 
  DEFAULT_AI_STATUS, 
  getToolStatusText 
} from '@/states/aiStates'
import { 
  saveThinkingTimes,
  loadThinkingTimes,
  updateThinkingTime,
  getFormattedThinkingTime
} from '@/states/thinkingManager'

// 动态获取WebSocket基础URL
const getWsBaseUrl = () => {
  const apiUrl = API_BASE_URL
  return apiUrl.replace('http://', 'ws://').replace('https://', 'wss://').replace('/api', '')
}

// 从环境变量或动态获取WebSocket配置
const WS_BASE_URL = getWsBaseUrl()

export {
  ModelStatus,
  GenerationStatus,
  ThinkingStatus,
  ToolStatus
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const currentModel = ref<string | null>(localStorage.getItem('selectedModel'))
  const currentConversationId = ref<string>('')
  const isGenerating = ref<boolean>(false)
  const error = ref<string | null>(null)
  const currentWebSocket = ref<WebSocket | null>(null)
  const abortController = ref<AbortController | null>(null)
  
  // 使用统一的状态管理
  const aiStatus = reactive<AiStatusState>({...DEFAULT_AI_STATUS})

  // 函数: 更新状态
  function updateAiStatus(updates: Partial<AiStatusState>) {
    Object.assign(aiStatus, updates)
    
    // 同步isGenerating状态用于兼容现有代码
    if (updates.generation !== undefined) {
      isGenerating.value = updates.generation === GenerationStatus.CONNECTING ||
                           updates.generation === GenerationStatus.GENERATING
    }
  }
  
  // 函数: 重置状态
  function resetAiStatus() {
    updateAiStatus({...DEFAULT_AI_STATUS})
  }

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
    
    // 更新状态为连接中
    updateAiStatus({
      generation: GenerationStatus.CONNECTING,
      activeMessage: assistantMessage.id,
      websocketState: 'connecting'
    })
    
    isGenerating.value = true
    error.value = null

    let ws: WebSocket | null = null;
    try {
      console.log('Connecting to WebSocket...');
      
      // 使用新的存储方式获取token
      const lastLoggedUser = localStorage.getItem('kunlab_last_user')
      let token = null
      
      if (lastLoggedUser) {
        token = localStorage.getItem(`kunlab_user_token_${lastLoggedUser}`)
      } else {
        // 兼容旧版存储方式
        token = localStorage.getItem('token')
      }
      
      if (!token) {
        console.error('No authentication token found');
        error.value = '未找到认证token';
        isGenerating.value = false;
        updateAiStatus({
          generation: GenerationStatus.FAILED,
          failureReason: '未找到认证token',
          websocketState: 'error'
        });
        return;
      }

      // 确保移除Bearer前缀
      const cleanToken = token.startsWith('Bearer ') ? token.substring(7) : token;
      
      const wsUrl = `${WS_BASE_URL}/api/chat/conversations/${currentConversationId.value}/ws?token=${encodeURIComponent(cleanToken)}`;
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
              // 更新状态
              updateAiStatus({
                generation: GenerationStatus.CONNECTING,
                failureReason: `连接超时, 重试 ${retryCount}/${maxRetries}`
              });
              // 重新连接 (这里会递归调用sendMessage)
              sendMessage(payload);
            }, 1000 * retryCount);
          } else {
            error.value = t('chat.errors.connection_timeout');
            isGenerating.value = false;
            updateAiStatus({
              generation: GenerationStatus.FAILED,
              failureReason: '连接超时，请稍后重试',
              websocketState: 'error'
            });
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
        
        // 更新WebSocket状态
        updateAiStatus({
          websocketState: 'open',
          generation: GenerationStatus.GENERATING
        });

        try {
          // 检查是否是工具调用
          if (payload.web_search) {
            console.log('[ChatStore] 启动网页搜索工具');
            updateAiStatus({
              tool: ToolStatus.WEB_SEARCH,
              webSearchEnabled: true // 标记网页搜索已启用
            });
          } else {
            // 确保网页搜索状态被重置
            updateAiStatus({
              webSearchEnabled: false
            });
          }
          
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
          updateAiStatus({
            generation: GenerationStatus.FAILED,
            failureReason: '发送消息失败',
            websocketState: 'error'
          });
          throw error;
        }
      };

      // 处理消息响应
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("[ChatStore] 收到WebSocket消息:", data);
          
          if (data.error) {
            console.error("[ChatStore] 收到错误:", data.error);
            error.value = data.error;
            isGenerating.value = false;
            updateAiStatus({
              generation: GenerationStatus.FAILED,
              failureReason: data.error
            });
            ws?.close();
            return;
          }

          // 处理模型加载状态事件
          if (data.type === "model_loading") {
            console.log("[ChatStore] 收到模型加载状态:", data.status, "进度:", data.progress || 0);
            if (data.status === "loading") {
              // 更新为模型加载状态
              updateAiStatus({
                model: ModelStatus.LOADING,
                loadingProgress: data.progress || 0,
                generation: GenerationStatus.CONNECTING,
                failureReason: null
              });
            } else if (data.status === "ready") {
              // 更新为模型加载完成状态
              console.log("[ChatStore] 模型加载完成");
              updateAiStatus({
                model: ModelStatus.READY,
                loadingProgress: 100,
                generation: GenerationStatus.GENERATING,
                failureReason: null
              });
            } else if (data.status === "error") {
              // 更新为模型加载错误状态
              console.error("[ChatStore] 模型加载失败:", data.message);
              updateAiStatus({
                model: ModelStatus.ERROR,
                generation: GenerationStatus.FAILED,
                failureReason: data.message || "模型加载失败"
              });
              error.value = data.message || "模型加载失败";
              ws?.close();
            }
            return;
          }

          if (data.message) {
            // 使用更高效的方式更新消息内容
            const assistantMessage = messages.value[assistantMessageIndex];
            
            // 检测思考状态
            const newContent = (assistantMessage.content || '') + (data.message.content || '');
            const hasThinkTag = newContent.includes('<think>');
            const hasCloseThinkTag = newContent.includes('</think>');
            
            // 更新思考状态
            if (hasThinkTag && !hasCloseThinkTag) {
              updateAiStatus({
                thinking: ThinkingStatus.THINKING
              });
            } else if (hasThinkTag && hasCloseThinkTag && aiStatus.thinking === ThinkingStatus.THINKING) {
              updateAiStatus({
                thinking: ThinkingStatus.COMPLETED
              });
            }
            
            // 检测工具调用状态
            if (data.message.tool_call) {
              if (data.message.tool_call.type === 'web_search' && aiStatus.webSearchEnabled) {
                // 只有当网页搜索功能启用时才设置工具状态为 WEB_SEARCH
                updateAiStatus({
                  tool: ToolStatus.WEB_SEARCH
                });
              } else if (data.message.tool_call.type === 'mcp') {
                updateAiStatus({
                  tool: ToolStatus.MCP
                });
              } else {
                updateAiStatus({
                  tool: ToolStatus.CALLING
                });
              }
            }
            
            // 如果有工具调用结果
            if (data.message.tool_result) {
              console.log('[ChatStore] 工具调用完成:', data.message.tool_result.type);
              // 特别处理网页搜索结果
              if (data.message.tool_result.type === 'web_search' && aiStatus.webSearchEnabled) {
                console.log('[ChatStore] 网页搜索完成');
                updateAiStatus({
                  tool: ToolStatus.COMPLETED
                });
              } else {
                // 其他工具或网页搜索未启用时完成工具调用
                updateAiStatus({
                  tool: ToolStatus.COMPLETED
                });
              }
            }
            
            // 使用Object.assign更新内容，避免触发整个对象的响应式更新
            Object.assign(assistantMessage, { 
              ...assistantMessage,
              content: newContent 
            });
            
            // 更新思考时间
            if (currentConversationId.value) {
              updateThinkingTime(
                assistantMessage, 
                aiStatus.thinking === ThinkingStatus.THINKING, 
                currentConversationId.value
              );
            }
            
            // 如果是最后一条消息，关闭连接
            if (data.done) {
              isGenerating.value = false;
              console.log('[ChatStore] 消息生成完成，重置所有状态');
              updateAiStatus({
                generation: GenerationStatus.COMPLETED,
                thinking: ThinkingStatus.IDLE,
                tool: ToolStatus.IDLE,
                webSearchEnabled: false // 确保在消息生成完成后重置网页搜索状态
              });
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
        updateAiStatus({
          generation: GenerationStatus.FAILED,
          failureReason: '连接错误',
          websocketState: 'error',
          webSearchEnabled: false // 在连接错误时重置网页搜索状态
        });
        
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
        updateAiStatus({
          websocketState: 'closed',
          webSearchEnabled: false // 在连接关闭时重置网页搜索状态
        });
        
        // 如果还在生成中但连接关闭了，说明可能是异常关闭
        if (isGenerating.value) {
          isGenerating.value = false;
          updateAiStatus({
            generation: GenerationStatus.FAILED,
            failureReason: '连接意外关闭'
          });
          
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
        } else if (aiStatus.generation === GenerationStatus.GENERATING) {
          // 如果状态还是生成中，但isGenerating已经是false，更新状态为完成
          updateAiStatus({
            generation: GenerationStatus.COMPLETED,
            thinking: ThinkingStatus.IDLE,
            tool: ToolStatus.IDLE
          });
        }
      };

    } catch (error) {
      console.error('Error in sendMessage:', error);
      isGenerating.value = false;
      updateAiStatus({
        generation: GenerationStatus.FAILED,
        failureReason: error instanceof Error ? error.message : '未知错误',
        websocketState: 'error'
      });
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
      resetAiStatus()
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : '清空对话失败'
      error.value = errorMessage
      console.error('Failed to clear chat:', e)
      throw e // 向上传播错误以便UI层处理
    }
  }

  async function loadConversation(conversationId: string): Promise<void> {
    try {
      // 重置状态
      resetAiStatus();
      isGenerating.value = false;
      error.value = null;
      
      // 显式重置网页搜索状态
      updateAiStatus({
        webSearchEnabled: false
      });
      
      // 如果当前有正在生成的消息，先停止生成
      if (isGenerating.value) {
        await stopGenerating()
      }
      
      // 先清空消息列表，避免显示旧的对话内容
      messages.value = []
      resetAiStatus()
      
      const conversation = await chatApi.getConversation(conversationId)
      if (conversation) {
        // 确保所有消息的时间戳都是 ISO 格式
        messages.value = (conversation.messages || []).map(msg => ({
          ...msg,
          timestamp: msg.timestamp.endsWith('Z') ? msg.timestamp : msg.timestamp + 'Z'
        }));

        // 加载所有消息的思考时间数据
        messages.value.forEach(message => {
          if (message.role === 'assistant') {
            loadThinkingTimes(message, conversationId);
          }
        });

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
    
    // 如果是相同的模型，不做任何操作
    if (currentModel.value === model) {
      return;
    }
    
    // 设置模型加载状态
    updateAiStatus({
      model: ModelStatus.LOADING,
      loadingProgress: 0,
      generation: GenerationStatus.IDLE
    });
    
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
      updateAiStatus({
        generation: GenerationStatus.PAUSED
      });
      
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
      updateAiStatus({
        generation: GenerationStatus.COMPLETED,
        thinking: ThinkingStatus.IDLE,
        tool: ToolStatus.IDLE,
        websocketState: 'closed'
      });
      
      // 显示成功通知
      const notificationStore = useNotificationStore()
      notificationStore.show({
        type: 'SUCCESS',
        message: t('chat.notifications.abort_success')
      })
    } catch (err) {
      console.error('停止生成失败:', err)
      error.value = '停止生成失败'
      updateAiStatus({
        generation: GenerationStatus.FAILED,
        failureReason: '停止生成失败'
      });
      
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

  // 保存消息思考时间数据
  function saveMessageThinkingTimes(message: Message) {
    if (message.role !== 'assistant' || !currentConversationId.value) return;
    saveThinkingTimes(message, currentConversationId.value);
  }

  // 获取格式化的思考时间
  function getThinkingTime(message: Message): string {
    return getFormattedThinkingTime(message);
  }

  // 开始消息思考计时
  function startMessageThinking(message: Message): void {
    if (message.role !== 'assistant' || !currentConversationId.value) return;
    
    // 初始化元数据
    if (!message.metadata) {
      message.metadata = { thinkTimes: [] };
    } else if (!message.metadata.thinkTimes) {
      message.metadata.thinkTimes = [];
    }
    
    // 记录开始时间
    message.currentThinkStartTime = Date.now();
    
    // 添加新的思考时间记录
    if (message.metadata && message.metadata.thinkTimes) {
      message.metadata.thinkTimes.push({
        startTime: message.currentThinkStartTime
      });
    }
    
    // 保存到localStorage
    saveThinkingTimes(message, currentConversationId.value);
    
    // 更新UI状态
    updateAiStatus({
      thinking: ThinkingStatus.THINKING
    });
  }
  
  // 结束消息思考计时
  function endMessageThinking(message: Message): void {
    if (message.role !== 'assistant' || !currentConversationId.value || !message.currentThinkStartTime) return;
    
    // 记录结束时间
    message.currentThinkEndTime = Date.now();
    
    // 确保元数据存在
    if (!message.metadata) {
      message.metadata = { thinkTimes: [] };
    } else if (!message.metadata.thinkTimes) {
      message.metadata.thinkTimes = [];
    }
    
    // 更新最后一条思考记录
    if (message.metadata && message.metadata.thinkTimes && message.metadata.thinkTimes.length > 0) {
      const lastThinkIndex = message.metadata.thinkTimes.length - 1;
      const currentThink = message.metadata.thinkTimes[lastThinkIndex];
      if (currentThink && !currentThink.endTime) {
        currentThink.endTime = message.currentThinkEndTime;
        currentThink.duration = message.currentThinkEndTime - currentThink.startTime;
      }
    }
    
    // 保存到localStorage
    saveThinkingTimes(message, currentConversationId.value);
    
    // 重置当前思考时间，为下一次思考做准备
    message.currentThinkStartTime = undefined;
    message.currentThinkEndTime = undefined;
    
    // 更新UI状态
    updateAiStatus({
      thinking: ThinkingStatus.COMPLETED
    });
  }

  return {
    messages,
    currentModel,
    currentConversationId,
    isGenerating,
    error,
    aiStatus,
    sendMessage,
    setCurrentConversation,
    clearChat,
    loadConversation,
    setCurrentModel,
    updateMessage,
    stopGenerating,
    updateAiStatus,
    resetAiStatus,
    saveMessageThinkingTimes,
    getThinkingTime,
    getToolStatusText,
    startMessageThinking,
    endMessageThinking
  }
})