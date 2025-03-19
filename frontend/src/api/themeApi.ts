import axios from 'axios'
import { API_URL } from './config'

// 主题设置类型
export interface ThemeSettings {
  theme_is_dark?: boolean
  theme_source?: 'system' | 'light' | 'dark'
}

// 主题API客户端
export const themeApi = {
  // 获取主题设置
  async getThemeSettings(token: string): Promise<ThemeSettings> {
    try {
      const response = await axios.get(`${API_URL}/theme/settings`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        withCredentials: true
      })
      return response.data
    } catch (error) {
      console.error('获取主题设置失败:', error)
      throw error
    }
  },

  // 更新主题设置
  async updateThemeSettings(settings: ThemeSettings, token: string): Promise<any> {
    try {
      const response = await axios.post(
        `${API_URL}/theme/settings`,
        settings,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          withCredentials: true
        }
      )
      return response.data
    } catch (error) {
      console.error('更新主题设置失败:', error)
      throw error
    }
  }
}
