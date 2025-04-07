import axios from 'axios';

export const getLicense = async () => {
  try {
    // 确保后端 URL 是字符串，正确等待 Promise 解析
    let backendUrl = '';
    if (window.electronAPI?.getBackendUrl) {
      backendUrl = await window.electronAPI.getBackendUrl();
      console.log('获取到的后端 URL:', backendUrl);
    }
    
    // 构建 API URL
    const apiUrl = `${backendUrl}/api/license`;
    console.log('正在请求许可证文件，URL:', apiUrl);
    
    const response = await axios.get(apiUrl);
    return response.data.content;
  } catch (error) {
    console.error('获取许可证失败:', error);
    throw error;
  }
};