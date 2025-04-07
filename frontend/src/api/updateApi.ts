/**
 * 应用更新 API
 */

// 导入类型定义
import type { UpdateStatus } from '../types/update';

// 定义 ElectronAPI 类型（内联定义，避免引用冲突）
type ElectronAPIType = {
  getBackendUrl: () => Promise<string>;
  minimizeWindow: () => Promise<void>;
  maximizeWindow: () => Promise<void>;
  closeWindow: () => Promise<void>;
  checkForUpdates: () => Promise<{ success: boolean; message?: string; error?: string }>;
  downloadUpdate: () => Promise<{ success: boolean; error?: string }>;
  installUpdate: () => Promise<{ success: boolean }>;
  getCurrentVersion: () => Promise<string>;
  onUpdateStatus: (callback: (status: UpdateStatus) => void) => () => void;
};

// 检查是否在 Electron 环境中
export const isElectron = (): boolean => {
  return window.electronAPI !== undefined;
};

// 获取当前版本
export const getCurrentVersion = async (): Promise<string> => {
  if (!isElectron()) {
    console.log('非 Electron 环境，无法获取版本信息');
    return '0.0.0';
  }
  
  try {
    // 使用更强的类型断言
    const api = window.electronAPI as ElectronAPIType;
    return await api.getCurrentVersion();
  } catch (error) {
    console.error('获取当前版本失败:', error);
    return '0.0.0';
  }
};

// 检查更新
export const checkForUpdates = async (): Promise<{ success: boolean; message?: string; error?: string }> => {
  if (!isElectron()) {
    console.log('非 Electron 环境，无法检查更新');
    return { success: false, message: '非 Electron 环境，无法检查更新' };
  }
  
  try {
    // 使用更强的类型断言
    const api = window.electronAPI as ElectronAPIType;
    return await api.checkForUpdates();
  } catch (error) {
    console.error('检查更新失败:', error);
    return { success: false, error: error instanceof Error ? error.message : String(error) };
  }
};

// 下载更新
export const downloadUpdate = async (): Promise<{ success: boolean; error?: string }> => {
  if (!isElectron()) {
    console.log('非 Electron 环境，无法下载更新');
    return { success: false, error: '非 Electron 环境，无法下载更新' };
  }
  
  try {
    // 使用更强的类型断言
    const api = window.electronAPI as ElectronAPIType;
    return await api.downloadUpdate();
  } catch (error) {
    console.error('下载更新失败:', error);
    return { success: false, error: error instanceof Error ? error.message : String(error) };
  }
};

// 安装更新
export const installUpdate = async (): Promise<{ success: boolean; error?: string }> => {
  if (!isElectron()) {
    console.log('非 Electron 环境，无法安装更新');
    return { success: false, error: '非 Electron 环境，无法安装更新' };
  }
  
  try {
    // 使用更强的类型断言
    const api = window.electronAPI as ElectronAPIType;
    return await api.installUpdate();
  } catch (error) {
    console.error('安装更新失败:', error);
    return { success: false, error: error instanceof Error ? error.message : String(error) };
  }
};

// 监听更新状态
export const onUpdateStatus = (callback: (status: UpdateStatus) => void): (() => void) => {
  if (!isElectron()) {
    console.log('非 Electron 环境，无法监听更新状态');
    return () => {};
  }
  
  // 使用更强的类型断言
  const api = window.electronAPI as ElectronAPIType;
  return api.onUpdateStatus(callback);
};
