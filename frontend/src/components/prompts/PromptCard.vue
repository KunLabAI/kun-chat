<template>
  <div class="prompt-card">
    <div class="card-content">
      <div class="card-header">
        <div class="title-group">
          <h3 class="card-title cursor-pointer" @click="$emit('edit')">
            {{ prompt.title }}
          </h3>
          <p class="card-meta">
            {{ prompt.updated_at !== prompt.created_at ? '更新于' : '创建于' }} {{ formatDate(prompt.updated_at || prompt.created_at) }}
          </p>
        </div>
        <div class="card-actions">
          <slot name="actions"></slot>
        </div>
      </div>
      <div class="card-body cursor-pointer" @click="$emit('edit')">
        <p class="card-text">
          {{ prompt.content }}
        </p>
      </div>
      <div class="card-tags">
        <span 
          v-for="tag in prompt.tags" 
          :key="tag.text"
          class="tag"
          :style="{ backgroundColor: tag.color }"
        >
          {{ tag.text }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type Prompt } from '@/api/prompts'

defineProps<{
  prompt: Prompt
}>()

defineEmits<{
  edit: []
}>()

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

<style scoped>
@import '@/styles/PromptCard.css';
</style>
