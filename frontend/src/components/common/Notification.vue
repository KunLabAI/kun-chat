<template>
  <div class="notifications-container">
    <TransitionGroup name="notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification"
        :class="[notification.type.toLowerCase()]"
      >
        <div class="notification-icon" v-if="notification.type">
          <component :is="getIcon(notification.type)" class="h-5 w-5" />
        </div>
        <div class="notification-content">
          <span class="message">{{ notification.message }}</span>
        </div>
        <button
          class="close-button"
          @click="() => removeNotification(notification.id)"
          :aria-label="t('common.notification.close')"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { useLocalization } from '@/i18n'
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const notificationStore = useNotificationStore()
const notifications = computed(() => notificationStore.notifications)
const { removeNotification } = notificationStore
const { t } = useLocalization()

type NotificationType = 'SUCCESS' | 'ERROR' | 'WARNING' | 'INFO'

const getIcon = (type: NotificationType) => {
  const icons = {
    SUCCESS: CheckCircleIcon,
    ERROR: ExclamationCircleIcon,
    WARNING: ExclamationCircleIcon,
    INFO: InformationCircleIcon
  } as const
  return icons[type]
}
</script>

<style scoped>
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.notification {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  max-width: 480px;
  transition: all 0.3s ease;
}

.dark .notification {
  background: #1f2937;
  color: white;
}

.notification-icon {
  flex-shrink: 0;
}

.notification-content {
  flex-grow: 1;
  font-size: 14px;
}

.notification.success .notification-icon {
  color: #10b981;
}

.notification.error .notification-icon {
  color: #ef4444;
}

.notification.warning .notification-icon {
  color: #f59e0b;
}

.notification.info .notification-icon {
  color: #3b82f6;
}

.close-button {
  flex-shrink: 0;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-button:hover {
  color: #374151;
  background: rgba(0, 0, 0, 0.05);
}

.dark .close-button:hover {
  color: #e5e7eb;
  background: rgba(255, 255, 255, 0.1);
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
