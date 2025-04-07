import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import './style.css'
import App from './App.vue'
import router from './router'
import { i18n, fetchLanguageSettings } from './i18n'
import { useThemeStore } from './stores/theme'
import { initOllamaService } from './services/ollamaService'
import axios from 'axios'
import { getAuthHeaders } from './api/config'

// 调试模式开关 - 通过环境变量控制
const DEBUG_MODE = import.meta.env.VITE_DEBUG_MODE === 'true';

// 将调试模式状态挂载到window对象上
(window as any).DEBUG_MODE = DEBUG_MODE;

// 在生产环境中根据DEBUG_MODE决定是否禁用控制台输出
if (process.env.NODE_ENV === 'production' && !DEBUG_MODE && typeof window.electronAPI === 'undefined') {
  // 保存原始的console方法
  const originalConsole = {
    log: console.log,
    debug: console.debug,
    info: console.info
  };
  
  // 添加全局方法用于启用日志
  (window as any).enableLogs = () => {
    console.log = originalConsole.log;
    console.debug = originalConsole.debug;
    console.info = originalConsole.info;
    console.log('日志输出已启用');
  };
  
  // 禁用日志方法
  console.log = () => {};
  console.debug = () => {};
  console.info = () => {};
}

// 设置axios全局请求拦截器，确保每个请求都有认证头
axios.interceptors.request.use(
  (config) => {
    // 获取认证头信息
    const authHeaders = getAuthHeaders()
    
    // 只在DEBUG_MODE为true时输出请求信息
    if (DEBUG_MODE) {
      console.log(`Axios请求: ${config.url}`, {
        hasAuthHeader: !!config.headers.Authorization,
        willAddAuth: !config.headers.Authorization && !!authHeaders.Authorization
      })
    }
    
    // 如果没有设置认证头，且有认证信息，则添加
    if (!config.headers.Authorization && authHeaders.Authorization) {
      config.headers.Authorization = authHeaders.Authorization
      
      if (DEBUG_MODE) {
        console.log(`已添加认证头到请求: ${config.url}`)
      }
    }
    
    return config
  },
  (error) => {
    console.error('Axios请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 添加响应拦截器
axios.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('Axios响应错误:', error.message || error)
    
    // 处理401错误（未认证）
    if (error.response && error.response.status === 401) {
      console.warn('收到401未认证响应，可能需要重新登录')
      
      // 获取当前页面路径
      const currentPath = window.location.hash.substring(1) // 去掉#号
      
      // 如果不是已经在登录页，则跳转到登录页
      if (currentPath !== '/login' && currentPath !== '/register') {
        console.log('即将跳转到登录页...')
        
        // 延迟跳转，给用户一些时间看到错误信息
        setTimeout(() => {
          window.location.href = '/#/login'
        }, 2000)
      }
    }
    
    return Promise.reject(error)
  }
)

// 导出是否是Electron环境的标志
export const isElectron = !!window.electronAPI;

// 应用初始化
async function initApp() {
  // 创建Pinia存储
  const pinia = createPinia()
  pinia.use(piniaPluginPersistedstate)
  
  // 创建Vue应用
  const app = createApp(App)
  
  // 使用插件
  app.use(pinia)
  app.use(router)
  app.use(i18n)
  
  // 初始化主题
  const themeStore = useThemeStore()
  themeStore.updateDocumentClass()
  themeStore.setupSystemThemeListener()
  
  try {
    await themeStore.loadThemeFromDatabase()
  } catch (error) {
    console.error('加载主题设置失败:', error)
  }
  
  // 初始化Ollama服务（如果可用）
  try {
    await initOllamaService()
  } catch (error) {
    console.error('初始化Ollama服务失败:', error)
  }
  
  // 获取语言设置
  try {
    await fetchLanguageSettings()
  } catch (error) {
    console.error('加载语言设置失败:', error)
  }
  
  // 挂载应用
  app.mount('#app')
}

// 加载应用
initApp().catch(console.error)
