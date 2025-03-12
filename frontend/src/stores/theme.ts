import { defineStore } from 'pinia'

// 定义主题存储的类型
interface ThemeState {
  isDark: boolean
}

// 定义 store
export const useThemeStore = defineStore({
  id: 'theme',
  state: (): ThemeState => ({
    isDark: false
  }),

  actions: {
    toggleTheme(): void {
      this.isDark = !this.isDark
      this.updateDocumentClass()
    },

    setDark(value: boolean): void {
      this.isDark = value
      this.updateDocumentClass()
    },

    setTheme(theme: 'light' | 'dark'): void {
      this.isDark = theme === 'dark'
      this.updateDocumentClass()
    },

    updateDocumentClass(): void {
      if (this.isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }
})

// 在 main.ts 或其他初始化文件中处理持久化
// 例如：
// import { createPinia } from 'pinia'
// import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
// const pinia = createPinia()
// pinia.use(piniaPluginPersistedstate)