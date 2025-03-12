<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div v-for="model in recentModels" :key="model.name" class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ model.name }}</h3>
        <span class="text-sm text-gray-500 dark:text-gray-400">
          {{ formatDate(model.modified_at) }}
        </span>
      </div>
      
      <div class="space-y-2">
        <div class="flex items-center text-sm text-gray-600 dark:text-gray-300">
          <span class="font-medium mr-2">大小:</span>
          <span>{{ formatSize(model.size) }}</span>
        </div>
        
        <div v-if="model.details" class="flex items-center text-sm text-gray-600 dark:text-gray-300">
          <span class="font-medium mr-2">系列:</span>
          <span>{{ model.details.family || '未知' }}</span>
        </div>
        
        <div v-if="model.details" class="flex items-center text-sm text-gray-600 dark:text-gray-300">
          <span class="font-medium mr-2">参数量:</span>
          <span>{{ model.details.parameter_size || '未知' }}</span>
        </div>
      </div>

      <div class="mt-4 flex justify-end">
        <button
          @click="selectModel(model)"
          class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        >
          选择
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { modelApi } from '@/api'

const recentModels = ref([])

const loadModels = async () => {
  try {
    const { success, data } = await modelApi.getModels()
    if (success && data.models) {
      // 按修改时间排序并只取前6个
      recentModels.value = data.models
        .sort((a, b) => new Date(b.modified_at) - new Date(a.modified_at))
        .slice(0, 6)
    }
  } catch (error) {
    console.error('Failed to load models:', error)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatSize = (bytes) => {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

const selectModel = (model) => {
  emit('select', model)
}

const emit = defineEmits(['select'])

onMounted(() => {
  loadModels()
})
</script>
