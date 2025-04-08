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

// 初始设置主题，避免闪烁
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {

  document.documentElement.classList.add('dark');
}

// 在生产环境中根据DEBUG_MODE决定是否禁用控制台输出
if (process.env.NODE_ENV === 'production' && !DEBUG_MODE && typeof window.electronAPI === 'undefined') {

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
    
    // 检查请求配置是否设置了跳过错误处理
    if (error.config?.skipErrorHandler) {
      return Promise.reject(error);
    }
    
    // 处理401错误（未认证）
    if (error.response && error.response.status === 401) {
      console.warn('收到401未认证响应，可能需要重新登录')
      
      // 如果设置了跳过认证刷新，则不处理
      if (error.config?.skipAuthRefresh) {
        return Promise.reject(error);
      }
      
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
  
  // 初始化主题 - 优先级最高，防止闪烁
  const themeStore = useThemeStore()
  
  // 立即更新文档类，确保与前面的预加载样式一致
  themeStore.updateDocumentClass()
  themeStore.setupSystemThemeListener()
  
  try {
    // 尝试加载保存的主题设置，但不改变当前外观
    // 因为我们已经在页面初始化时应用了暗色主题
    await themeStore.loadThemeFromDatabase()
  } catch (error) {
    console.error('加载主题设置失败:', error)
  }
  
  // 先挂载应用，保证UI体验的流畅性
  app.mount('#app')
  
  // 在应用挂载后执行其他初始化操作
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
}

// 加载应用
initApp().catch(console.error)
