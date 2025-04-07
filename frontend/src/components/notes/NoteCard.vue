<template>
  <div class="note-card">
    <div class="card-content">
      <div class="card-header">
        <div class="title-group">
          <h3 class="card-title cursor-pointer" @click="handleEdit">
            {{ note.title }}
          </h3>
        </div>
        <div class="card-actions">
          <button class="action-button delete-button" @click="handleDelete">
            <img src="@/assets/icons/model_delete.svg" alt="删除" class="action-icon" />
          </button>
        </div>
      </div>
      <div class="card-body cursor-pointer" @click="handleEdit">
        <p class="card-text">
          {{ note.content || '暂无内容' }}
        </p>
      </div>
      <p class="card-meta">
        {{ note.updated_at !== note.created_at ? '更新于' : '创建于' }} {{ formatDate(note.updated_at || note.created_at) }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Note } from '@/api/notes'

const props = defineProps<{
  note: Note
}>()

const emit = defineEmits<{
  (e: 'edit', id: number): void
  (e: 'delete', id: number): void
}>()

// 处理编辑按钮点击
const handleEdit = (event: Event) => {
  event.stopPropagation()
  emit('edit', props.note.id)
}

// 处理删除按钮点击
const handleDelete = (event: Event) => {
  event.stopPropagation()
  emit('delete', props.note.id)
}

function formatDate(timestamp: string) {
  if (!timestamp) return '未知时间'
  
  // 将 UTC 时间字符串转换为本地时间
  const date = new Date(timestamp)
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  
  return localDate.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    hour12: false // 使用24小时制
  })
}
</script>

<script lang="ts">
export default {}
</script>

<style scoped>
@import './NoteCard.css';
</style> 