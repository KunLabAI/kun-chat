import { API_URL, getAuthHeaders, fetchWithRetry, handleApiResponse } from './config'

// Tavily搜索API接口
export const toolsApi = {
  // 获取Tavily API设置
  getTavilySettings: async (): Promise<any> => {
    const response = await fetchWithRetry(`${API_URL}/tavily/settings`, {
      headers: getAuthHeaders()
    })
    return handleApiResponse<any>(response)
  },

  // 更新Tavily API设置
  updateTavilySettings: async (settings: { 
    api_key?: string,
    search_depth?: string,
    include_domains?: string[] | string,
    exclude_domains?: string[] | string
  }): Promise<any> => {
    const response = await fetchWithRetry(`${API_URL}/tavily/settings`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(settings)
    })
    return handleApiResponse<any>(response)
  },

  // 测试Tavily API连接
  testTavilyConnection: async (): Promise<any> => {
    const response = await fetchWithRetry(`${API_URL}/tavily/test`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse<any>(response)
  },

  // 执行Tavily搜索
  search: async (
    query: string,
    options: {
      search_depth?: string,
      max_results?: number,
      include_answer?: boolean,
      include_domains?: string[] | string,
      exclude_domains?: string[] | string
    } = {}
  ): Promise<any> => {
    const params = new URLSearchParams({
      query
    })
    
    if (options.search_depth) {
      params.append('search_depth', options.search_depth)
    }
    
    if (options.max_results !== undefined) {
      params.append('max_results', options.max_results.toString())
    }
    
    if (options.include_answer !== undefined) {
      params.append('include_answer', options.include_answer.toString())
    }
    
    if (options.include_domains) {
      if (Array.isArray(options.include_domains)) {
        params.append('include_domains', options.include_domains.join(','))
      } else {
        params.append('include_domains', options.include_domains)
      }
    }
    
    if (options.exclude_domains) {
      if (Array.isArray(options.exclude_domains)) {
        params.append('exclude_domains', options.exclude_domains.join(','))
      } else {
        params.append('exclude_domains', options.exclude_domains)
      }
    }
    
    const response = await fetchWithRetry(`${API_URL}/tavily/search?${params.toString()}`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleApiResponse<any>(response)
  }
}
