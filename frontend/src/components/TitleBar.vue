<template>
  <div class="title-bar" :class="{ 'dark': isDarkMode }" @mouseenter="showControls = true" @mouseleave="showControls = false">
    <div class="title-bar-drag-area">
    </div>
    <div class="window-controls" :class="{ 'visible': showControls }">
      <button class="window-control minimize" @click="minimizeWindow" title="最小化">
        <svg width="18" height="18" viewBox="0 0 12 12">
          <rect x="2" y="5.5" width="8" height="1" fill="currentColor" />
        </svg>
      </button>
      <button class="window-control maximize" @click="toggleMaximize" :title="isMaximized ? '还原' : '最大化'">
        <svg v-if="!isMaximized" width="18" height="18" viewBox="0 0 12 12">
          <rect x="2.5" y="2.5" width="7" height="7" stroke="currentColor" fill="none" />
        </svg>
        <svg v-else width="24" height="24" viewBox="0 0 12 12">
          <path d="M3.5,2.5 v5 h5 v-5 h-5 M2.5,4.5 v5 h5 v-5" stroke="currentColor" fill="none" />
        </svg>
      </button>
      <button class="window-control close" @click="closeWindow" title="关闭">
        <svg width="18" height="18" viewBox="0 0 12 12">
          <path d="M3,3 L9,9 M3,9 L9,3" stroke="currentColor" stroke-width="1.2" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();
const isDarkMode = ref(themeStore.isDark);
const isMaximized = ref(false);
const showControls = ref(false); // 控制窗口控制按钮的显示状态

// 监听主题变化
onMounted(() => {
  themeStore.$subscribe((mutation, state) => {
    isDarkMode.value = state.isDark;
  });
  
  // 检查窗口是否已最大化
  checkMaximizeState();
  
  // 监听窗口大小变化
  window.addEventListener('resize', checkMaximizeState);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMaximizeState);
});

// 检查窗口是否最大化
function checkMaximizeState() {
  // 在Electron环境中，我们可以通过比较窗口尺寸和屏幕尺寸来判断
  const isElectron = window && window.electronAPI;
  if (isElectron) {
    // 简单判断：如果窗口宽度等于屏幕宽度，则认为是最大化
    isMaximized.value = window.innerWidth >= window.screen.availWidth && 
                        window.innerHeight >= window.screen.availHeight - 10;
  }
}

// 最小化窗口
function minimizeWindow() {
  if (window.electronAPI) {
    window.electronAPI.minimizeWindow();
  }
}

// 切换最大化/还原窗口
function toggleMaximize() {
  if (window.electronAPI) {
    window.electronAPI.maximizeWindow();
    // 状态将通过resize事件更新
  }
}

// 关闭窗口
function closeWindow() {
  if (window.electronAPI) {
    window.electronAPI.closeWindow();
  }
}
</script>

<style scoped>
.title-bar {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--bg-color-light);
  -webkit-app-region: drag;
  user-select: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2;
  padding-left: 64px;
  opacity: 0;
}

.title-bar:hover {
  opacity: 1;
}

.dark .title-bar {
  background-color: var(--gray-1000);
  border-color: var(--gray-800);
}

.dark .title-bar:hover {
  opacity: 1;
}

.title-bar-drag-area {
  flex: 1;
  display: flex;
  align-items: center;
  padding-left: 8px;
}

.window-controls {
  display: flex;
  gap: 8px;
  -webkit-app-region: no-drag;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.window-controls.visible {
  opacity: 1;
}

.window-control {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  outline: none;
  cursor: pointer;
  color: var(--gray-600);
}

.window-control:hover {
  background-color: var(--gray-200);
}

.window-control.close:hover {
  background-color: #e81123;
  color: white;
}

.dark .window-control {
  color: var(--gray-400);
}

.dark .window-control:hover {
  background-color: var(--gray-800);
}

.dark .window-control.close:hover {
  background-color: #e81123;
  color: white;
}
</style>
