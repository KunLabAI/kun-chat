<template>
  <div class="model-card">
    <div class="model-card-static">
      <img :src="getModelLogo(model.family || 'default')" :alt="model.family || t('model.card.unknown')" class="model-card-icon">
      <h2 class="model-card-title">{{ model.display_name || model.name }}</h2>
    </div>
    <div v-if="model.is_favorite" class="favorite-star">
      <img :src="starIconSrc" width="20" height="20" alt="已收藏" />
    </div>
    <div class="model-card-hover">
      <div class="model-card-info">
        <p>{{ t('model.card.parameter_size') }}: {{ model.parameter_size || t('model.card.unknown') }}</p>
        <p>{{ t('model.card.file_size') }}: {{ model.size ? formatFileSize(model.size) : t('model.card.unknown') }}</p>
        <p>{{ t('model.card.modified_time') }}: {{ model.modified_at ? formatDate(model.modified_at) : t('model.card.unknown') }}</p>
      </div>
      <div class="model-card-buttons">
        <button 
          class="model-card-button details-button" 
          :data-tooltip="t('model.card.tooltip.details')"
          @mouseenter="updateTooltipPosition"
          @click.prevent="$emit('view-details', model)"
          type="button"
        >
          <img src="@/assets/icons/model_details.svg" :alt="t('model.card.tooltip.details')" />
        </button>
        <button 
          class="model-card-button chat-button" 
          :data-tooltip="t('model.card.tooltip.chat')"
          @mouseenter="updateTooltipPosition"
          @click.prevent="handleStartChat"
          type="button"
        >
          <img src="@/assets/icons/model_chat.svg" :alt="t('model.card.tooltip.chat')" />
        </button>
        <button 
          class="model-card-button delete-button" 
          :data-tooltip="t('model.card.tooltip.delete')"
          @mouseenter="updateTooltipPosition"
          @click.prevent="handleDelete"
          type="button"
        >
          <img src="@/assets/icons/model_delete.svg" :alt="t('model.card.tooltip.delete')" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Model } from '@/types/models'
import { getModelLogo } from '@/utils/ModelsLogoMap'
import { useNotificationStore } from '@/stores/notification'
import { useLocalization } from '@/i18n/composables'
import '@/styles/ModelCard.css'

const notificationStore = useNotificationStore()
const { t } = useLocalization()

const props = defineProps<{
  model: Model
}>()

const emit = defineEmits<{
  (e: 'view-details', model: Model): void
  (e: 'start-chat', model: Model): void
  (e: 'delete', model: Model): void
}>()

// 导入星星图标
const starIconSrc = new URL('@/assets/icons/sys_star.svg', import.meta.url).href

const handleStartChat = async () => {
  try {
    emit('start-chat', props.model)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : t('model.notifications.create_error')
    notificationStore.showError(errorMessage)
  }
}

const handleDelete = () => {
  try {
    emit('delete', props.model)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : t('model.notifications.delete_error')
    notificationStore.showError(errorMessage)
  }
}

const updateTooltipPosition = (event: MouseEvent) => {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const tooltip = target.getAttribute('data-tooltip')
  if (tooltip) {
    target.style.setProperty('--tooltip-top', `${rect.top - 30}px`)
    target.style.setProperty('--tooltip-left', `${rect.left + rect.width / 2}px`)
  }
}

const formatFileSize = (size: number): string => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(2)} MB`
  return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

const formatDate = (date: string): string => {
  return new Date(date).toLocaleString(t('common.locale', 'zh-CN'), {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>