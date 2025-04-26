

// 聊天相关类型
export interface Message {
  id: string
  role: 'system' | 'user' | 'assistant'
  content: string
  timestamp: string
  model?: string
  image?: string
  images?: string | string[]
  image_path?: string
  pdf?: PDFData
  document?: DocumentData
  showDocument?: boolean
  metadata?: {
    thinkTimes?: Array<{
      startTime: number
      endTime?: number
      duration?: number
    }>
    [key: string]: any
  }
  currentThinkStartTime?: number
  currentThinkEndTime?: number
  showThinking?: boolean
  preparing?: boolean  // 标记消息是否正在准备中，尚未添加到消息列表
}

export interface PDFData {
  name: string
  title: string;
  author: string;
  content: string;
} 

export interface DocumentData {
  name: string
  content: string
  type: string
}

export interface Chat {
  id: string
  title: string
  messages: Message[]
  model: string
  createdAt: string
  updatedAt: string
}

// 提示词相关类型
export interface Prompt {
  id: string
  title: string
  content: string
  tags: string[]
  createdAt: string
  updatedAt: string
}

// 用户设置相关类型
export interface Settings {
  theme: 'light' | 'dark' | 'system'
  language: string
  fontSize: number
  sendKey: 'enter' | 'ctrl+enter'
  streamingResponse: boolean
  showTimestamp: boolean
}

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
}

// 通知相关类型
export interface Notification {
  id: string
  type: 'success' | 'info' | 'warning' | 'error'
  title: string
  message: string
  duration?: number
}

// 对话相关类型
export interface Conversation {
  conversation_id: string
  title: string
  model: string | null
  created_at: string
  updated_at: string
  messages: Message[]
}

export interface ConversationCreate {
  title?: string
  model?: string
}

export interface ConversationUpdate {
  messages: Message[]
  model?: string
}

export interface SendMessagePayload {
  content: string
  image?: string
  pdf?: PDFData
  document?: DocumentData
  web_search?: boolean
}

export interface ChatMessage {
  role: string
  content: string
  image?: string
  document?: DocumentData | string
}

export interface ProcessedChatMessage {
  role: string
  content: string
  images?: string[]
  document?: DocumentData | string
}

export interface FileUpload {
  id: string
  filename: string
  size: number
  type: string
  url: string
}

export interface PDFPage {
  page_number: number
  content: string
  images: string[]
}

export interface PDFResponse {
  pages: PDFPage[]
  total_pages: number
  metadata: {
    format: string
    title: string
    author: string
    subject: string
    keywords: string
    creator: string
    producer: string
    creationDate: string
    modDate: string
    trapped: string
    encryption: null | any
  }
  total_images: number
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: string
  [key: string]: any
}
