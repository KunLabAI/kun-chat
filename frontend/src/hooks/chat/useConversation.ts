import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Message, Conversation, ConversationCreate } from '@/types'
import { chatApi } from '@/api/chat'

export function useConversation() {
  const router = useRouter()
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const sortedConversations = computed(() => {
    return [...conversations.value].sort((a, b) => 
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  })

  const loadConversations = async () => {
    try {
      loading.value = true
      const response = await chatApi.getConversations()
      conversations.value = response.map((conv: any) => ({
        ...conv,
        messages: conv.messages || []
      }))
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载对话列表失败'
    } finally {
      loading.value = false
    }
  }

  const loadConversation = async (conversationId: string) => {
    try {
      loading.value = true
      const response = await chatApi.getConversation(conversationId)
      if (response) {
        currentConversation.value = {
          conversation_id: response.conversation_id,
          title: response.title,
          model: response.model,
          created_at: response.created_at,
          updated_at: response.updated_at,
          messages: response.messages || []
        }
      } else {
        error.value = '未找到对话或对话数据为空'
        currentConversation.value = null
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载对话失败'
      currentConversation.value = null
    } finally {
      loading.value = false
    }
  }

  const createConversation = async (params: ConversationCreate): Promise<Conversation | null> => {
    try {
      loading.value = true
      const response = await chatApi.createConversation(params)
      if (response) {
        return {
          conversation_id: response.conversation_id,
          title: response.title || '',
          model: response.model,
          created_at: response.created_at,
          updated_at: response.updated_at,
          messages: response.messages || []
        }
      }
      return null
    } catch (e) {
      error.value = e instanceof Error ? e.message : '创建对话失败'
      return null
    } finally {
      loading.value = false
    }
  }

  const deleteConversation = async (conversationId: string) => {
    try {
      loading.value = true
      await chatApi.deleteConversation(conversationId)
      conversations.value = conversations.value.filter(c => c.conversation_id !== conversationId)
      if (currentConversation.value?.conversation_id === conversationId) {
        currentConversation.value = null
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '删除对话失败'
    } finally {
      loading.value = false
    }
  }

  return {
    conversations,
    currentConversation,
    sortedConversations,
    loading,
    error,
    loadConversations,
    loadConversation,
    createConversation,
    deleteConversation
  }
}
