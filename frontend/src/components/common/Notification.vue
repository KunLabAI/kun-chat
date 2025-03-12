<template>
  <div class="kun-notifications-container">
    <TransitionGroup name="kun-notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="kun-notification"
        :class="[`kun-notification-${notification.type.toLowerCase()}`]"
      >
        <div class="kun-notification-icon" v-if="notification.type">
          <component :is="getIcon(notification.type)" class="h-5 w-5" />
        </div>
        <div class="kun-notification-content">
          <span class="kun-notification-message">{{ notification.message }}</span>
        </div>
        <button
          class="kun-notification-close"
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
/* 通知容器 */
.kun-notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
}

/* 通知基础样式 */
.kun-notification {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background-color: var(--bg-color-light);
  border-radius: 8px;
  box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.1), 0 4px 8px -4px rgba(0, 0, 0, 0.06);
  min-width: 320px;
  max-width: 480px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-left: 4px solid transparent;
}

/* 深色模式通知基础样式 */
:global(.dark) .kun-notification {
  background-color: var(--gray-800);
  box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.3), 0 4px 8px -4px rgba(0, 0, 0, 0.2);
}

/* 通知图标 */
.kun-notification-icon {
  flex-shrink: 0;
}

/* 通知内容 */
.kun-notification-content {
  flex-grow: 1;
  font-size: 14px;
  color: var(--text-color);
}

/* 成功通知 */
.kun-notification-success {
  border-left-color: var(--success-500);
}

.kun-notification-success .kun-notification-icon {
  color: var(--success-500);
}

:global(.dark) .kun-notification-success .kun-notification-icon {
  color: var(--success-400);
}

/* 错误通知 */
.kun-notification-error {
  border-left-color: var(--red-500);
}

.kun-notification-error .kun-notification-icon {
  color: var(--red-500);
}

:global(.dark) .kun-notification-error .kun-notification-icon {
  color: var(--red-400);
}

/* 警告通知 */
.kun-notification-warning {
  border-left-color: #f59e0b;
}

.kun-notification-warning .kun-notification-icon {
  color: #f59e0b;
}

:global(.dark) .kun-notification-warning .kun-notification-icon {
  color: #fbbf24;
}

/* 信息通知 */
.kun-notification-info {
  border-left-color: var(--primary-500);
}

.kun-notification-info .kun-notification-icon {
  color: var(--primary-500);
}

:global(.dark) .kun-notification-info .kun-notification-icon {
  color: var(--primary-400);
}

/* 关闭按钮 */
.kun-notification-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: var(--text-color-lighter);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kun-notification-close:hover {
  color: var(--text-color-light);
  background-color: var(--button-hover-bg);
}

:global(.dark) .kun-notification-close:hover {
  color: var(--gray-300);
  background-color: var(--gray-700);
}

/* 过渡动画 */
.kun-notification-enter-active,
.kun-notification-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.kun-notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.kun-notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
