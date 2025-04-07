/**
 * Electron API 类型定义
 */

// 导入更新状态类型
import { UpdateStatus } from './update';

interface ElectronAPI {
  // 获取后端服务地址
  getBackendUrl: () => Promise<string>;
  
  // 窗口控制
  minimizeWindow: () => Promise<void>;
  maximizeWindow: () => Promise<void>;
  closeWindow: () => Promise<void>;
  
  // 更新相关API
  checkForUpdates: () => Promise<{ success: boolean; message?: string; error?: string }>;
  downloadUpdate: () => Promise<{ success: boolean; error?: string }>;
  installUpdate: () => Promise<{ success: boolean }>;
  getCurrentVersion: () => Promise<string>;
  getElectronVersion: () => string;
  
  // 更新事件监听
  onUpdateStatus: (callback: (status: UpdateStatus) => void) => () => void;

  // GitHub 配置
  getGitHubConfig: () => { owner: string; repo: string; token: string };
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};
