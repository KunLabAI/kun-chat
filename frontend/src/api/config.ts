// 动态获取API基础URL
const getApiBaseUrl = () => {
  // 检查是否在Electron环境中
  const isElectron = window && 'electronAPI' in window;
  
  if (isElectron) {
    // 在Electron环境中，使用固定的后端地址
    return 'http://localhost:8000';
  }
  
  // 在浏览器环境中，根据当前访问的主机名动态确定
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  } else {
    return `${protocol}//${hostname}:8000`;
  }
}

// API配置
// API_BASE_URL 不包含 /api 前缀
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || getApiBaseUrl();
// API_URL 包含 /api 前缀
export const API_URL = `${API_BASE_URL}/api`;

// 导出获取API URL的异步函数
export async function getApiUrl() {
  // 尝试从electronConfig中获取
  try {
    // 检查是否在Electron环境中
    const isElectron = window && 'electronAPI' in window;
    
    if (isElectron) {
      console.log('检测到Electron环境，尝试获取Electron API URL');
      try {
        const { getEnvironmentApiUrl } = await import('./electronConfig');
        const baseUrl = await getEnvironmentApiUrl();
        
        if (baseUrl) {
          // 统一在这里添加/api前缀
          const apiUrl = `${baseUrl}/api`;
          console.log('成功获取Electron环境API URL:', apiUrl);
          return apiUrl;
        } else {
          console.warn('无法从Electron获取API URL，使用默认配置');
        }
      } catch (electronError) {
        console.error('获取Electron环境API URL失败:', electronError);
      }
    }
  } catch (error) {
    console.error('检测Electron环境失败:', error);
  }
  
  // 回退到默认API URL
  console.log('使用默认API URL配置:', API_URL);
  return API_URL;
}

// 定义一个辅助函数来检查是否应该输出日志
function shouldLog(): boolean {
  // 使用全局DEBUG_MODE变量
  return (window as any).DEBUG_MODE === true;
}

// 条件日志函数
function debugLog(...args: any[]): void {
  if (shouldLog()) {
    console.log(...args);
  }
}

// 获取认证头
export const getAuthHeaders = () => {
  // 使用新的存储方式获取token
  const lastLoggedUser = localStorage.getItem('kunlab_last_user')
  let token = null
  
  if (lastLoggedUser) {
    token = localStorage.getItem(`kunlab_user_token_${lastLoggedUser}`)
    debugLog('从多账户存储中获取token:', lastLoggedUser, !!token)
  } 
  
  // 如果没有获取到token，尝试从旧版存储中获取
  if (!token) {
    token = localStorage.getItem('token')
    debugLog('从旧版存储中获取token:', !!token)
  }
  
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
    debugLog('添加认证头:', headers['Authorization'] ? '已添加' : '未添加')
  } else {
    debugLog('警告: 未找到有效的token')
  }
  
  return headers
}

// 请求重试配置
export const RETRY_CONFIG = {
  maxRetries: 3,         // 最大重试次数
  retryDelay: 1000,      // 重试间隔（毫秒）
  shouldRetry: (error: any) => {
    // 判断是否应该重试
    // 扩展重试条件：包括网络错误和401错误（可能是token过期）
    return (error instanceof TypeError && error.message === 'Failed to fetch') || 
           (error.status === 401 && error.detail?.includes('Could not validate credentials'))
  }
}

// 带重试的 fetch 函数
export async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retryCount = 0
): Promise<Response> {
  try {
    debugLog(`发送请求: ${url}, 重试次数: ${retryCount}`)
    
    // 检查认证头
    if (options.headers && (options.headers as any)['Authorization']) {
      debugLog(`请求包含认证头: ${url}`)
    } else {
      debugLog(`请求无认证头: ${url}`)
      
      // 尝试再次获取token并添加认证头
      const headers = getAuthHeaders()
      options.headers = { ...options.headers, ...headers }
      debugLog(`重新获取认证头后的状态: ${!!headers['Authorization']}`)
    }
    
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
      
      console.error(`HTTP错误: ${response.status}, 详情: ${errorDetail}`)
      
      // 处理认证错误
      if (response.status === 401) {
        console.warn('认证失败，尝试刷新token...')
        
        // 尝试从localStorage重新获取token
        const lastLoggedUser = localStorage.getItem('kunlab_last_user')
        if (lastLoggedUser) {
          const token = localStorage.getItem(`kunlab_user_token_${lastLoggedUser}`)
          debugLog(`重新获取token: ${!!token}`)
          
          if (token) {
            // 更新认证头并重试
            options.headers = {
              ...options.headers,
              'Authorization': token.startsWith('Bearer ') ? token : `Bearer ${token}`
            }
            
            // 如果是第一次重试，尝试再次发送请求
            if (retryCount === 0) {
              debugLog('使用新token重试请求')
              return fetchWithRetry(url, options, retryCount + 1)
            }
          }
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
      debugLog(`请求失败，${retryCount + 1}秒后重试...`)
      await new Promise(resolve => setTimeout(resolve, RETRY_CONFIG.retryDelay))
      return fetchWithRetry(url, options, retryCount + 1)
    }
    throw error
  }
}

/**
 * 处理API响应
 * @param response Fetch API响应对象
 * @returns 解析后的响应数据
 * @throws 如果响应不成功，抛出带有状态码和详细信息的错误
 */
export async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetail = '';
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || JSON.stringify(errorData);
    } catch (e) {
      try {
        errorDetail = await response.text();
      } catch (textError) {
        errorDetail = `状态码: ${response.status}`;
      }
    }
    
    console.error(`API响应错误: ${response.status}, 详情: ${errorDetail}`);
    
    // 如果是401错误，可能是token过期，尝试自动跳转到登录页
    if (response.status === 401) {
      console.warn('认证失败，即将跳转到登录页...');
      
      // 延迟2秒后跳转，给用户一些时间看到错误信息
      setTimeout(() => {
        window.location.href = '/#/login';
      }, 2000);
    }
    
    const error = new Error(`HTTP error! status: ${response.status}, detail: ${errorDetail}`) as any;
    error.status = response.status;
    error.detail = errorDetail;
    throw error;
  }
  
  return await response.json() as T;
}
