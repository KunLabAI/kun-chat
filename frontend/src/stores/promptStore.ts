import { defineStore } from 'pinia'
import { promptApi } from '../api/prompts'
import type { Prompt, PromptBase } from '../api/prompts'

interface PromptState {
  prompts: Prompt[]
  loading: boolean
  error: string | null
}

export const usePromptStore = defineStore("prompt", {
  state: (): PromptState => ({
    prompts: [] as Prompt[],
    loading: false,
    error: null as string | null
  }),

  getters: {
    getPromptById: (state) => (id: string) => {
      return state.prompts.find(p => p.id === id)
    },

    getPromptsByTag: (state) => (tag: string) => {
      return state.prompts.filter(p => p.tags?.some(t => t.text === tag))
    },

    getRecentPrompts: (state) => (limit = 5) => {
      return [...state.prompts]
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, limit)
    }
  },

  actions: {
    async loadPrompts() {
      this.loading = true
      this.error = null
      try {
        this.prompts = await promptApi.getPrompts()
      } catch (error: any) {
        this.error = error?.message || '加载提示词失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async getPrompt(id: string) {
      try {
        return await promptApi.getPrompt(id)
      } catch (error: any) {
        this.error = error?.message || '获取提示词失败'
        throw error
      }
    },

    async createPrompt(prompt: PromptBase) {
      this.loading = true
      this.error = null
      try {
        const newPrompt = await promptApi.createPrompt(prompt)
        this.prompts.push(newPrompt)
        return newPrompt
      } catch (error: any) {
        this.error = error?.message || '创建提示词失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updatePrompt(prompt: Prompt) {
      this.loading = true
      this.error = null
      try {
        const { id, ...promptData } = prompt
        const updatedPrompt = await promptApi.updatePrompt(id, promptData)
        const index = this.prompts.findIndex(p => p.id === id)
        if (index !== -1) {
          this.prompts[index] = updatedPrompt
        }
        return updatedPrompt
      } catch (error: any) {
        this.error = error?.message || '更新提示词失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deletePrompt(id: string) {
      this.loading = true
      this.error = null
      try {
        await promptApi.deletePrompt(id)
        this.prompts = this.prompts.filter(p => p.id !== id)
      } catch (error: any) {
        this.error = error?.message || '删除提示词失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
});
