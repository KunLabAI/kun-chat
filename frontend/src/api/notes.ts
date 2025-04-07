import axios from 'axios'
import { API_URL, getAuthHeaders } from './config'

export interface Note {
  id: number
  user_id: string
  title: string
  content?: string
  conversation_id?: string
  created_at: string
  updated_at: string
}

export type NoteCreate = {
  title: string
  content: string
  conversation_id?: string
}

export type NoteUpdate = Partial<{
  title: string
  content: string
  conversation_id: string | null
}>

// 使用默认导出而不是命名导出
const notesApi = {
  /**
   * 获取用户的所有笔记
   */
  async getNotes(limit: number = 50, skip: number = 0): Promise<Note[]> {
    const response = await axios.get(`${API_URL}/notes`, {
      params: { limit, skip },
      headers: getAuthHeaders()
    })
    return response.data
  },

  /**
   * 获取单个笔记详情
   */
  async getNote(id: number): Promise<Note> {
    const response = await axios.get(`${API_URL}/notes/${id}`, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  /**
   * 创建新笔记
   */
  async createNote(note: NoteCreate): Promise<Note> {
    const response = await axios.post(`${API_URL}/notes`, note, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  /**
   * 更新笔记
   */
  async updateNote(id: number, note: NoteUpdate): Promise<Note> {
    const response = await axios.put(`${API_URL}/notes/${id}`, note, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  /**
   * 删除笔记
   */
  async deleteNote(id: number): Promise<void> {
    await axios.delete(`${API_URL}/notes/${id}`, {
      headers: getAuthHeaders()
    })
  },
  
  /**
   * 获取与特定对话关联的笔记
   */
  async getConversationNotes(conversationId: string): Promise<Note[]> {
    const response = await axios.get(`${API_URL}/notes/conversation/${conversationId}`, {
      headers: getAuthHeaders()
    })
    return response.data
  }
}

// 导出API对象作为默认导出
export default notesApi 