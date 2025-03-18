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

// API配置
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || getApiBaseUrl()
export const API_URL = `${API_BASE_URL}/api`

// 获取认证头
export const getAuthHeaders = () => {
  // 先从localStorage中获取token
  let token = localStorage.getItem('token')
  
  // 基础头信息
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  }
  
  // 如果有token，添加到头信息中
  if (token) {
    // 确保token以Bearer开头
    if (!token.startsWith('Bearer ')) {
      token = `Bearer ${token}`
    }
    headers['Authorization'] = token
  }
  
  return headers
}

// 请求重试配置
export const RETRY_CONFIG = {
  maxRetries: 3,         // 最大重试次数
  retryDelay: 1000,      // 重试间隔（毫秒）
  shouldRetry: (error: any) => {
    // 判断是否应该重试
    return error instanceof TypeError && error.message === 'Failed to fetch'
  }
}

// 带重试的 fetch 函数
export async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retryCount = 0
): Promise<Response> {
  try {
    const response = await fetch(url, options)
    if (!response.ok) {
      // 尝试读取响应内容
      let errorDetail = '';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        // 如果无法解析为 JSON，尝试读取文本
        try {
          errorDetail = await response.text();
        } catch (textError) {
          errorDetail = `状态码: ${response.status}`;
        }
      }
      
      const error = new Error(`HTTP error! status: ${response.status}, detail: ${errorDetail}`) as any;
      error.status = response.status;
      error.detail = errorDetail;
      throw error;
    }
    return response
  } catch (error) {
    if (retryCount < RETRY_CONFIG.maxRetries && RETRY_CONFIG.shouldRetry(error)) {
      console.log(`请求失败，${retryCount + 1}秒后重试...`)
      await new Promise(resolve => setTimeout(resolve, RETRY_CONFIG.retryDelay))
      return fetchWithRetry(url, options, retryCount + 1)
    }
    throw error
  }
}

// 统一的错误处理
export async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`请求失败: ${response.status} - ${errorText}`)
  }
  return await response.json()
}
