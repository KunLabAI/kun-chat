/**
 * AI状态管理模块
 * 集中管理所有与AI交互相关的状态定义、类型和工具函数
 */

// 模型状态枚举
export enum ModelStatus {
  IDLE = 'idle',      // 空闲状态
  LOADING = 'loading', // 模型加载中
  READY = 'ready',    // 模型已就绪
  ERROR = 'error'     // 模型加载出错
}

// 生成状态枚举
export enum GenerationStatus {
  IDLE = 'idle',          // 空闲状态
  CONNECTING = 'connecting', // 正在连接
  GENERATING = 'generating', // 生成中
  PAUSED = 'paused',      // 已暂停
  COMPLETED = 'completed', // 已完成
  FAILED = 'failed',      // 生成失败
}

// 思考状态枚举
export enum ThinkingStatus {
  IDLE = 'idle',        // 非思考状态
  THINKING = 'thinking', // 思考中
  COMPLETED = 'completed' // 思考完成
}

// 工具调用状态枚举
export enum ToolStatus {
  IDLE = 'idle',       // 未调用工具
  CALLING = 'calling', // 工具调用中
  WEB_SEARCH = 'web_search', // 网页搜索
  MCP = 'mcp',        // MCP操作
  COMPLETED = 'completed', // 工具调用完成
  FAILED = 'failed'    // 工具调用失败
}

// WebSocket连接状态
export type WebSocketConnectionState = 'connecting' | 'open' | 'closed' | 'error' | null;

// 统一AI状态接口
export interface AiStatusState {
  model: ModelStatus;
  generation: GenerationStatus;
  thinking: ThinkingStatus;
  tool: ToolStatus;
  activeMessage: string | null;
  failureReason: string | null;
  loadingProgress: number;
  websocketState: WebSocketConnectionState;
  webSearchEnabled: boolean; // 是否启用了网页搜索
}

// 思考时间记录结构
export interface ThinkTimeEntry {
  startTime: number;
  endTime?: number;
  duration?: number;
}

// 消息元数据结构
export interface MessageMetadata {
  thinkTimes: ThinkTimeEntry[];
  [key: string]: any;
}

// 提取思考过程内容
export function extractThinkContent(content: string): string {
  if (!content) return '';
  const match = content.match(/<think>([\s\S]*?)(?:<\/think>|$)/);
  return match ? match[1].trim() : '';
}

// 提取最终回答内容
export function extractFinalContent(content: string): string {
  if (!content) return content;
  
  // 如果没有结束标签，说明还在思考中，不显示最终内容
  if (content.includes('<think>') && !content.includes('</think>')) {
    return '';
  }
  
  return content.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
}

// 检查内容是否包含思考过程
export function hasThinkingContent(content: string): boolean {
  if (!content) return false;
  
  // 如果包含未闭合的think标签，显示思考过程
  if (content.includes('<think>') && !content.includes('</think>')) {
    return true;
  }
  
  // 如果思考过程已完成，检查内容是否为空
  const thinkMatch = content.match(/<think>([\s\S]*?)<\/think>/);
  return Boolean(thinkMatch && thinkMatch[1].trim().length > 0);
}

// 格式化思考内容，处理换行和缩进
export function formatThinkContent(content: string): string {
  return content
    .split('\n')
    .map(line => line.trim())
    .filter(line => line)
    .join('\n');
}

// 获取工具状态文本
export function getToolStatusText(toolStatus: ToolStatus): string {
  switch (toolStatus) {
    case ToolStatus.WEB_SEARCH:
      return '正在搜索网络...';
    case ToolStatus.MCP:
      return '正在执行MCP操作...';
    case ToolStatus.CALLING:
      return '正在调用工具...';
    default:
      return '工具调用中...';
  }
}

// 默认的AI状态
export const DEFAULT_AI_STATUS: AiStatusState = {
  model: ModelStatus.IDLE,
  generation: GenerationStatus.IDLE,
  thinking: ThinkingStatus.IDLE,
  tool: ToolStatus.IDLE,
  activeMessage: null,
  failureReason: null,
  loadingProgress: 0,
  websocketState: null,
  webSearchEnabled: false
};

/**
 * 模型状态管理辅助函数
 * 提供一组函数用于处理模型状态的转换
 */

// 已加载模型的缓存，用于跟踪哪些模型已经加载
let loadedModels: Set<string> = new Set();

/**
 * 检查模型是否已加载
 * @param model 模型名称
 * @returns 模型是否已加载
 */
export function isModelLoaded(model: string): boolean {
  return loadedModels.has(model);
}

/**
 * 标记模型为已加载状态
 * @param model 模型名称
 */
export function markModelAsLoaded(model: string): void {
  loadedModels.add(model);
}

/**
 * 清除已加载模型缓存
 */
export function clearLoadedModels(): void {
  loadedModels.clear();
}

/**
 * 获取模型加载状态更新
 * @param status 模型加载状态
 * @param progress 加载进度
 * @param message 错误消息（如果有）
 * @returns 状态更新对象
 */
export function getModelStatusUpdate(status: string, progress: number = 0, message?: string): Partial<AiStatusState> {
  switch (status) {
    case 'loading':
      return {
        model: ModelStatus.LOADING,
        loadingProgress: progress,
        generation: GenerationStatus.CONNECTING,
        failureReason: null
      };
    case 'ready':
      return {
        model: ModelStatus.READY,
        loadingProgress: 100,
        generation: GenerationStatus.GENERATING,
        failureReason: null
      };
    case 'error':
      return {
        model: ModelStatus.ERROR,
        generation: GenerationStatus.FAILED,
        failureReason: message || '模型加载失败'
      };
    default:
      return {};
  }
}