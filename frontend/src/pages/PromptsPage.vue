<template>
  <MainLayout>
    <div class="prompts-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="main-title">{{ t('prompt.title') }}</h1>
            <p class="sub-title">{{ t('prompt.subtitle') }}</p>
          </div>
          <div class="header-actions">
            <Button
              variant="primary"
              size="md"
              @click="router.push('/prompts/create')"
            >
              {{ t('prompt.create_prompt') }}
            </Button>
          </div>
        </div>
      </div>

      <!-- 提示词列表 -->
      <div v-if="promptStore.loading" class="loading-indicator">
        <DotLoader />
        <p class="mt-2">{{ t('status.loading') }}</p>
      </div>
      <div v-else-if="promptStore.error" class="error-message">
        {{ promptStore.error }}
      </div>
      <div v-else-if="prompts.length === 0" class="empty-state">
        {{ t('prompt.empty_state.subtitle') }}
      </div>
      <div v-else class="prompts-grid">
        <div v-for="prompt in prompts" :key="prompt.id" class="prompt-grid-item">
          <PromptCard
            :prompt="prompt"
            @edit="router.push(`/prompts/${prompt.id}/edit`)"
          >
            <template #actions>
              <button
                @click="confirmDeletePrompt(prompt)"
                class="prompt-delete"
              >
                <img 
                  src="@/assets/icons/model_delete.svg" 
                  class="h-5 w-5 filter" 
                  :class="{'hover-red': true}"
                  alt="删除" 
                />
              </button>
            </template>
          </PromptCard>
        </div>
      </div>
    </div>

    <!-- 提示词表单对话框 -->
    <Dialog
      v-model="showPromptForm"
      :title="editingPrompt ? t('prompt.edit_prompt') : t('prompt.create_prompt')"
    >
      <PromptForm
        :initial-data="editingPrompt || {}"
        @submit="(data) => handlePromptSubmit(data)"
        @cancel="showPromptForm = false"
      />
    </Dialog>

    <!-- 删除确认对话框 -->
    <Dialog
      v-model="showDeleteConfirm"
      :title="t('prompt.delete_dialog.title')"
      @confirm="executeDelete"
      @cancel="showDeleteConfirm = false"
      :confirm-text="t('common.actions.delete')"
      :cancel-text="t('common.actions.cancel')"
      confirm-variant="danger"
    >
      <div class="delete-confirm-content">
        <p>{{ t('prompt.delete_dialog.confirm_message') }}</p>
      </div>
    </Dialog>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import MainLayout from '@/layouts/MainLayout.vue'
import PromptCard from '@/components/prompts/PromptCard.vue'
import PromptForm from '@/components/prompts/PromptForm.vue'
import Button from '@/components/common/Button.vue'
import Dialog from '@/components/common/Dialog.vue'
import DotLoader from '@/components/common/DotLoader.vue'
import { usePromptStore } from '@/stores/promptStore'
import { useNotificationStore } from '@/stores/notification'
import { type Prompt, type PromptBase } from '@/api/prompts'
import { useRouter } from 'vue-router'
import { useLocalization } from '@/i18n'

const { t } = useLocalization()
const promptStore = usePromptStore()
const notificationStore = useNotificationStore()
const { prompts } = storeToRefs(promptStore)
const router = useRouter()

const showPromptForm = ref(false)
const editingPrompt = ref<Prompt | null>(null)
const showDeleteConfirm = ref(false)
const promptToDelete = ref<Prompt | null>(null)

onMounted(async () => {
  await promptStore.loadPrompts()
})

function confirmDeletePrompt(prompt: Prompt) {
  promptToDelete.value = prompt
  showDeleteConfirm.value = true
}

async function executeDelete() {
  if (!promptToDelete.value) return
  
  try {
    await promptStore.deletePrompt(promptToDelete.value.id)
    notificationStore.success(t('prompt.notifications.delete_success'))
    showDeleteConfirm.value = false
    promptToDelete.value = null
  } catch (error) {
    console.error('删除提示词失败:', error)
    notificationStore.error(t('prompt.notifications.delete_error'))
  }
}

async function handlePromptSubmit(formData: PromptBase) {
  try {
    if (editingPrompt.value) {
      await promptStore.updatePrompt({
        ...formData,
        id: editingPrompt.value.id,
        created_at: editingPrompt.value.created_at,
        updated_at: editingPrompt.value.updated_at
      })
      notificationStore.success(t('prompt.notifications.update_success'))
    } else {
      await promptStore.createPrompt(formData)
      notificationStore.success(t('prompt.notifications.create_success'))
    }
    showPromptForm.value = false
    editingPrompt.value = null
  } catch (error) {
    console.error('保存提示词失败:', error)
    notificationStore.error(editingPrompt.value ? t('prompt.notifications.update_error') : t('prompt.notifications.create_error'))
  }
}
</script>

<style scoped>
@import '@/styles/PromptsPage.css';

</style>
