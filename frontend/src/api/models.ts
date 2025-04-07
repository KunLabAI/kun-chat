// frontend/src/api/models.ts

import { Model, ModelInfo } from '../types/models'
import axios from 'axios';
import { API_URL, getAuthHeaders } from './config';

const API_BASE_URL = API_URL;

// 自定义错误类
export class ModelApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'ModelApiError'
    this.status = status
  }
}

// 统一的错误处理函数
async function handleApiResponse<T>(response: any): Promise<T> {
  if (!response.data) {
    const errorText = response.statusText
    throw new ModelApiError(
      `HTTP error! status: ${response.status}, message: ${errorText}`,
      response.status
    )
  }
  return response.data;
}

interface CreateModelData {
  name: string;
  modelfile: string;
  parameters?: {
    temperature?: number;
    num_ctx?: number;
    top_k?: number;
    top_p?: number;
    repeat_last_n?: number;
    repeat_penalty?: number;
    mirostat?: number;
    mirostat_eta?: number;
    mirostat_tau?: number;
  };
  force?: boolean;
}

export const modelApi = {
  async getModelList(): Promise<Model[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/models/list`, {
        headers: getAuthHeaders()
      })
      return await handleApiResponse<Model[]>(response)
    } catch (error) {
      console.error('Error fetching models:', error)
      throw error
    }
  },

  async getModelInfo(modelId: number): Promise<ModelInfo> {
    try {
      const response = await axios.get(`${API_BASE_URL}/models/${modelId}`, {
        headers: getAuthHeaders()
      })
      return await handleApiResponse<ModelInfo>(response)
    } catch (error) {
      console.error('API: 获取模型详情失败:', error)
      throw error
    }
  },

  async checkModelExists(modelName: string): Promise<boolean> {
    try {
      const response = await axios.get(`${API_BASE_URL}/models/exists/${encodeURIComponent(modelName)}`, {
        headers: getAuthHeaders()
      })
      return await handleApiResponse<boolean>(response)
    } catch (error) {
      console.error('Error checking model existence:', error)
      return false
    }
  },

  async updateModelOptions(modelId: number, options: any): Promise<Model> {
    const response = await axios.put(`${API_BASE_URL}/models/${modelId}/options`, options, {
      headers: getAuthHeaders()
    })
    return await handleApiResponse<Model>(response)
  },

  async updateModelDisplayName(modelId: number, displayName: string): Promise<Model> {
    const response = await axios.put(`${API_BASE_URL}/models/${modelId}/display-name`, { display_name: displayName }, {
      headers: getAuthHeaders()
    })
    return await handleApiResponse<Model>(response)
  },

  pullModel(modelName: string, force: boolean = false): EventSource {
    // 获取认证头
    const authHeaders = getAuthHeaders();
    const authToken = authHeaders.Authorization || '';
    
    // 为EventSource添加认证信息
    const url = `${API_BASE_URL}/models/pull/${encodeURIComponent(modelName)}?force=${force}&token=${encodeURIComponent(authToken.replace('Bearer ', ''))}`;
    const eventSource = new EventSource(url)
    
    // 添加错误处理
    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error)
    }
    
    return eventSource
  },

  async cancelPull(modelName: string): Promise<void> {
    try {
      const response = await axios.post(`${API_BASE_URL}/models/pull/${encodeURIComponent(modelName)}/cancel`, {}, {
        headers: getAuthHeaders()
      })
      
      if (!response.data) {
        const errorText = response.statusText
        throw new ModelApiError(
          `取消下载失败: ${errorText}`,
          response.status
        )
      }
    } catch (error) {
      console.error('Error cancelling model pull:', error)
      throw error
    }
  },

  async deleteModel(modelId: number): Promise<{ status: string, message: string }> {
    const response = await axios.delete(`${API_BASE_URL}/models/${modelId}`, {
      headers: getAuthHeaders()
    })
    return await handleApiResponse<{ status: string, message: string }>(response)
  },

  async getModels(): Promise<Model[]> {
    const response = await axios.get(`${API_BASE_URL}/models`, {
      headers: getAuthHeaders()
    })
    return await handleApiResponse<Model[]>(response)
  },

  async getFavoriteModels(username: string): Promise<Model[]> {
    const response = await axios.get(`${API_BASE_URL}/models/favorites/${username}`, {
      headers: getAuthHeaders()
    })
    return await handleApiResponse<Model[]>(response)
  },

  async checkFavoriteStatus(modelId: number, username: string): Promise<boolean> {
    try {
      if (!username) {
        return false;
      }
      const response = await axios.get(`${API_BASE_URL}/models/${modelId}/favorite/${username}`, {
        headers: getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('检查收藏状态失败:', error);
      return false;
    }
  },

  async toggleFavorite(modelId: number, username: string): Promise<{ is_favorited: boolean, message: string }> {
    try {
      if (!username) {
        throw new Error('用户未登录');
      }
      const response = await axios.post(`${API_BASE_URL}/models/${modelId}/favorite/${username}`, {}, {
        headers: getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('切换收藏状态失败:', error);
      throw error;
    }
  },

  async createModel(data: CreateModelData): Promise<Model> {
    try {
      const response = await axios.post(`${API_BASE_URL}/models/custom`, data, {
        headers: getAuthHeaders()
      })
      return await handleApiResponse<Model>(response)
    } catch (error) {
      console.error('Error creating model:', error)
      throw error
    }
  }
}