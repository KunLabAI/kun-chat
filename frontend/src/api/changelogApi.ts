import axios from 'axios';

export interface ChangelogResponse {
  content: string;
}

export async function getChangelog(): Promise<ChangelogResponse> {
  try {
    const response = await axios.get<ChangelogResponse>('/api/changelog');
    return response.data;
  } catch (error) {
    console.error('获取更新日志失败:', error);
    throw error;
  }
}