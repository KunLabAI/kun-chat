<template>
  <div :class="{ 'dark': themeStore.isDark }" class="h-screen">
    <!-- 在认证页面（登录/注册）显示标题栏，但在主布局页面不显示 -->
    <TitleBar v-if="isElectron && isAuthPage" class="electron-title-bar" />
    <RouterView />
    <Notification />
  </div>
</template>

<script setup lang="ts">
import { RouterView, useRouter, useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { onMounted, watch, ref, computed } from 'vue'
import Notification from '@/components/common/Notification.vue'
import TitleBar from '@/components/TitleBar.vue'
import '@/styles/variables.css'

const themeStore = useThemeStore()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isFirstVisit = ref(true)
const isElectron = ref(false)

// 判断当前是否为认证页面（登录/注册/忘记密码）
const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register' || route.path === '/forgot-password'
})

// 初始化主题和语言
onMounted(async () => {
  // 检测是否在 Electron 环境中
  isElectron.value = window && 'electronAPI' in window;
  
  // 从本地存储加载主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    themeStore.setDark(true)
  }

  // 初始化认证状态前，检查当前localStorage状态
  const lastLoggedUser = localStorage.getItem('kunlab_last_user')
  const token = lastLoggedUser 
    ? localStorage.getItem(`kunlab_user_token_${lastLoggedUser}`)
    : localStorage.getItem('token')
    
  console.log('App初始化时的认证状态:', {
    lastLoggedUser,
    hasToken: !!token,
    tokenFormat: token ? (token.startsWith('Bearer ') ? 'Bearer格式' : '原始格式') : '无token'
  })

  // 初始化认证状态
  await authStore.initAuth()
  console.log('认证状态初始化完成:', {
    isAuthenticated: authStore.isAuthenticated,
    hasUser: !!authStore.user.username
  })
  
  // 添加路由守卫，在用户首次登录或注册后显示 Ollama 连接状态通知
  router.afterEach((to, from) => {
    // 检查是否是首次访问应用
    if (isFirstVisit.value) {
      isFirstVisit.value = false
      return
    }
    
    // 检查是否是从登录/注册页面到主页面的导航
    if ((from.path === '/login' || from.path === '/register') && to.path === '/') {
      // 重新检查 Ollama 连接状态并显示通知
      import('@/services/ollamaService').then(async ({ initOllamaService, showOllamaStatusNotification }) => {
        try {
          // 重新检查连接状态
          await initOllamaService()
          // 延迟 1 秒显示通知，避免与其他通知重叠
          setTimeout(() => {
            showOllamaStatusNotification(true)
          }, 1000)
        } catch (error) {
          console.error('登录后检查 Ollama 连接失败:', error)
        }
      })
    }
  })
})

// 监听主题变化并保存到本地存储
watch(() => themeStore.isDark, (isDark) => {
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
})
</script>