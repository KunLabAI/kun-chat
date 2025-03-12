import { defineStore } from 'pinia'
import { ref } from 'vue'

export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
} as const

export const NOTIFICATION_DURATION = {
  SHORT: 3000,
  MEDIUM: 5000,
  LONG: 8000
} as const

export interface Notification {
  id: number
  type: keyof typeof NOTIFICATION_TYPES
  message: string
  duration?: number
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  let nextId = 1

  const addNotification = (
    message: string,
    type: keyof typeof NOTIFICATION_TYPES = 'INFO',
    duration: number = NOTIFICATION_DURATION.MEDIUM
  ) => {
    const id = nextId++
    const notification = { id, type, message, duration }
    notifications.value.push(notification)
    
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }
  }

  const removeNotification = (id: number) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  const clearAll = () => {
    notifications.value = []
  }

  const error = (message: string, duration: number = NOTIFICATION_DURATION.MEDIUM) => {
    addNotification(message, 'ERROR', duration)
  }

  const warning = (message: string, duration: number = NOTIFICATION_DURATION.MEDIUM) => {
    addNotification(message, 'WARNING', duration)
  }

  const info = (message: string, duration: number = NOTIFICATION_DURATION.MEDIUM) => {
    addNotification(message, 'INFO', duration)
  }

  const success = (message: string, duration: number = NOTIFICATION_DURATION.MEDIUM) => {
    addNotification(message, 'SUCCESS', duration)
  }

  const showError = (message: string, duration: number = NOTIFICATION_DURATION.MEDIUM) => {
    error(message, duration)
  }

  const showSuccess = (message: string, duration: number = NOTIFICATION_DURATION.MEDIUM) => {
    success(message, duration)
  }

  const show = (options: { type: keyof typeof NOTIFICATION_TYPES; message: string; duration?: number }) => {
    const { type, message, duration = NOTIFICATION_DURATION.MEDIUM } = options
    addNotification(message, type, duration)
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    error,
    warning,
    info,
    success,
    showError,
    showSuccess,
    show
  }
})
