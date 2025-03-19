import { defineStore } from 'pinia'
import { themeApi } from '@/api/themeApi'

// 检测系统主题色是否为深色
function isSystemDarkTheme(): boolean {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}

// 从本地存储获取主题设置
function getStoredTheme(): { isDark: boolean; themeSource: 'system' | 'light' | 'dark' } {
  try {
    const storedTheme = localStorage.getItem('kun-lab-theme')
    if (storedTheme) {
      return JSON.parse(storedTheme)
    }
  } catch (error) {
    console.error('读取主题设置失败:', error)
  }
  
  // 默认返回系统主题
  return {
    isDark: isSystemDarkTheme(),
    themeSource: 'system'
  }
}

// 使用选项式 API 定义 store
export const useThemeStore = defineStore('theme', {
  state: () => {
    const storedTheme = getStoredTheme()
    return {
      isDark: storedTheme.isDark,
      themeSource: storedTheme.themeSource as 'system' | 'light' | 'dark'
    }
  },

  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
      this.themeSource = this.isDark ? 'dark' : 'light'
      this.updateDocumentClass()
      this.saveThemeToStorage()
      this.saveThemeToDatabase()
    },

    setDark(value: boolean) {
      this.isDark = value
      this.themeSource = value ? 'dark' : 'light'
      this.updateDocumentClass()
      this.saveThemeToStorage()
      this.saveThemeToDatabase()
    },

    setTheme(theme: 'system' | 'light' | 'dark') {
      this.themeSource = theme
      
      if (theme === 'system') {
        this.isDark = isSystemDarkTheme()
      } else {
        this.isDark = theme === 'dark'
      }
      
      this.updateDocumentClass()
      this.saveThemeToStorage()
      this.saveThemeToDatabase()
    },

    updateDocumentClass() {
      if (this.isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },

    // 监听系统主题变化
    setupSystemThemeListener() {
      if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        
        const handleChange = (e: MediaQueryListEvent) => {
          if (this.themeSource === 'system') {
            this.isDark = e.matches
            this.updateDocumentClass()
            this.saveThemeToStorage()
            this.saveThemeToDatabase()
          }
        }
        
        // 添加监听器
        mediaQuery.addEventListener('change', handleChange)
      }
    },

    // 保存主题设置到本地存储
    saveThemeToStorage() {
      try {
        localStorage.setItem('kun-lab-theme', JSON.stringify({
          isDark: this.isDark,
          themeSource: this.themeSource
        }))
      } catch (error) {
        console.error('保存主题设置失败:', error)
      }
    },

    // 保存主题设置到数据库
    async saveThemeToDatabase() {
      try {
        const token = localStorage.getItem('token')
        if (!token) return // 如果用户未登录，不保存到数据库
        
        await themeApi.updateThemeSettings({
          theme_is_dark: this.isDark,
          theme_source: this.themeSource
        }, token)
      } catch (error) {
        console.error('保存主题设置到数据库失败:', error)
      }
    },

    // 从数据库加载主题设置
    async loadThemeFromDatabase() {
      try {
        const token = localStorage.getItem('token')
        if (!token) return // 如果用户未登录，不从数据库加载
        
        const settings = await themeApi.getThemeSettings(token)
        
        // 如果数据库中有主题设置，则使用数据库中的设置
        if (settings.theme_source !== undefined) {
          this.themeSource = settings.theme_source
          
          if (this.themeSource === 'system') {
            this.isDark = isSystemDarkTheme()
          } else if (settings.theme_is_dark !== undefined) {
            this.isDark = settings.theme_is_dark
          }
          
          this.updateDocumentClass()
          this.saveThemeToStorage()
        }
      } catch (error) {
        console.error('从数据库加载主题设置失败:', error)
      }
    }
  }
})