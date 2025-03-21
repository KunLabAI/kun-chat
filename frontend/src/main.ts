import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import './style.css'
import App from './App.vue'
import router from './router'
import { i18n, fetchLanguageSettings } from './i18n'
import { useThemeStore } from './stores/theme'

// 初始化 Pinia
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// 初始化应用
const app = createApp(App)

app.use(pinia)
app.use(i18n)

// 获取语言设置并初始化
console.log('正在初始化应用，加载语言设置...')
fetchLanguageSettings().then(async () => {
  console.log('语言设置加载完成，挂载应用')
  
  // 初始化主题
  const themeStore = useThemeStore()
  themeStore.updateDocumentClass()
  themeStore.setupSystemThemeListener()
  
  // 从数据库加载主题设置
  try {
    await themeStore.loadThemeFromDatabase()
    console.log('从数据库加载主题设置完成')
  } catch (error) {
    console.error('从数据库加载主题设置失败:', error)
  }
  
  // 挂载应用
  app.use(router).mount('#app')
}).catch(async error => {
  console.error('初始化语言设置失败:', error)
  // 即使语言设置初始化失败，也继续挂载应用
  console.log('尽管语言设置加载失败，仍然挂载应用')
  
  // 初始化主题
  const themeStore = useThemeStore()
  themeStore.updateDocumentClass()
  themeStore.setupSystemThemeListener()
  
  // 从数据库加载主题设置
  try {
    await themeStore.loadThemeFromDatabase()
    console.log('从数据库加载主题设置完成')
  } catch (error) {
    console.error('从数据库加载主题设置失败:', error)
  }
  
  app.use(router).mount('#app')
})
