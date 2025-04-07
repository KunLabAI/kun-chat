<template>
  <MainLayout>
    <div class="home-container">
      <!-- 顶部标题区域 -->
      <header class="home-header">
        <h1 class="home-title">{{ t('home.welcome', [authStore.user.nickname || authStore.user.username || '']) }}</h1>
        <p class="home-subtitle">{{ t('home.subtitle') }}</p>
      </header>

      <!-- 收藏模型列表区域 -->
      <section class="models-section">
        <div class="view-more">
          <h2 class="models-title">{{ t('home.favorite_models.title') }}</h2>
          <RouterLink to="/models" class="view-more-link">
            <span>{{ t('home.favorite_models.view_more') }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="view-more-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </RouterLink>
        </div>
        <div v-if="isLoading" class="loading-state">
          <DotLoader />
        </div>
        <div v-else-if="favoriteModels.length > 0" class="models-grid">
          <RouterLink v-for="model in limitedFavoriteModels" :key="model.name" :to="{ name: 'model-detail', params: { id: model.id }, query: { from: 'home' } }" class="model-card-link">
            <ModelCard
              :model="model"
              @view-details="viewModelDetails"
              @start-chat="startChat"
              @delete="deleteModel"
            />
          </RouterLink>
        </div>
        <div v-else class="empty-state">
          <div class="onboarding-container">
            <div class="welcome-illustration">
              <img src="@/assets/illustration/welcome.png" alt="Welcome" class="welcome-image">
            </div>
            <div class="onboarding-steps">
              <a href="https://ollama.com/download" target="_blank" rel="noopener noreferrer" class="onboarding-button" 
                 :data-tooltip="t('home.onboarding.install_ollama')"
                 @mouseenter="updateTooltipPosition">
                <div class="step-content">
                  <div class="step-icon">
                    <img src="@/assets/modelslogo/Ollama_icon.svg" alt="Ollama" class="icon-image" />
                  </div>
                </div>
              </a>
              
              <div class="step-connector">
                <div class="connector-line">
                  <img src="@/assets/icons/sys_arrowright.svg" alt="箭头" class="arrow-icon" />
                </div>
              </div>
              
              <RouterLink to="/models/pull" class="onboarding-button" 
                           :data-tooltip="t('home.onboarding.pull_models')"
                           @mouseenter="updateTooltipPosition">
                <div class="step-content">
                  <div class="step-icon">
                    <img src="@/assets/icons/sys_download.svg" alt="下载" class="icon-image" />
                  </div>
                </div>
              </RouterLink>
            </div>
          </div>
        </div>
      </section>

      <!-- 底部开始对话按钮 -->
      <div class="new-chat-button-container">
        <button class="btn" @click="startNewChat">
          <svg height="24" width="24" fill="#FFFFFF" viewBox="0 0 24 24" data-name="Layer 1" id="Layer_1" class="sparkle">
            <path d="M10,21.236,6.755,14.745.264,11.5,6.755,8.255,10,1.764l3.245,6.491L19.736,11.5l-6.491,3.245ZM18,21l1.5,3L21,21l3-1.5L21,18l-1.5-3L18,18l-3,1.5ZM19.333,4.667,20.5,7l1.167-2.333L24,3.5,21.667,2.333,20.5,0,19.333,2.333,17,3.5Z"></path>
          </svg>
          <span class="text">{{ t('home.new_chat') }}</span>
        </button>
      </div>
    </div>
    <Dialog
      v-model="showDeleteDialog"
      :title="t('home.delete_model.title')"
      :confirm-text="t('common.actions.delete')"
      :cancel-text="t('common.actions.cancel')"
      @confirm="confirmDelete"
    >
      <p>{{ t('home.delete_model.confirm_message', [modelToDelete?.name]) }}</p>
    </Dialog>
  </MainLayout>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { ChatBubbleLeftRightIcon } from '@heroicons/vue/24/outline'
import MainLayout from '@/layouts/MainLayout.vue'
import ModelCard from '@/components/models/ModelCard.vue'
import Dialog from '@/components/common/Dialog.vue'
import DotLoader from '@/components/common/DotLoader.vue'
import { useChatStore } from '@/stores/chat'
import { useModelsStore } from '@/stores/models'
import { useAuthStore } from '@/stores/auth'
import { useConversation } from '@/hooks/chat/useConversation'
import { useNotificationStore } from '@/stores/notification'
import { API_URL, getAuthHeaders } from '@/api/config'
import { useLocalization } from '@/i18n/composables'

const router = useRouter()
const chatStore = useChatStore()
const modelsStore = useModelsStore()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const { createConversation } = useConversation()
const { t } = useLocalization()

// 获取最近6个模型
const recentModels = computed(() => {
  return [...modelsStore.models]
    .sort((a, b) => new Date(b.modified_at || 0) - new Date(a.modified_at || 0))
    .slice(0, 6)
})

// 获取收藏的模型
const favoriteModels = ref([])
const isLoading = ref(true)

// 限制收藏模型显示数量为最多6个
const limitedFavoriteModels = computed(() => {
  return favoriteModels.value.slice(0, 6)
})

// 删除确认相关
const showDeleteDialog = ref(false)
const modelToDelete = ref(null)

// 获取收藏模型列表
async function fetchFavoriteModels() {
  try {
    if (!authStore.user.username) return
    isLoading.value = true
    favoriteModels.value = await modelsStore.getFavoriteModels(authStore.user.username)
    
    // 设置收藏状态
    favoriteModels.value.forEach(model => {
      model.is_favorite = true
    })
  } catch (error) {
    console.error('获取收藏模型失败:', error)
    notificationStore.showError(t('status.error'))
  } finally {
    isLoading.value = false
  }
}

function formatDate(date) {
  if (!date) return t('status.info')
  return new Date(date).toLocaleString()
}

function getModelActionText(model) {
  if (modelsStore.isLoading) return t('status.loading')
  return t('home.new_chat')
}

function formatSize(size) {
  if (!size) return t('status.info')
  return `${(size / 1024 / 1024).toFixed(2)} MB`
}

async function startChat(model) {
  if (modelsStore.isLoading) return

  try {
    const conversation = await createConversation({
      title: `与 ${model.display_name || model.name} 的对话`,
      model: model.name
    })
    
    if (conversation && conversation.conversation_id) {
      chatStore.setCurrentModel(model.name)
      chatStore.setCurrentConversation(conversation.conversation_id)
      router.push(`/chat/${conversation.conversation_id}`)
    } else {
      throw new Error(t('status.error'))
    }
  } catch (error) {
    console.error('创建对话失败:', error)
    notificationStore.showError(error instanceof Error ? error.message : t('status.error'))
  }
}

function viewModelDetails(model) {
  router.push({
    name: 'model-detail',
    params: { id: model.id },
    query: { from: 'home' }
  })
}

function deleteModel(model) {
  modelToDelete.value = model
  showDeleteDialog.value = true
}

async function confirmDelete() {
  if (!modelToDelete.value) return
  
  try {
    await modelsStore.deleteModel(modelToDelete.value.id)
    await modelsStore.fetchModels()
    await fetchFavoriteModels()
    notificationStore.showSuccess(t('status.success'))
    
    showDeleteDialog.value = false
    modelToDelete.value = null
  } catch (error) {
    console.error('删除模型失败:', error)
    notificationStore.showError(t('status.error'))
  }
}

// 添加工具提示位置更新方法
function updateTooltipPosition(event) {
  // 当前悬停的按钮元素
  const button = event.currentTarget;
  
  // 计算工具提示的位置，确保在所有设备上都正确显示
  // 这个函数可以根据需要扩展，例如检测边缘情况
  // 目前只是一个辅助函数，用于未来可能的扩展
}

// 开始新对话
async function startNewChat() {
  if (modelsStore.isLoading) return

  try {
    const defaultModel = modelsStore.models[0]?.name
    if (!defaultModel) {
      notificationStore.showError('没有可用的模型')
      return
    }

    const conversation = await createConversation({
      title: `新对话`,
      model: defaultModel
    })
    
    if (conversation && conversation.conversation_id) {
      chatStore.setCurrentModel(defaultModel)
      chatStore.setCurrentConversation(conversation.conversation_id)
      router.push(`/chat/${conversation.conversation_id}`)
    } else {
      throw new Error('创建对话失败：未获取到对话ID')
    }
  } catch (error) {
    console.error('创建对话失败:', error)
    notificationStore.showError(error instanceof Error ? error.message : '创建对话失败')
  }
}

// 获取用户信息
async function fetchUserInfo() {
  if (!authStore.isAuthenticated) return
  try {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: getAuthHeaders()
    })
    if (response.ok) {
      const userData = await response.json()
      authStore.setUser(userData)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

onMounted(async () => {
  await modelsStore.fetchModels()
  // 确保先获取用户信息，再获取收藏模型
  if (authStore.isAuthenticated && !authStore.user.username) {
    await fetchUserInfo()
  }
  await fetchFavoriteModels()
})
</script>

<style scoped>
@import '@/styles/HomePage.css';
</style>
