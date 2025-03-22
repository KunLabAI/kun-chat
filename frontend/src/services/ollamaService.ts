import { ollamaApi } from '@/api/ollama'
import { useNotificationStore } from '@/stores/notification'

// Ollama 连接状态
let isConnected = false
let ollamaVersion = ''
let connectionError = ''

/**
 * 初始化 Ollama 服务
 * 静默检查连接状态，不显示通知
 */
export async function initOllamaService(): Promise<boolean> {
  try {
    console.log('正在初始化 Ollama 服务...')
    const settings = await ollamaApi.getConnectionSettings()
    
    // 如果没有配置 Ollama 主机地址，则跳过连接检查
    if (!settings.host) {
      console.log('未配置 Ollama 主机地址，跳过连接检查')
      isConnected = false
      connectionError = '未配置 Ollama 主机地址'
      return false
    }
    
    // 静默检查连接状态
    const response = await ollamaApi.checkConnection()
    
    // 确保我们正确解析连接状态
    isConnected = response && response.connected === true
    ollamaVersion = isConnected ? (response.version || '未知') : ''
    connectionError = response.error || ''
    
    if (isConnected) {
      console.log(`Ollama 服务连接成功，版本: ${ollamaVersion}`)
    } else {
      console.warn(`Ollama 服务连接失败: ${connectionError}`)
    }
    
    return isConnected
  } catch (error: any) {
    console.error('初始化 Ollama 服务失败:', error)
    isConnected = false
    connectionError = error?.message || '未知错误'
    return false
  }
}

/**
 * 显示 Ollama 连接状态通知
 * 仅在用户首次登录或注册后调用
 */
export function showOllamaStatusNotification(forceShow: boolean = false): void {
  const notificationStore = useNotificationStore()
  
  // 始终显示通知，无论连接状态如何
  if (forceShow) {
    if (isConnected) {
      notificationStore.show({
        type: 'SUCCESS',
        message: `Ollama 服务已连接 (${ollamaVersion})`,
        duration: 5000
      })
    } else {
      notificationStore.show({
        type: 'WARNING',
        message: `Ollama 服务未连接，部分功能可能不可用。可能的原因：您未启动 Ollama，或地址和端口未正确设置。`,
        duration: 8000
      })
    }
  }
}

/**
 * 获取 Ollama 连接状态
 */
export function getOllamaConnectionStatus(): { connected: boolean; version: string; error: string } {
  return {
    connected: isConnected,
    version: ollamaVersion,
    error: connectionError
  }
}
