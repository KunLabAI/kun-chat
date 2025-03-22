<template>
  <div class="settings-section">
    <h3 class="settings-section-title">{{ $t('settings.connection.ollama.title') }}</h3>
    <div class="settings-section-content">
      <!-- Ollama 连接状态 -->
      <div class="settings-form-group">
        <label class="settings-form-label">{{ $t('settings.connection.ollama.status.label') }}</label>
        <p class="settings-form-help mb-4">
          {{ $t('settings.connection.ollama.status.description') }}
        </p>
        <div class="status-container">
          <div class="status-item">
            <span class="status-label">{{ $t('settings.connection.ollama.status.state') }}：</span>
            <span class="status-value" :class="{'status-connected': isConnected, 'status-disconnected': !isConnected}">
              {{ isConnected ? $t('settings.connection.ollama.status.connected') : $t('settings.connection.ollama.status.disconnected') }}
            </span>
          </div>
          <div class="status-item" v-if="isConnected">
            <span class="status-label">{{ $t('settings.connection.ollama.status.version') }}：</span>
            <span class="status-value">{{ ollamaVersion }}</span>
            <span class="status-info" v-if="versionCompatibility">
              {{ versionCompatibility }}
            </span>
          </div>
        </div>
        <button class="settings-test-button" @click="checkConnection" :disabled="isChecking">
          <span v-if="isChecking">{{ $t('settings.connection.ollama.checking') }}</span>
          <span v-else>{{ $t('settings.connection.ollama.test_button') }}</span>
        </button>
      </div>

      <!-- Ollama 连接设置 -->
      <div class="settings-form-group">
        <label class="settings-form-label">{{ $t('settings.connection.ollama.host.label') }}</label>
        <p class="settings-form-help mb-4">
          {{ $t('settings.connection.ollama.host.description') }}
        </p>
        <div class="settings-api-key-container">
          <input 
            type="text" 
            v-model="ollamaHost" 
            class="settings-form-input"
            :placeholder="$t('settings.connection.ollama.host.placeholder')"
            :disabled="isSaving"
          >
          <div class="settings-api-key-actions">
            <button
              @click="saveConnectionSettings"
              class="settings-api-key-action"
              :disabled="isSaving || !ollamaHost || ollamaHost.trim() === ''"
              :title="$t('settings.connection.ollama.save_button')"
            >
              <img v-if="!isSaving" :src="saveIcon" alt="save" />
              <span v-else class="loading-spinner"></span>
            </button>
          </div>
        </div>
      </div>

      <!-- 自动检测设置 -->
      <div class="settings-form-group">
        <div class="settings-toggle-container">
          <span class="settings-toggle-label">{{ $t('settings.connection.ollama.auto_check.label') }}（{{ $t('settings.connection.ollama.auto_check.description') }}）</span>
          <label class="settings-toggle-switch">
            <input 
              type="checkbox" 
              v-model="enableAutoCheck"
              @change="saveAutoCheckSetting"
            >
            <span class="settings-toggle-slider"></span>
          </label>
        </div>
      </div>

      <!-- 通知设置 -->
      <div class="settings-form-group">
        <div class="settings-toggle-container">
          <span class="settings-toggle-label">{{ $t('settings.connection.ollama.notification.label') }}</span>
          <label class="settings-toggle-switch">
            <input 
              type="checkbox" 
              v-model="showNotification"
              @change="saveNotificationSetting"
            >
            <span class="settings-toggle-slider"></span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useNotificationStore } from '@/stores/notification'
import { ollamaApi } from '@/api/ollama'
import saveIcon from '@/assets/icons/sys_save.svg'

const { t } = useI18n()
const notificationStore = useNotificationStore()

// 状态变量
const isConnected = ref(false)
const isChecking = ref(false)
const isSaving = ref(false)
const ollamaVersion = ref('')
const versionCompatibility = ref('')
const ollamaHost = ref('')  // 初始为空，将从后端获取
const enableAutoCheck = ref(true)
const showNotification = ref(true)
let checkIntervalTimer = null
const isInitialCheck = ref(true) // 标记是否是初始检查

// 检查 Ollama 连接状态
const checkConnection = async () => {
  if (isChecking.value) return
  
  isChecking.value = true
  try {
    const response = await ollamaApi.checkConnection()
    console.log('Ollama 连接检查结果:', response)
    isConnected.value = response.connected
    
    if (response.connected) {
      ollamaVersion.value = response.version || '未知'
      console.log('Ollama 版本:', ollamaVersion.value)
      
      // 简单的版本兼容性检查
      const versionNumber = ollamaVersion.value.replace('v', '')
      console.log('版本号解析结果:', versionNumber)
      if (versionNumber && parseFloat(versionNumber) < 0.1) {
        versionCompatibility.value = '(版本过低，建议升级)'
      } else {
        versionCompatibility.value = '(兼容)'
      }
      
      // 只有在非初始检查且启用了通知时才显示成功通知
      if (!isInitialCheck.value && showNotification.value) {
        notificationStore.show({
          type: 'success',
          message: t('settings.connection.ollama.notification.connected', { version: ollamaVersion.value })
        })
      }
    } else {
      ollamaVersion.value = ''
      versionCompatibility.value = ''
      
      // 只有在非初始检查且启用了通知时才显示错误通知
      if (!isInitialCheck.value && showNotification.value) {
        notificationStore.show({
          type: 'error',
          message: t('settings.connection.ollama.notification.disconnected', { host: ollamaHost.value })
        })
      }
    }
  } catch (error) {
    console.error('检查 Ollama 连接失败:', error)
    isConnected.value = false
    ollamaVersion.value = ''
    versionCompatibility.value = ''
    
    // 只有在非初始检查且启用了通知时才显示错误通知
    if (!isInitialCheck.value && showNotification.value) {
      notificationStore.show({
        type: 'error',
        message: t('settings.connection.ollama.notification.disconnected', { host: ollamaHost.value })
      })
    }
  } finally {
    isChecking.value = false
    // 如果是初始检查，将标记设置为 false，后续检查将显示通知
    if (isInitialCheck.value) {
      isInitialCheck.value = false
    }
  }
}

// 保存连接设置
const saveConnectionSettings = async () => {
  if (isSaving.value || !ollamaHost.value) return
  
  isSaving.value = true
  try {
    await ollamaApi.updateConnectionSettings({
      host: ollamaHost.value
    })
    
    notificationStore.show({
      type: 'success',
      message: t('settings.connection.ollama.save_success')
    })
    
    // 保存后立即检查连接
    await checkConnection()
  } catch (error) {
    console.error('保存 Ollama 连接设置失败:', error)
    notificationStore.show({
      type: 'error',
      message: t('settings.connection.ollama.save_failed')
    })
  } finally {
    isSaving.value = false
  }
}

// 保存自动检测设置
const saveAutoCheckSetting = async () => {
  try {
    await ollamaApi.updateCheckSettings({
      enabled: enableAutoCheck.value,
      interval: 30 * 60 // 默认30分钟（秒为单位）
    })
    
    // 重新设置定时器
    setupAutoCheck()
  } catch (error) {
    console.error('保存自动检测设置失败:', error)
    notificationStore.show({
      type: 'error',
      message: t('settings.connection.ollama.save_failed')
    })
    // 恢复原值
    enableAutoCheck.value = !enableAutoCheck.value
  }
}

// 保存通知设置
const saveNotificationSetting = async () => {
  try {
    await ollamaApi.updateCheckSettings({
      notification: showNotification.value
    })
  } catch (error) {
    console.error('保存通知设置失败:', error)
    notificationStore.show({
      type: 'error',
      message: t('settings.connection.ollama.save_failed')
    })
    // 恢复原值
    showNotification.value = !showNotification.value
  }
}

// 设置自动检测定时器
const setupAutoCheck = () => {
  // 清除现有定时器
  if (checkIntervalTimer) {
    clearInterval(checkIntervalTimer)
    checkIntervalTimer = null
  }
  
  // 如果启用了自动检测，设置新的定时器
  if (enableAutoCheck.value) {
    const intervalMs = 30 * 60 * 1000 // 默认30分钟
    checkIntervalTimer = setInterval(checkConnection, intervalMs)
  }
}

// 加载设置
const loadSettings = async () => {
  try {
    const settings = await ollamaApi.getConnectionSettings()
    console.log('加载到的 Ollama 设置:', settings)
    ollamaHost.value = settings.host || ''
    enableAutoCheck.value = settings.enableAutoCheck !== false
    showNotification.value = settings.showNotification !== false
    
    // 初始化自动检测
    setupAutoCheck()
    
    // 立即检查连接
    if (ollamaHost.value) {
      await checkConnection()
    } else {
      console.warn('未配置 Ollama 主机地址，跳过连接检查')
    }
  } catch (error) {
    console.error('加载 Ollama 设置失败:', error)
    notificationStore.show({
      type: 'error',
      message: t('settings.connection.ollama.load_failed')
    })
  }
}

// 组件挂载时加载设置
onMounted(() => {
  loadSettings()
})

// 组件卸载时清除定时器
onUnmounted(() => {
  if (checkIntervalTimer) {
    clearInterval(checkIntervalTimer)
    checkIntervalTimer = null
  }
})
</script>

<style scoped>
@import './OllamaSettings.css';
</style>
