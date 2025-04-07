<template>
  <div class="layout-container">
    <!-- 仅在 Electron 环境中显示自定义标题栏 -->
    <TitleBar v-if="isElectron" class="electron-title-bar" />
    
    <Notification />
    <Sidebar />
    <main class="main-content" :class="{ 'electron-mode': isElectron }">
      <div class="responsive-container">
        <slot></slot>
        <slot name="preview-panel"></slot>
      </div>
      <slot name="drawer"></slot>
    </main>
  </div>
</template>

<style>
@import '@/styles/MainLayout.css';
</style>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import Notification from '@/components/common/Notification.vue'
import TitleBar from '@/components/TitleBar.vue'

// 检测是否在 Electron 环境中
const isElectron = ref(false)

onMounted(() => {
  // 检查是否在 Electron 环境中
  isElectron.value = window && 'electronAPI' in window
})
</script>
