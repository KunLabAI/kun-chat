import { API_URL, getAuthHeaders, fetchWithRetry } from './config'

// Ollama 连接设置类型
export interface OllamaConnectionSettings {
  host: string
  checkInterval?: number
  enableAutoCheck?: boolean
  showNotification?: boolean
}

// Ollama 连接状态类型
export interface OllamaConnectionStatus {
  connected: boolean
  version?: string
  error?: string
}

// Ollama API 客户端
export const ollamaApi = {
  /**
   * 获取 Ollama 连接设置
   */
  async getConnectionSettings(): Promise<OllamaConnectionSettings> {
    try {
      const response = await fetchWithRetry(
        `${API_URL}/ollama/settings`,
        {
          method: 'GET',
          headers: getAuthHeaders()
        }
      )
      return await response.json()
    } catch (error) {
      console.error('获取 Ollama 连接设置失败:', error)
      // 返回默认设置
      return {
        host: '',  // 不设置默认值，由后端提供
        checkInterval: 60,
        enableAutoCheck: true,
        showNotification: true
      }
    }
  },

  /**
   * 更新 Ollama 连接设置
   */
  async updateConnectionSettings(settings: Partial<OllamaConnectionSettings>): Promise<void> {
    const response = await fetchWithRetry(
      `${API_URL}/ollama/settings`,
      {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(settings)
      }
    )
    return await response.json()
  },

  /**
   * 更新检查设置
   */
  async updateCheckSettings(settings: {
    interval?: number
    enabled?: boolean
    notification?: boolean
  }): Promise<void> {
    const response = await fetchWithRetry(
      `${API_URL}/ollama/check-settings`,
      {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(settings)
      }
    )
    return await response.json()
  },

  /**
   * 检查 Ollama 连接状态
   */
  async checkConnection(): Promise<OllamaConnectionStatus> {
    try {
      const response = await fetchWithRetry(
        `${API_URL}/ollama/check`,
        {
          method: 'GET',
          headers: getAuthHeaders()
        }
      )
      const result = await response.json()
      console.log('Ollama 连接检查结果:', result)
      return result
    } catch (error: any) {
      console.error('检查 Ollama 连接失败:', error)
      return {
        connected: false,
        error: error.message || '未知错误'
      }
    }
  }
}
