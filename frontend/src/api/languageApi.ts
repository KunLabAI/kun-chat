/**
 * 语言设置API
 */
import { API_URL, getAuthHeaders, fetchWithRetry } from './config';

// 获取语言设置
export const getLanguageSettings = async (): Promise<{ language: string }> => {
  try {
    console.log('正在从后端获取语言设置...');
    // 使用 fetchWithRetry 代替普通的 fetch，增加重试机制
    const response = await fetchWithRetry(`${API_URL}/language/settings`, {
      headers: getAuthHeaders(),
      // 添加缓存控制，确保每次都获取最新设置
      cache: 'no-cache'
    }, 3);
    
    if (!response.ok) {
      console.error(`获取语言设置失败: HTTP ${response.status} - ${response.statusText}`);
      throw new Error(`获取语言设置失败: HTTP ${response.status}`);
    }
    
    const data = await response.json();
    console.log('获取到的语言设置:', data);
    
    // 确保返回的数据包含language字段
    if (!data || typeof data.language !== 'string') {
      console.warn('后端返回的语言设置数据格式不正确:', data);
      return { language: 'zh-CN' }; // 默认返回中文
    }
    
    // 验证语言代码是否有效
    if (!['zh-CN', 'en-US'].includes(data.language)) {
      console.warn(`后端返回了不支持的语言代码: ${data.language}`);
      return { language: 'zh-CN' }; // 默认返回中文
    }
    
    return data;
  } catch (error) {
    console.error('获取语言设置出错:', error);
    return { language: 'zh-CN' }; // 默认返回中文
  }
};

// 更新语言设置
export const updateLanguageSettings = async (language: string): Promise<boolean> => {
  try {
    console.log(`正在更新语言设置为: ${language}`);
    if (!['zh-CN', 'en-US'].includes(language)) {
      console.warn(`尝试设置不支持的语言: ${language}`);
      return false;
    }
    
    // 使用 fetchWithRetry 代替普通的 fetch，增加重试机制
    const response = await fetchWithRetry(`${API_URL}/language/settings`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ language }),
    }, 3);
    
    if (!response.ok) {
      console.error(`更新语言设置失败: HTTP ${response.status} - ${response.statusText}`);
      return false;
    }
    
    const result = await response.json();
    console.log('更新语言设置结果:', result);
    
    // 验证返回的结果
    if (result && result.status === 'success') {
      console.log(`语言设置已成功更新为: ${language}`);
      
      // 同时更新本地存储
      localStorage.setItem('kun-lab-language', language);
      console.log('本地语言设置已更新');
      
      return true;
    } else {
      console.warn('更新语言设置的响应不包含成功状态:', result);
      return false;
    }
  } catch (error) {
    console.error('更新语言设置出错:', error);
    return false;
  }
};

// 获取支持的语言列表
export const getSupportedLanguages = async (): Promise<Array<{ code: string, name: string }>> => {
  try {
    console.log('正在获取支持的语言列表...');
    const response = await fetchWithRetry(`${API_URL}/language/supported`, {
      headers: getAuthHeaders(),
    }, 3);
    
    if (!response.ok) {
      console.error(`获取支持的语言列表失败: HTTP ${response.status}`);
      throw new Error('获取支持的语言列表失败');
    }
    
    const data = await response.json();
    console.log('获取到的支持语言列表:', data);
    
    if (data && Array.isArray(data.languages)) {
      return data.languages;
    } else {
      console.warn('后端返回的语言列表格式不正确:', data);
      // 默认返回支持的语言
      return [
        { code: 'zh-CN', name: '中文' },
        { code: 'en-US', name: 'English' }
      ];
    }
  } catch (error) {
    console.error('获取支持的语言列表出错:', error);
    // 默认返回支持的语言
    return [
      { code: 'zh-CN', name: '中文' },
      { code: 'en-US', name: 'English' }
    ];
  }
};
