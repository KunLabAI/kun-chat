import { defineStore } from 'pinia'
import notesApi from '../api/notes'
import type { Note, NoteCreate, NoteUpdate } from '../api/notes'
import { useNotificationStore } from './notification'

interface NotesState {
  notes: Note[]
  filteredNotes: Note[]
  currentNote: Note | null
  loading: boolean
  error: string | null
  searchQuery: string
}

export const useNotesStore = defineStore('notes', {
  state: (): NotesState => ({
    notes: [],
    filteredNotes: [],
    currentNote: null,
    loading: false,
    error: null,
    searchQuery: ''
  }),

  getters: {
    getNoteById: (state) => (id: number) => {
      return state.notes.find(note => note.id === id) || null
    },

    getNotesByConversation: (state) => (conversationId: string) => {
      return state.notes.filter(note => note.conversation_id === conversationId)
    },

    getRecentNotes: (state) => (limit = 5) => {
      return [...state.notes]
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, limit)
    }
  },

  actions: {
    // 获取所有笔记
    async fetchNotes() {
      this.loading = true
      this.error = null
      
      try {
        const notes = await notesApi.getNotes()
        console.log('获取到的笔记数据:', notes);
        // 检查每个笔记的内容字段
        notes.forEach((note, index) => {
          console.log(`笔记 ${index} 内容:`, note.content, typeof note.content);
        });
        
        this.notes = notes
        this.applyFilters()
        this.loading = false
        return { success: true, data: notes }
      } catch (error: any) {
        console.error('获取笔记失败:', error)
        this.loading = false
        this.error = error.response?.data?.detail || '获取笔记时发生错误'
        const notificationStore = useNotificationStore()
        notificationStore.showError('获取笔记失败')
        return { success: false, error }
      }
    },

    // 获取单个笔记
    async fetchNote(id: number) {
      this.loading = true
      this.error = null
      
      try {
        const note = await notesApi.getNote(id)
        this.currentNote = note
        this.loading = false
        return { success: true, data: note }
      } catch (error: any) {
        console.error(`获取笔记 ${id} 失败:`, error)
        this.loading = false
        this.error = error.response?.data?.detail || '获取笔记时发生错误'
        const notificationStore = useNotificationStore()
        notificationStore.showError('获取笔记失败')
        return { success: false, error }
      }
    },

    // 创建笔记
    async createNote(noteData: NoteCreate) {
      this.loading = true
      this.error = null
      
      try {
        const note = await notesApi.createNote(noteData)
        await this.fetchNotes() // 刷新笔记列表
        this.loading = false
        const notificationStore = useNotificationStore()
        notificationStore.showSuccess('笔记创建成功')
        return { success: true, data: note }
      } catch (error: any) {
        console.error('创建笔记失败:', error)
        this.loading = false
        this.error = error.response?.data?.detail || '创建笔记时发生错误'
        const notificationStore = useNotificationStore()
        notificationStore.showError('创建笔记失败')
        return { success: false, error }
      }
    },

    // 更新笔记
    async updateNote(id: number, noteData: NoteUpdate) {
      this.loading = true
      this.error = null
      
      try {
        const note = await notesApi.updateNote(id, noteData)
        // 更新本地数据
        const index = this.notes.findIndex(note => note.id === id)
        if (index !== -1) {
          this.notes[index] = note
          this.applyFilters()
        }
        this.currentNote = note
        this.loading = false
        const notificationStore = useNotificationStore()
        notificationStore.showSuccess('笔记更新成功')
        return { success: true, data: note }
      } catch (error: any) {
        console.error(`更新笔记 ${id} 失败:`, error)
        this.loading = false
        this.error = error.response?.data?.detail || '更新笔记时发生错误'
        const notificationStore = useNotificationStore()
        notificationStore.showError('更新笔记失败')
        return { success: false, error }
      }
    },

    // 删除笔记
    async deleteNote(id: number) {
      this.loading = true
      this.error = null
      
      try {
        await notesApi.deleteNote(id)
        // 更新本地数据
        this.notes = this.notes.filter(note => note.id !== id)
        this.applyFilters()
        if (this.currentNote?.id === id) {
          this.currentNote = null
        }
        this.loading = false
        const notificationStore = useNotificationStore()
        notificationStore.showSuccess('笔记删除成功')
        return { success: true }
      } catch (error: any) {
        console.error(`删除笔记 ${id} 失败:`, error)
        this.loading = false
        this.error = error.response?.data?.detail || '删除笔记时发生错误'
        const notificationStore = useNotificationStore()
        notificationStore.showError('笔记删除失败')
        return { success: false, error }
      }
    },

    // 应用筛选
    applyFilters() {
      if (!this.searchQuery) {
        this.filteredNotes = [...this.notes]
          .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
        return
      }
      
      const query = this.searchQuery.toLowerCase()
      this.filteredNotes = this.notes.filter(note => 
        note.title.toLowerCase().includes(query) || 
        (note.content?.toLowerCase()?.includes(query) || false)
      )
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
    },

    // 清除当前笔记
    clearCurrentNote() {
      this.currentNote = null
    },

    // 重置状态
    resetState() {
      this.notes = []
      this.filteredNotes = []
      this.currentNote = null
      this.loading = false
      this.error = null
      this.searchQuery = ''
    },

    async loadConversationNotes(conversationId: string) {
      this.loading = true
      this.error = null
      try {
        const notes = await notesApi.getConversationNotes(conversationId)
        
        // 更新store中的笔记
        notes.forEach(note => {
          const index = this.notes.findIndex(n => n.id === note.id)
          if (index !== -1) {
            this.notes[index] = note
          } else {
            this.notes.push(note)
          }
        })
        
        return notes
      } catch (error: any) {
        this.error = error?.message || '加载对话笔记失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    setCurrentNote(note: Note | null) {
      this.currentNote = note
    }
  }
}) 