<template>
  <MainLayout>
    <div class="model-details-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <div class="model-icon-wrapper">
              <img :src="getModelLogo(modelDetails?.family || '')" :alt="modelDetails?.family" class="model-icon">
            </div>
            <div class="title-text">
              <h1 class="main-title">{{ modelDetails?.display_name || modelDetails?.name }}</h1>
            </div>
          </div>
          <div class="header-actions">
            <div class="favorite-container">
              <input type="checkbox" id="favorite-checkbox" :checked="isFavorite" @change="toggleFavorite" />
              <label for="favorite-checkbox">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
              </label>
            </div>
            <Button variant="link" size="md" @click="goBack">
              {{ t('model.detail.back') }}
            </Button>
          </div>
        </div>
      </div>

      <div v-if="modelDetails" class="model-content">
        <!-- 标签页导航 -->
        <div class="model-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.key"
            class="model-tab-item"
            :class="{ 'model-tab-item-active': currentTab === tab.key }"
            @click="currentTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 标签页内容 -->
        <div class="model-tab-content">
          <!-- 基础信息 -->
          <div v-show="currentTab === 'basic'" class="model-tab-pane">
            <!-- 基本信息卡片 -->
            <div class="model-section">
              <h3 class="section-title">{{ t('model.detail.sections.basic_info') }}</h3>
              <div class="info-grid">
                <div v-for="(value, key) in basicInfo" :key="key" class="info-item">
                  <span class="info-label">{{ key }}</span>
                  <span class="info-value">{{ value || '-' }}</span>
                </div>
              </div>
            </div>

            <!-- ModelFile配置 -->
            <div class="model-section">
              <div class="section-header">
                <h3 class="section-title">{{ t('model.detail.sections.modelfile_config') }}</h3>
                <button class="toggle-btn" @click="toggleModelFileConfig">
                  {{ showModelFileConfig ? t('model.detail.actions.collapse') : t('model.detail.actions.expand') }}
                </button>
              </div>
              <div v-show="showModelFileConfig" class="section-content">
                <pre class="code-block">{{ modelDetails.advanced_parameters.modelfile }}</pre>
              </div>
            </div>
          </div>

          <!-- 高级参数 -->
          <div v-show="currentTab === 'advanced'" class="model-tab-pane">
            <!-- 模型架构信息 -->
            <div class="model-section">
              <h3 class="section-title">{{ t('model.detail.sections.model_architecture') }}</h3>
              <div class="info-grid">
                <div v-for="(value, key) in architectureInfo" :key="key" class="info-item">
                  <span class="info-label">{{ key }}</span>
                  <span class="info-value">{{ value || '-' }}</span>
                </div>
              </div>
            </div>

            <!-- Attention参数 -->
            <div class="model-section">
              <h3 class="section-title">{{ t('model.detail.sections.attention_params') }}</h3>
              <div class="info-grid">
                <div v-for="(value, key) in attentionParams" :key="key" class="info-item">
                  <span class="info-label">{{ key }}</span>
                  <span class="info-value">{{ value || '-' }}</span>
                </div>
              </div>
            </div>

            <!-- Tokenizer参数 -->
            <div class="model-section">
              <h3 class="section-title">{{ t('model.detail.sections.tokenizer_params') }}</h3>
              <div class="info-grid">
                <div v-for="(value, key) in tokenizerParams" :key="key" class="info-item">
                  <span class="info-label">{{ key }}</span>
                  <span class="info-value">{{ value || '-' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import { useModelsStore } from '@/stores/models'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/layouts/MainLayout.vue'
import Button from '@/components/common/Button.vue'
import { getModelLogo } from '@/utils/ModelsLogoMap'
import { useLocalization } from '@/i18n/composables'

const router = useRouter()
const route = useRoute()
const notification = useNotificationStore()
const modelsStore = useModelsStore()
const authStore = useAuthStore()
const { t } = useLocalization()

const modelDetails = ref<any>(null)
const currentTab = ref('basic')
const showModelFileConfig = ref(false)

// 收藏相关
const isFavorite = ref(false)
const favoriteLoading = ref(false)

// 检查收藏状态
async function checkFavoriteStatus() {
  if (!modelDetails.value || !authStore.isAuthenticated) return

  try {
    favoriteLoading.value = true
    if (!authStore.user?.username) return
    
    const isFavorited = await modelsStore.checkFavoriteStatus(modelDetails.value.id, authStore.user.username)
    isFavorite.value = isFavorited
  } catch (error) {
    console.error('获取收藏状态失败:', error)
  } finally {
    favoriteLoading.value = false
  }
}

// 切换收藏状态
async function toggleFavorite() {
  if (!modelDetails.value || !authStore.isAuthenticated || !authStore.user?.username) return

  try {
    favoriteLoading.value = true
    const result = await modelsStore.toggleFavorite(modelDetails.value.id, authStore.user.username)
    isFavorite.value = result.is_favorited
    notification.showSuccess(result.message)
  } catch (error) {
    console.error('操作收藏失败:', error)
    notification.showError('操作失败，请重试')
  } finally {
    favoriteLoading.value = false
  }
}

const tabs = [
  { key: 'basic', label: t('model.detail.tabs.basic') },
  { key: 'advanced', label: t('model.detail.tabs.advanced') }
]

const formatFileSize = (size: number): string => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
  if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(2)} MB`
  return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

const basicInfo = computed(() => {
  if (!modelDetails.value) return {}
  
  return {
    [t('model.detail.info_labels.name')]: modelDetails.value.display_name || modelDetails.value.name,
    [t('model.detail.info_labels.family')]: modelDetails.value.family || '-',
    [t('model.detail.info_labels.parameter_size')]: modelDetails.value.parameter_size || '-',
    [t('model.detail.info_labels.quantization')]: modelDetails.value.quantization_level || '-',
    [t('model.detail.info_labels.file_size')]: modelDetails.value.size ? formatFileSize(modelDetails.value.size) : '-',
    [t('model.detail.info_labels.created_at')]: modelDetails.value.created_at ? formatDate(modelDetails.value.created_at) : '-',
    [t('model.detail.info_labels.modified_at')]: modelDetails.value.modified_at ? formatDate(modelDetails.value.modified_at) : '-',
    [t('model.detail.info_labels.format')]: modelDetails.value.format || '-',
    [t('model.detail.info_labels.system_prompt')]: modelDetails.value.system_prompt || '-',
  }
})

const architectureInfo = computed(() => {
  if (!modelDetails.value || !modelDetails.value.advanced_parameters) return {}
  
  // 尝试从 model_info 获取数据，如果没有则使用 architecture
  const modelInfo = modelDetails.value.advanced_parameters.model_info || {}
  const architecture = modelDetails.value.advanced_parameters.architecture || {}
  
  if (Object.keys(modelInfo).length > 0) {
    // 使用旧版本的数据结构
    return {
      [t('model.detail.advanced_params.architecture_type')]: modelInfo['general.architecture'],
      [t('model.detail.advanced_params.base_model')]: modelInfo['general.base_model.0.name'],
      [t('model.detail.advanced_params.organization')]: modelInfo['general.base_model.0.organization'],
      [t('model.detail.advanced_params.repo_url')]: modelInfo['general.base_model.0.repo_url'],
      [t('model.detail.advanced_params.model_name')]: modelInfo['general.basename'],
      [t('model.detail.advanced_params.parameter_count')]: formatNumber(modelInfo['general.parameter_count']),
      [t('model.detail.advanced_params.quantization_version')]: modelInfo['general.quantization_version'],
      [t('model.detail.advanced_params.size_label')]: modelInfo['general.size_label'],
      [t('model.detail.advanced_params.finetune_type')]: modelInfo['general.finetune'],
      [t('model.detail.advanced_params.tags')]: Array.isArray(modelInfo['general.tags']) ? modelInfo['general.tags'].join(', ') : '-'
    }
  } else {
    // 使用新版本的数据结构
    return {
      [t('model.detail.advanced_params.context_length')]: formatNumber(architecture.context_length),
      [t('model.detail.advanced_params.embedding_length')]: formatNumber(architecture.embedding_length),
      [t('model.detail.advanced_params.feed_forward')]: formatNumber(architecture.feed_forward),
      [t('model.detail.advanced_params.head_count')]: formatNumber(architecture.head_count),
      [t('model.detail.advanced_params.kv_head_count')]: formatNumber(architecture.kv_head_count),
      [t('model.detail.advanced_params.layer_count')]: formatNumber(architecture.layer_count),
      [t('model.detail.advanced_params.vocabulary_size')]: formatNumber(architecture.vocabulary_size)
    }
  }
})

const attentionParams = computed(() => {
  if (!modelDetails.value || !modelDetails.value.advanced_parameters) return {}
  
  // 尝试从 model_info 获取数据，如果没有则使用 attention
  const modelInfo = modelDetails.value.advanced_parameters.model_info || {}
  const attention = modelDetails.value.advanced_parameters.attention || {}
  
  if (Object.keys(modelInfo).length > 0) {
    // 获取注意力相关的参数
    const attentionKeys = Object.keys(modelInfo).filter(key => 
      key.includes('attention') || 
      key.includes('context_length') || 
      key.includes('embedding') || 
      key.includes('feed_forward') || 
      key.includes('rope') ||
      key.includes('block_count')
    )
    
    const params: Record<string, any> = {}
    attentionKeys.forEach(key => {
      let displayName = key.split('.').pop() || ''
      // 格式化显示名称
      displayName = displayName
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .toLowerCase()
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
      
      params[displayName] = modelInfo[key]
    })
    
    return {
      [t('model.detail.advanced_params.attention_head_count')]: params['Head Count'],
      [t('model.detail.advanced_params.kv_head_count_param')]: params['Head Count Kv'],
      [t('model.detail.advanced_params.layer_norm_epsilon')]: params['Layer Norm Rms Epsilon'],
      [t('model.detail.advanced_params.block_count')]: params['Block Count'],
      [t('model.detail.advanced_params.context_length_param')]: formatNumber(params['Context Length']),
      [t('model.detail.advanced_params.embedding_dimension')]: params['Embedding Length'],
      [t('model.detail.advanced_params.feed_forward_dimension')]: params['Feed Forward Length'],
      [t('model.detail.advanced_params.rope_freq_base')]: params['Freq Base']
    }
  } else {
    // 使用新版本的数据结构
    return {
      [t('model.detail.advanced_params.rope_dimension')]: formatNumber(attention.rope_dimension),
      [t('model.detail.advanced_params.rope_freq_base')]: formatNumber(attention.rope_freq_base)
    }
  }
})

const tokenizerParams = computed(() => {
  if (!modelDetails.value || !modelDetails.value.advanced_parameters) return {}
  
  // 尝试从 model_info 获取数据，如果没有则使用 tokenizer
  const modelInfo = modelDetails.value.advanced_parameters.model_info || {}
  const tokenizer = modelDetails.value.advanced_parameters.tokenizer || {}
  
  if (Object.keys(modelInfo).length > 0) {
    const tokenizerKeys = Object.keys(modelInfo).filter(key => key.startsWith('tokenizer.'))
    
    const params: Record<string, any> = {}
    tokenizerKeys.forEach(key => {
      const value = modelInfo[key]
      if (value !== null && value !== undefined) {
        params[key] = value
      }
    })
    
    return {
      [t('model.detail.advanced_params.tokenizer_type')]: params['tokenizer.ggml.model'],
      [t('model.detail.advanced_params.add_bos_token')]: params['tokenizer.ggml.add_bos_token'] ? t('common.yes') : t('common.no'),
      [t('model.detail.advanced_params.add_eos_token')]: params['tokenizer.ggml.add_eos_token'] ? t('common.yes') : t('common.no'),
      [t('model.detail.advanced_params.bos_token_id')]: params['tokenizer.ggml.bos_token_id'],
      [t('model.detail.advanced_params.eos_token_id')]: params['tokenizer.ggml.eos_token_id'],
      [t('model.detail.advanced_params.padding_token_id')]: params['tokenizer.ggml.padding_token_id'],
      [t('model.detail.advanced_params.prefix')]: params['tokenizer.ggml.pre']
    }
  } else {
    // 使用新版本的数据结构
    return {
      [t('model.detail.advanced_params.type')]: tokenizer.type || '-',
      [t('model.detail.advanced_params.model')]: tokenizer.model || '-',
      [t('model.detail.advanced_params.tokens')]: formatNumber(tokenizer.tokens)
    }
  }
})

// 添加一个调试函数，帮助我们查看所有可用的参数
const logModelInfo = () => {
  console.log('Model Details:', modelDetails.value)
  if (modelDetails.value?.advanced_parameters) {
    console.log('Advanced Parameters:', modelDetails.value.advanced_parameters)
    if (modelDetails.value.advanced_parameters.model_info) {
      console.log('Model Info:', modelDetails.value.advanced_parameters.model_info)
    }
    if (modelDetails.value.advanced_parameters.architecture) {
      console.log('Architecture:', modelDetails.value.advanced_parameters.architecture)
    }
    if (modelDetails.value.advanced_parameters.attention) {
      console.log('Attention:', modelDetails.value.advanced_parameters.attention)
    }
    if (modelDetails.value.advanced_parameters.tokenizer) {
      console.log('Tokenizer:', modelDetails.value.advanced_parameters.tokenizer)
    }
  }
}

const toggleModelFileConfig = () => showModelFileConfig.value = !showModelFileConfig.value

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/models')
  }
}

const formatDate = (date: string | undefined | null) => {
  if (!date) return '-'
  
  return new Date(date).toLocaleString(t('common.locale', 'zh-CN'), {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatNumber = (num: number | string | null): string => {
  if (num === null || num === undefined) return '-'
  if (typeof num === 'string' && !num.trim()) return '-'
  
  return String(num)
}

const fetchModelDetails = async () => {
  try {
    const modelId = parseInt(route.params.id as string)
    if (isNaN(modelId)) {
      notification.showError('无效的模型ID')
      router.push('/models')
      return
    }
    
    const details = await modelsStore.fetchModelDetails(modelId)
    if (!details) {
      notification.showError('获取模型详情失败')
      router.push('/models')
      return
    }
    
    modelDetails.value = details
  } catch (error) {
    console.error('获取模型详情失败:', error)
    notification.showError('获取模型详情失败')
    router.push('/models')
  }
}

onMounted(async () => {
  await fetchModelDetails()
  await checkFavoriteStatus()
})

// 监听路由变化，重新获取模型详情
watch(() => route.params.id, async (newId, oldId) => {
  if (newId !== oldId) {
    await fetchModelDetails()
    await checkFavoriteStatus()
  }
})

// 在获取到模型详情后调用调试函数
watch(modelDetails, (newVal) => {
  if (newVal) {
    logModelInfo()
  }
}, { immediate: true })
</script>

<style scoped>
@import '@/styles/ModelDetailPage.css';
</style>