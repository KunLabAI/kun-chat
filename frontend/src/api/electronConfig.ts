// Electron 环境下的 API 配置
import { API_BASE_URL } from './config';

// 检测是否在 Electron 环境中
export const isElectron = () => {
  // 检查是否存在 electronAPI 对象
  return window && 'electronAPI' in window;
};

// 获取 Electron 环境下的后端 URL
export async function getElectronBackendUrl(): Promise<string | null> {
  try {
    if (isElectron() && window.electronAPI) {
      // 通过 Electron IPC 获取后端 URL
      const url = await window.electronAPI.getBackendUrl();
      console.log('从 Electron 获取的后端 URL:', url);
      
      // 确保 URL 是有效的
      if (url && typeof url === 'string' && url.startsWith('http')) {
        return url;
      } else {
        console.warn('从 Electron 获取的后端 URL 无效:', url);
        console.warn('将使用默认 URL:', 'http://localhost:8000');
        return 'http://localhost:8000';
      }
    }
  } catch (error) {
    console.error('获取 Electron 后端 URL 失败:', error);
    console.warn('将使用默认 URL:', 'http://localhost:8000');
    return 'http://localhost:8000';
  }
  return null;
}

// 获取适用于当前环境的 API 基础 URL
export async function getEnvironmentApiBaseUrl(): Promise<string> {
  // 尝试从 Electron 获取
  try {
    const electronBackendUrl = await getElectronBackendUrl();
    if (electronBackendUrl) {
      console.log('使用 Electron 提供的后端 URL:', electronBackendUrl);
      return electronBackendUrl;
    }
  } catch (error) {
    console.error('获取 Electron 后端 URL 时出错:', error);
  }
  
  // 回退到常规配置
  console.log('使用常规配置的后端 URL:', API_BASE_URL);
  return API_BASE_URL;
}

// 获取适用于当前环境的 API URL
export async function getEnvironmentApiUrl(): Promise<string> {
  const baseUrl = await getEnvironmentApiBaseUrl();
  // 直接返回基础URL，让config.ts处理/api前缀
  console.log('最终使用的 API URL:', baseUrl);
  return baseUrl;
}

// 为 TypeScript 添加 Electron API 类型定义
declare global {
  interface Window {
    electronAPI?: {
      getBackendUrl: () => Promise<string>;
      minimizeWindow: () => Promise<void>;
      maximizeWindow: () => Promise<void>;
      closeWindow: () => Promise<void>;
    };
  }
}
