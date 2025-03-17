<template>
  <div :class="{ 'dark': themeStore.isDark }" class="h-screen">
    <RouterView />
    <Notification />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { onMounted, watch } from 'vue'
import Notification from '@/components/common/Notification.vue'
import '@/styles/variables.css'

const themeStore = useThemeStore()

// 初始化主题和语言
onMounted(async () => {
  // 从本地存储加载主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    themeStore.setDark(true)
  }
})

// 监听主题变化并保存到本地存储
watch(() => themeStore.isDark, (isDark) => {
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
})
</script>
