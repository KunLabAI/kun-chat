import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { API_URL } from './config'

export interface Tag {
  text: string
  color: string
}

export interface Prompt {
  id: string
  title: string
  content: string
  tags: Tag[]
  created_at: string
  updated_at: string
}

export type PromptBase = Omit<Prompt, 'id' | 'created_at' | 'updated_at'>

export const promptApi = {
  async getPrompts(): Promise<Prompt[]> {
    const authStore = useAuthStore()
    const response = await axios.get(`${API_URL}/prompts`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    return response.data
  },

  async getPrompt(id: string): Promise<Prompt> {
    const authStore = useAuthStore()
    const response = await axios.get(`${API_URL}/prompts/${id}`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    return response.data
  },

  async createPrompt(prompt: PromptBase): Promise<Prompt> {
    const authStore = useAuthStore()
    const response = await axios.post(`${API_URL}/prompts`, prompt, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    return response.data
  },

  async updatePrompt(id: string, prompt: PromptBase): Promise<Prompt> {
    const authStore = useAuthStore()
    const response = await axios.put(`${API_URL}/prompts/${id}`, prompt, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    return response.data
  },

  async deletePrompt(id: string): Promise<void> {
    const authStore = useAuthStore()
    await axios.delete(`${API_URL}/prompts/${id}`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
  }
}
