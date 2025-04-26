/**
 * 思考过程管理器
 * 负责处理思考内容的存储、提取和计算
 */
import type { Message } from '@/types/index';

/**
 * 构建思考时间的存储键
 * @param message 消息对象
 * @param conversationId 对话ID
 * @returns 存储键
 */
function getThinkingTimeStorageKey(message: Message, conversationId: string): string {
  // 使用消息内容的前100个字符作为标识符
  const contentIdentifier = message.content ? message.content.substring(0, 100) : '';
  return `thinkTimes_${conversationId}_${contentIdentifier}`;
}

/**
 * 保存思考时间到localStorage
 * @param message 消息对象
 * @param conversationId 对话ID
 */
export function saveThinkingTimes(message: Message, conversationId: string): void {
  try {
    if (!message.metadata?.thinkTimes) return;
    
    // 构建存储键
    const storageKey = getThinkingTimeStorageKey(message, conversationId);
    
    // 保存思考时间数据
    localStorage.setItem(storageKey, JSON.stringify(message.metadata.thinkTimes));
  } catch (error) {
    console.error('保存思考时间到localStorage失败:', error);
  }
}

/**
 * 从localStorage加载思考时间
 * @param message 消息对象
 * @param conversationId 对话ID
 */
export function loadThinkingTimes(message: Message, conversationId: string): void {
  try {
    if (!conversationId) return;
    
    // 构建存储键
    const storageKey = getThinkingTimeStorageKey(message, conversationId);
    
    // 从localStorage获取数据
    const storedData = localStorage.getItem(storageKey);
    if (!storedData) return;
    
    // 解析数据并更新消息
    const thinkTimes = JSON.parse(storedData);
    if (Array.isArray(thinkTimes) && thinkTimes.length > 0) {
      // 只有当消息没有思考时间数据或数据不完整时才更新
      if (!message.metadata) {
        message.metadata = { thinkTimes };
      } else if (!message.metadata.thinkTimes || message.metadata.thinkTimes.length < thinkTimes.length) {
        message.metadata.thinkTimes = thinkTimes;
      }
    }
  } catch (error) {
    console.error('从localStorage加载思考时间失败:', error);
  }
}

/**
 * 开始记录思考时间
 * @param message 消息对象
 * @param conversationId 对话ID
 */
export function startThinkingTimer(message: Message, conversationId: string): void {
  // 初始化元数据
  if (!message.metadata) {
    message.metadata = { thinkTimes: [] };
  } else if (!message.metadata.thinkTimes) {
    message.metadata.thinkTimes = [];
  }
  
  // 记录开始时间
  message.currentThinkStartTime = Date.now();
  
  // 添加新的思考时间记录
  if (message.metadata && message.metadata.thinkTimes) {
    message.metadata.thinkTimes.push({
      startTime: message.currentThinkStartTime
    });
  }
  
  // 保存到localStorage
  saveThinkingTimes(message, conversationId);
}

/**
 * 结束记录思考时间
 * @param message 消息对象
 * @param conversationId 对话ID
 */
export function endThinkingTimer(message: Message, conversationId: string): void {
  if (!message.currentThinkStartTime) return;
  
  // 记录结束时间
  message.currentThinkEndTime = Date.now();
  
  // 确保元数据存在
  if (!message.metadata) {
    message.metadata = { thinkTimes: [] };
  } else if (!message.metadata.thinkTimes) {
    message.metadata.thinkTimes = [];
  }
  
  // 更新最后一条思考记录
  if (message.metadata && message.metadata.thinkTimes && message.metadata.thinkTimes.length > 0) {
    const lastThinkIndex = message.metadata.thinkTimes.length - 1;
    const currentThink = message.metadata.thinkTimes[lastThinkIndex];
    if (currentThink && !currentThink.endTime) {
      currentThink.endTime = message.currentThinkEndTime;
      currentThink.duration = message.currentThinkEndTime - currentThink.startTime;
    }
  }
  
  // 保存到localStorage
  saveThinkingTimes(message, conversationId);
  
  // 重置当前思考时间，为下一次思考做准备
  message.currentThinkStartTime = undefined;
  message.currentThinkEndTime = undefined;
}

/**
 * 更新消息的思考时间
 * @param message 消息对象
 * @param isThinking 是否正在思考
 * @param conversationId 对话ID
 * @returns 更新后的消息对象
 */
export function updateThinkingTime(message: Message, isThinking: boolean, conversationId: string): Message {
  // 如果不是思考状态，不处理
  if (!message.content?.includes('<think>')) {
    return message;
  }
  
  // 检查是否包含未闭合的<think>标签
  const hasOpenThink = message.content.includes('<think>');
  const hasCloseThink = message.content.includes('</think>');
  
  // 如果开始思考
  if (hasOpenThink && !hasCloseThink && isThinking) {
    // 如果之前没有记录开始时间
    if (!message.currentThinkStartTime) {
      startThinkingTimer(message, conversationId);
    }
  }
  
  // 如果思考结束
  if (hasOpenThink && hasCloseThink && message.currentThinkStartTime && !message.currentThinkEndTime) {
    endThinkingTimer(message, conversationId);
  }
  
  return message;
}

/**
 * 计算思考总时间（秒）
 * @param message 消息对象
 * @returns 思考总时间（秒）
 */
export function calculateThinkingTime(message: Message): number {
  if (!message.metadata?.thinkTimes?.length) {
    return 0;
  }
  
  // 如果正在思考中，计算当前思考时间
  if (message.currentThinkStartTime && !message.currentThinkEndTime) {
    const currentThinkingTime = Math.floor((Date.now() - message.currentThinkStartTime) / 1000);
    
    // 计算历史思考时间总和
    const historicalTime = message.metadata.thinkTimes.reduce((total, think) => {
      if (think.endTime) {
        return total + Math.floor((think.endTime - think.startTime) / 1000);
      }
      return total;
    }, 0);
    
    return historicalTime + currentThinkingTime;
  } 
  
  // 思考已结束，计算所有思考时间总和
  return message.metadata.thinkTimes.reduce((total, think) => {
    if (think.endTime) {
      return total + Math.floor((think.endTime - think.startTime) / 1000);
    }
    return total;
  }, 0);
}

/**
 * 获取格式化的思考时间
 * @param message 消息对象
 * @returns 格式化的思考时间字符串
 */
export function getFormattedThinkingTime(message: Message): string {
  const totalSeconds = calculateThinkingTime(message);
  
  if (totalSeconds < 60) {
    return `${totalSeconds}秒`;
  }
  
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  
  return `${minutes}分${seconds > 0 ? seconds + '秒' : ''}`;
} 