// 动态获取API基础URL
const getApiBaseUrl = () => {
  // 根据当前访问的主机名动态确定
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000'
  } else {
    return `${protocol}//${hostname}:8000`
  }
}

// API 配置
export const API = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || getApiBaseUrl(),
  TIMEOUT: 30000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000,
} as const

// 本地存储键名
export const STORAGE_KEYS = {
  THEME: 'kunyu-theme',
  SETTINGS: 'kunyu-settings',
  PROMPTS: 'kunyu-prompts',
  CHAT_HISTORY: 'kunyu-chat-history',
} as const

// 默认设置
export const DEFAULT_SETTINGS = {
  theme: 'system',
  language: 'zh-CN',
  fontSize: 14,
  sendKey: 'enter',
  streamingResponse: true,
  showTimestamp: true,
} as const

// 主题配置
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  SYSTEM: 'system',
} as const

// 路由路径
export const ROUTES = {
  HOME: '/',
  CHAT: '/chat',
  MODELS: '/models',
  PROMPTS: '/prompts',
  HISTORY: '/history',
  SETTINGS: '/settings',
} as const

// 消息类型
export const MESSAGE_TYPES = {
  USER: 'user',
  ASSISTANT: 'assistant',
} as const

// 通知类型
export const NOTIFICATION_TYPES = {
  SUCCESS: 'SUCCESS',
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
} as const

// 通知持续时间（毫秒）
export const NOTIFICATION_DURATION = {
  SHORT: 3000,
  MEDIUM: 5000,
  LONG: 8000,
} as const

// 模型状态
export const MODEL_STATUS = {
  READY: 'ready',
  PULLING: 'pulling',
  ERROR: 'error',
} as const

// 文件大小限制（字节）
export const FILE_SIZE_LIMITS = {
  CHAT_HISTORY: 10 * 1024 * 1024, // 10MB
  PROMPT_EXPORT: 1 * 1024 * 1024, // 1MB
} as const

// 分页配置
export const PAGINATION = {
  PAGE_SIZE: 10,
  MAX_PAGES: 100,
} as const

// 防抖和节流配置（毫秒）
export const THROTTLE = {
  SCROLL: 100,
  RESIZE: 200,
  SAVE: 1000,
} as const

// 快捷键配置
export const SHORTCUTS = {
  NEW_CHAT: 'ctrl+n',
  SAVE: 'ctrl+s',
  SEND: 'ctrl+enter',
  CLEAR: 'ctrl+l',
  FOCUS: 'ctrl+/',
} as const
