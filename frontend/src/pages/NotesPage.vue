<template>
  <MainLayout>
    <div class="notes-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="main-title">{{ t('notes.title') }}</h1>
            <p class="sub-title">{{ t('notes.subtitle') }}</p>
          </div>
          <div class="header-actions">

            <Button
              variant="primary"
              size="md"
              @click="router.push('/notes/create')"
            >
              {{ t('notes.create_note') }}
            </Button>
          </div>
        </div>
        <div class="search-box">
          <input 
            type="text" 
            v-model="notesStore.searchQuery" 
            class="search-input" 
            :placeholder="t('notes.search_placeholder')" 
            @input="onSearchInput"
            @keydown.enter="handleSearch" 
          />
          <MagnifyingGlassIcon class="search-icon" />
        </div>
      </div>

      <!-- 笔记列表 -->
      <div v-if="notesStore.loading" class="loading-indicator">
        <DotLoader />
        <p class="mt-2">{{ t('status.loading') }}</p>
      </div>
      <div v-else-if="notesStore.error" class="error-message">
        {{ notesStore.error }}
      </div>
      <div v-else-if="notes.length === 0" class="empty-state">
        <img src="@/assets/illustration/notesempty.png" alt="Empty Notes" class="empty-state-image">
        <p class="empty-state-text">{{ t('notes.empty_state.subtitle') }}</p>
      </div>
      <div v-else-if="notesStore.filteredNotes.length === 0" class="empty-container">
        <img src="@/assets/icons/sys_search.svg" alt="搜索" class="empty-icon" />
        <h3 class="empty-title">{{ t('notes.search_empty.title') }}</h3>
        <p class="empty-message">{{ t('notes.search_empty.subtitle') }}</p>
        <Button 
          @click="notesStore.searchQuery = ''; applyFilters()" 
          variant="secondary" 
          size="md"
        >
          {{ t('notes.search_empty.clear_button') }}
        </Button>
      </div>
      <div v-else class="notes-grid">
        <div v-for="note in notesStore.filteredNotes" :key="note.id" class="note-grid-item">
          <!-- 调试提示 -->
          <div style="display: none;">
            <pre>{{ JSON.stringify(note, null, 2) }}</pre>
            <p>内容字段: {{ note.content }} ({{ typeof note.content }})</p>
          </div>
          <NoteCard 
            :note="note" 
            @edit="router.push(`/notes/${note.id}/edit`)" 
            @delete="confirmDelete(note)" 
          />
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <Dialog
      v-model="showDeleteConfirm"
      :title="t('notes.delete_dialog.title')"
      @confirm="executeDelete"
      @cancel="showDeleteConfirm = false"
      :confirm-text="t('common.actions.delete')"
      :cancel-text="t('common.actions.cancel')"
      confirm-variant="danger"
    >
      <div class="delete-confirm-content">
        <p>{{ t('notes.delete_dialog.confirm_message') }}</p>
      </div>
    </Dialog>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import MainLayout from '@/layouts/MainLayout.vue'
import Button from '@/components/common/Button.vue'
import Dialog from '@/components/common/Dialog.vue'
import DotLoader from '@/components/common/DotLoader.vue'
import NoteCard from '../components/notes/NoteCard.vue'
import { useNotesStore } from '@/stores/notes'
import { useNotificationStore } from '@/stores/notification'
import { useRouter } from 'vue-router'
import { useLocalization } from '@/i18n'
import notesApi, { type Note } from '@/api/notes'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const { t } = useLocalization()
const notesStore = useNotesStore()
const notificationStore = useNotificationStore()
const router = useRouter()

const { notes } = storeToRefs(notesStore)
const showDeleteConfirm = ref(false)
const noteToDelete = ref<Note | null>(null)

onMounted(async () => {
  await fetchNotes()
})

function confirmDelete(note: Note) {
  noteToDelete.value = note
  showDeleteConfirm.value = true
}

async function executeDelete() {
  if (!noteToDelete.value) return
  
  try {
    await notesStore.deleteNote(noteToDelete.value.id)
    showDeleteConfirm.value = false
    noteToDelete.value = null
  } catch (error: any) {
    console.error('删除笔记失败:', error)
    notificationStore.error(t('notes.notifications.delete_error'))
  }
}

// 获取笔记数据
const fetchNotes = async () => {
  notesStore.loading = true
  notesStore.error = null
  
  try {
    const data = await notesApi.getNotes()
    notes.value = data || [] // 确保notes是一个数组
    applyFilters()
    notesStore.loading = false
  } catch (error: any) {
    console.error('获取笔记失败:', error)
    notesStore.loading = false
    notesStore.error = error.response?.data?.detail || t('notes.notifications.load_error')
    notificationStore.error(t('notes.notifications.load_error'))
  }
}

// 筛选笔记
const applyFilters = () => {
  // 确保filteredNotes存在
  if (!notesStore.filteredNotes) {
    notesStore.filteredNotes = [];
  }
  
  if (!notesStore.searchQuery) {
    notesStore.filteredNotes = [...notes.value]
      .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
    return;
  }
  
  const query = notesStore.searchQuery.toLowerCase();
  notesStore.filteredNotes = notes.value.filter(note => 
    (note.title?.toLowerCase().includes(query) || 
    (note.content?.toLowerCase()?.includes(query) || false))
  )
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
}

// 搜索处理
const handleSearch = () => {
  applyFilters()
}

// 监听搜索查询变化
const onSearchInput = () => {
  applyFilters()
}
</script>

<style scoped>
@import '@/styles/NotesPage.css';
</style> 