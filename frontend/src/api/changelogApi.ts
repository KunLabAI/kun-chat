import axios from 'axios';
import { API_URL } from './config';

export interface ChangelogResponse {
  content: string;
}

export async function getChangelog(): Promise<ChangelogResponse> {
  try {
    const response = await axios.get<ChangelogResponse>(`${API_URL}/changelog`, {
      timeout: 10000,
      headers: {
        'Accept': 'application/json'
      },
      withCredentials: false
    });
    return response.data;
  } catch (error) {
    console.error('获取更新日志失败:', error);
    throw error;
  }
}