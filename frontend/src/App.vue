<template>
  <div :class="{ 'dark': themeStore.isDark }" class="h-screen">
    <RouterView />
    <Notification />
  </div>
</template>

<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { onMounted, watch, ref } from 'vue'
import Notification from '@/components/common/Notification.vue'
import '@/styles/variables.css'

const themeStore = useThemeStore()
const router = useRouter()
const isFirstVisit = ref(true)

// 初始化主题和语言
onMounted(async () => {
  // 从本地存储加载主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    themeStore.setDark(true)
  }
  
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
