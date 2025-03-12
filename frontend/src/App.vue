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

<style lang="postcss">
/* 全局字体定义 */
:root {
  font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif,
    'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

/* 全局过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 主题相关的 CSS 变量 */
:root {
  /* 主题色系 - 使用紫色作为主色调 */
  --primary-50: #faf5ff;
  --primary-100: #f3e8ff;
  --primary-200: #e9d5ff;
  --primary-300: #d8b4fe;
  --primary-400: #c084fc;
  --primary-500: #a855f7;
  --primary-600: #9333ea;
  --primary-700: #7e22ce;
  --primary-800: #6b21a8;
  --primary-900: #581c87;

  /* 成功色系 */
  --success-50: #f0fdf4;
  --success-100: #dcfce7;
  --success-200: #bbf7d0;
  --success-300: #86efac;
  --success-400: #4ade80;
  --success-500: #22c55e;
  --success-600: #16a34a;
  --success-700: #15803d;
  --success-800: #166534;
  --success-900: #14532d;

  /* 灰度色系 */
  --gray-0: #ffffff;  /* 纯白 */
  --gray-50: #fafafa;   /* 最浅的灰，几乎是白色 */
  --gray-100: #f4f4f5;  /* 非常浅的灰，适合背景 */
  --gray-200: #e4e4e7;  /* 浅灰，适合边框和分割线 */
  --gray-300: #d4d4d8;  /* 中浅灰，适合不活跃的文本 */
  --gray-400: #a1a1aa;  /* 中灰，适合次要文本 */
  --gray-500: #71717a;  /* 标准灰，适合普通文本 */
  --gray-600: #52525b;  /* 中深灰，适合重要文本 */
  --gray-700: #3f3f46;  /* 深灰，适合标题 */
  --gray-800: #27272a;  /* 非常深的灰，适合深色背景 */
  --gray-900: #18181b;  /* 最深的灰，几乎是黑色 */
  --gray-1000: #0b0b0b;  /* 几乎黑 */

  /* 红色系 - 用于警告和危险操作 */
  --red-50: #fef2f2;    /* 最浅的红色 */
  --red-100: #fee2e2;   /* 非常浅的红色 */
  --red-200: #fecaca;   /* 浅红色 */
  --red-300: #fca5a5;   /* 中浅红色 */
  --red-400: #f87171;   /* 中红色 */
  --red-500: #ef4444;   /* 标准红色 */
  --red-600: #dc2626;   /* 中深红色，主要用于按钮 */
  --red-700: #b91c1c;   /* 深红色，用于悬停状态 */
  --red-800: #991b1b;   /* 非常深的红色 */
  --red-900: #7f1d1d;   /* 最深的红色 */

  /* 浅色主题默认值 */
  --bg-color: var(--gray-50);
  --bg-color-light: white;
  --bg-color-dark: var(--gray-100);
  --text-color: var(--gray-900);
  --text-color-light: var(--gray-700);
  --text-color-lighter: var(--gray-500);
  --border-color: var(--gray-200);
  --border-color-light: var(--gray-100);
  --link-color: var(--primary-600);
  --link-hover-color: var(--primary-700);
  --button-bg: var(--gray-100);
  --button-hover-bg: var(--gray-200);
  --button-border: var(--gray-300);
  --button-hover-border: var(--gray-400);
  --chat-user-avatar-bg: var(--gray-200);
  --chat-user-bubble-bg: var(--gray-200);  /* 用户消息气泡背景色 */
  --chat-user-bubble-text: var(--gray-900);  /* 用户消息文字颜色 */
  --chat-ai-bubble-bg: var(--bg-color);     /* AI消息气泡背景色 */
  --chat-ai-bubble-text: var(--text-color); /* AI消息文字颜色 */
  --chat-ai-bubble-border: var(--border-color); /* AI消息气泡边框颜色 */
}

/* 深色主题样式 */
.dark {
  color-scheme: dark;
  
  /* 深色主题变量覆盖 */
  --bg-color: var(--gray-900);
  --bg-color-light: var(--gray-800);
  --bg-color-dark: var(--gray-950);
  --text-color: var(--gray-50);
  --text-color-light: var(--gray-300);
  --text-color-lighter: var(--gray-400);
  --border-color: var(--gray-800);
  --border-color-light: var(--gray-700);
  --link-color: var(--primary-400);
  --link-hover-color: var(--primary-300);
  --button-bg: var(--gray-800);
  --button-hover-bg: var(--gray-700);
  --button-border: var(--gray-600);
  --button-hover-border: var(--gray-500);
  --chat-user-avatar-bg: var(--gray-700);
  --chat-user-bubble-bg: var(--gray-600);   /* 用户消息气泡背景色 */
  --chat-user-bubble-text: var(--gray-50);   /* 用户消息文字颜色 */
  --chat-ai-bubble-bg: var(--bg-color);      /* AI消息气泡背景色 */
  --chat-ai-bubble-text: var(--text-color);  /* AI消息文字颜色 */
  --chat-ai-bubble-border: var(--border-color); /* AI消息气泡边框颜色 */
}

/* 浅色主题样式 */
.bg-primary {
  background-color: var(--gray-500);
}

.text-primary {
  color: var(--gray-500);
}

/* 链接样式 */
a {
  color: var(--link-color);
}

a:hover {
  color: var(--link-hover-color);
}

/* 按钮样式 */
button:hover {
  border-color: var(--button-hover-border);
}

button:focus,
button:focus-visible {
  outline: 4px auto -webkit-focus-ring-color;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background-color: var(--gray-300);
  border-radius: 3px;
}

.dark ::-webkit-scrollbar-thumb {
  background-color: var(--gray-600);
}

/* 全局文本选择样式 */
::selection {
  background-color: var(--gray-100);
  color: var(--gray-900);
}

.dark ::selection {
  background-color: var(--gray-900);
  color: var(--gray-100);
}

/* 全局过渡效果 */
.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>
