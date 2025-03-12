// src/stores/models.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { modelApi } from '@/api/models'
import { useNotificationStore } from './notification'
import type { Model, ModelInfo, ModelCreateRequest } from '@/types/models'

export const useModelsStore = defineStore('models', () => {
  const models = ref<Model[]>([])
  const lastUsedModel = ref('')
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const pullStatus = ref<{ [key: number]: any }>({})
  const createModelDialogVisible = ref(false)
  const notificationStore = useNotificationStore()

  // 添加计算属性，按照modified_at降序排序
  const sortedModels = computed(() => {
    return [...models.value].sort((a, b) => {
      const dateA = new Date(a.modified_at || new Date(0)).getTime()
      const dateB = new Date(b.modified_at || new Date(0)).getTime()
      return dateB - dateA // 降序排序，最新的在前面
    })
  })

  async function fetchModels() {
    isLoading.value = true
    error.value = null
    try {
      const response = await modelApi.getModelList()
      models.value = response
    } catch (e) {
      error.value = '获取模型列表失败'
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchModelDetails(modelId: number): Promise<ModelInfo | null> {
    console.log('store: 开始获取模型详情，ID:', modelId)
    isLoading.value = true
    error.value = null
    try {
      const details = await modelApi.getModelInfo(modelId)
      console.log('store: 获取到模型详情:', details)
      return details
    } catch (e) {
      error.value = '获取模型详情失败'
      console.error('store: 获取模型详情失败:', e)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function deleteModel(modelId: number) {
    isLoading.value = true
    error.value = null
    try {
      await modelApi.deleteModel(modelId)
      // 从本地状态中移除模型
      models.value = models.value.filter(model => model.id !== modelId)
    } catch (e) {
      error.value = '删除模型失败'
      console.error(e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function pullModel(modelId: number, onProgress?: (data: any) => void) {
    error.value = null
    try {
      console.log('Starting model pull:', modelId)
      
      // 查找对应的模型
      const model = models.value.find(m => m.id === modelId)
      if (!model) {
        throw new Error('Model not found')
      }

      // 初始化下载状态
      pullStatus.value[modelId] = {
        status: 'downloading',
        progress: 0,
        total_size: 0,
        downloaded_size: 0,
        details: [],
        error: null
      }

      const eventSource = modelApi.pullModel(model.name)
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)
        console.log('Progress update in store:', data)
        
        // 更新状态
        pullStatus.value[modelId] = {
          ...pullStatus.value[modelId],
          ...data
        }
        
        // 调用进度回调
        onProgress?.(pullStatus.value[modelId])

        // 如果下载完成，刷新模型列表并关闭 EventSource
        if (data.status === 'completed') {
          console.log('Pull completed, refreshing models list')
          eventSource.close()
          fetchModels()
        }
      }

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error)
        pullStatus.value[modelId].error = 'Download failed'
        pullStatus.value[modelId].status = 'error'
        eventSource.close()
      }
    } catch (e) {
      console.error('Pull model error:', e)
      error.value = '拉取模型失败'
      pullStatus.value[modelId] = {
        ...pullStatus.value[modelId],
        status: 'failed',
        error: e instanceof Error ? e.message : String(e)
      }
      throw e
    }
  }

  async function cancelPull(modelId: number) {
    error.value = null
    try {
      // 查找对应的模型
      const model = models.value.find(m => m.id === modelId)
      if (!model) {
        throw new Error('Model not found')
      }

      await modelApi.cancelPull(model.name)
      pullStatus.value[modelId] = {
        ...pullStatus.value[modelId],
        status: 'cancelled'
      }
    } catch (e) {
      error.value = '取消拉取失败'
      console.error(e)
      throw e
    }
  }

  async function createModel(request: ModelCreateRequest) {
    isLoading.value = true
    error.value = null
    try {
      const response = await modelApi.createModel(request)
      await fetchModels() // 刷新模型列表
      return response
    } catch (e) {
      error.value = '创建模型失败'
      console.error(e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function showCreateModelDialog() {
    createModelDialogVisible.value = true
  }

  function hideCreateModelDialog() {
    createModelDialogVisible.value = false
  }

  async function fetchChatModels() {
    isLoading.value = true
    error.value = null
    try {
      const response = await modelApi.getModelList()
      models.value = response
    } catch (e) {
      error.value = '获取聊天模型列表失败'
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  // 获取收藏的模型列表
  async function getFavoriteModels(username: string): Promise<Model[]> {
    try {
      return await modelApi.getFavoriteModels(username)
    } catch (e) {
      console.error('获取收藏模型列表失败:', e)
      return []
    }
  }

  // 检查模型是否已收藏
  async function checkFavoriteStatus(modelId: number, username: string): Promise<boolean> {
    try {
      return await modelApi.checkFavoriteStatus(modelId, username)
    } catch (e) {
      console.error('检查收藏状态失败:', e)
      return false
    }
  }

  // 切换模型收藏状态
  async function toggleFavorite(modelId: number, username: string): Promise<{ is_favorited: boolean, message: string }> {
    try {
      return await modelApi.toggleFavorite(modelId, username)
    } catch (e) {
      console.error('切换收藏状态失败:', e)
      throw e
    }
  }

  async function waitForChatModels() {
    if (models.value.length > 0) {
      return lastUsedModel.value
    }
    
    try {
      await fetchChatModels()
      return lastUsedModel.value
    } catch (error) {
      return null
    }
  }

  const setLastUsedChatModel = (modelName: string) => {
    lastUsedModel.value = modelName
  }

  return {
    models,
    lastUsedModel,
    isLoading,
    error,
    pullStatus,
    createModelDialogVisible,
    fetchModels,
    fetchModelDetails,
    deleteModel,
    pullModel,
    cancelPull,
    createModel,
    showCreateModelDialog,
    hideCreateModelDialog,
    fetchChatModels,
    waitForChatModels,
    setLastUsedChatModel,
    getFavoriteModels,
    checkFavoriteStatus,
    toggleFavorite,
    sortedModels
  }
})