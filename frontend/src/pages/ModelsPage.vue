<template>
  <MainLayout>
    <div class="models-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="main-title">{{ t('model.title') }}</h1>
            <p class="sub-title">{{ t('model.subtitle') }}</p>
          </div>
          <div class="header-actions">
            <Button
              variant="primary"
              size="md"
              class="mr-2"
              @click="router.push('/models/custom')"
            >
              {{ t('model.custom_model') }}
            </Button>
            <Button
              variant="primary"
              size="md"
              @click="router.push('/models/pull')"
            >
              {{ t('model.pull_model') }}
            </Button>
          </div>
        </div>
      </div>

      <!-- 模型列表 -->
      <div v-if="modelsStore.isLoading" class="loading-indicator">
        <DotLoader />
      </div>
      <div v-else-if="modelsStore.error" class="error-message">
        {{ modelsStore.error }}
      </div>
      <div v-else-if="modelsStore.models.length === 0" class="empty-state">
        {{ t('model.empty_state') }}
      </div>
      <div v-else class="models-grid">
        <div v-for="model in modelsStore.sortedModels" :key="model.name" class="model-grid-item">
          <ModelCard
            :model="model"
            @view-details="viewModelDetails"
            @start-chat="startChat"
            @delete="deleteModel"
          />
        </div>
      </div>
    </div>
  </MainLayout>
  <Dialog
    v-model="showDeleteDialog"
    :title="t('model.delete_dialog.title')"
    :confirm-text="t('common.actions.delete')"
    :cancel-text="t('common.actions.cancel')"
    @confirm="confirmDelete"
  >
    <p>{{ t('model.delete_dialog.confirm_message', { 0: modelToDelete?.name }) }}</p>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import Button from '@/components/common/Button.vue'
import ModelCard from '@/components/models/ModelCard.vue'
import Dialog from '@/components/common/Dialog.vue'
import DotLoader from '@/components/common/DotLoader.vue'
import { useModelsStore } from '@/stores/models'
import { useChatStore } from '@/stores/chat'
import { useNotificationStore } from '@/stores/notification'
import { useAuthStore } from '@/stores/auth'
import { Model } from '@/types/models'
import { useConversation } from '@/hooks/chat/useConversation'
import { useLocalization } from '@/i18n/composables'

const router = useRouter()
const modelsStore = useModelsStore()
const chatStore = useChatStore()
const notificationStore = useNotificationStore()
const authStore = useAuthStore()
const { createConversation } = useConversation()
const { t } = useLocalization()

const showDeleteDialog = ref(false)
const modelToDelete = ref<Model | null>(null)

onMounted(async () => {
  await fetchModelsWithFavoriteStatus()
})

// 获取模型列表并设置收藏状态
async function fetchModelsWithFavoriteStatus() {
  await modelsStore.fetchModels()
  
  // 如果用户已登录，检查每个模型的收藏状态
  if (authStore.isAuthenticated && authStore.user.username) {
    const username = authStore.user.username
    
    // 获取所有收藏的模型
    const favoriteModels = await modelsStore.getFavoriteModels(username)
    const favoriteModelIds = favoriteModels.map(model => model.id)
    
    // 更新模型列表中的收藏状态
    modelsStore.models.forEach(model => {
      model.is_favorite = favoriteModelIds.includes(model.id)
    })
  }
}

const viewModelDetails = (model: Model) => {
  console.log('查看模型详情:', model.name)
  router.push({
    name: 'model-detail',
    params: {
      id: model.id.toString()
    }
  })
}

const startChat = async (model: Model) => {
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
      throw new Error(t('model.notifications.create_error'))
    }
  } catch (error) {
    console.error('创建对话失败:', error)
    notificationStore.showError(error instanceof Error ? error.message : t('model.notifications.create_error'))
  }
}

const deleteModel = (model: Model) => {
  modelToDelete.value = model
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  if (!modelToDelete.value) return
  
  try {
    await modelsStore.deleteModel(modelToDelete.value.id)
    notificationStore.showSuccess(t('model.notifications.delete_success'))
    showDeleteDialog.value = false
    modelToDelete.value = null
  } catch (error) {
    console.error('删除模型失败:', error)
    notificationStore.showError(t('model.notifications.delete_error'))
  }
}

// async function pullModel() {
//   if (!newModelName.value.trim()) return
  
//   try {
//     await modelsStore.pullModel(newModelName.value.trim())
//     showPullDialog.value = false
//     newModelName.value = ''
//     await modelsStore.fetchModels()
//   } catch (error) {
//     console.error('拉取模型失败:', error)
//   }
// }
</script>

<style scoped>
@import '@/styles/ModelsPage.css';
</style>
