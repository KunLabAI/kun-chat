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
              <h1 class="main-title" :title="modelDetails?.display_name || modelDetails?.name">{{ modelDetails?.display_name || modelDetails?.name }}</h1>
            </div>
          </div>
          <div class="header-actions">
            <div class="favorite-container">
              <input type="checkbox" id="favorite-checkbox" :checked="isFavorite" @change="toggleFavorite" />
              <label for="favorite-checkbox">
                <img v-if="!isFavorite" :src="emptyStarIcon" width="24" height="24" alt="未收藏" />
                <img v-else :src="starIcon" width="24" height="24" alt="已收藏" />
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
                  <span v-if="typeof value === 'object' && value.type === 'system_prompt'" 
                        class="info-value system-prompt" 
                        @click="showSystemPromptDialog(value.value)">
                    {{ truncateSystemPrompt(value.value) }}
                  </span>
                  <span v-else class="info-value">{{ value || '-' }}</span>
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
              <div v-if="showModelFileConfig" class="section-content">
                <pre class="code-block">{{ getModelfileWithoutLicense }}</pre>
              </div>
            </div>

            <!-- License信息 -->
            <div v-if="modelDetails.advanced_parameters?.license" class="model-section">
              <div class="section-header">
                <h3 class="section-title">{{ t('model.detail.sections.license') }}</h3>
                <button class="toggle-btn" @click="toggleLicense">
                  {{ showLicense ? t('model.detail.actions.collapse') : t('model.detail.actions.expand') }}
                </button>
              </div>
              <div v-if="showLicense" class="section-content">
                <pre class="code-block">{{ modelDetails.advanced_parameters.license }}</pre>
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

      <!-- 系统提示词对话框 -->
      <Dialog
        v-model="isSystemPromptDialogVisible"
        :title="t('model.detail.system_prompt_title')"
        :confirmText="t('common.actions.close')"
        @confirm="closeSystemPromptDialog"
        class="system-prompt-dialog"
      >
        <div class="system-prompt-dialog-content">
          <pre class="system-prompt-content">{{ formatSystemPrompt(currentSystemPrompt) }}</pre>
        </div>
      </Dialog>
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
import Dialog from '@/components/common/Dialog.vue'
import { getModelLogo } from '@/utils/ModelsLogoMap'
import { useLocalization } from '@/i18n/composables'
import emptyStarIcon from '@/assets/icons/sys_emptystar.svg'
import starIcon from '@/assets/icons/sys_star.svg'

const router = useRouter()
const route = useRoute()
const notification = useNotificationStore()
const modelsStore = useModelsStore()
const authStore = useAuthStore()
const { t } = useLocalization()

const modelDetails = ref<any>(null)
const currentTab = ref('basic')
const showModelFileConfig = ref(false)
const showLicense = ref(false)

// 收藏相关
const isFavorite = ref(false)
const favoriteLoading = ref(false)

// 系统提示词相关
const isSystemPromptDialogVisible = ref(false)
const currentSystemPrompt = ref('')

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

// 添加从modelfile提取系统提示词的计算属性
const systemPromptFromModelfile = computed(() => {
  if (!modelDetails.value?.advanced_parameters?.modelfile) return null
  
  const modelfile = modelDetails.value.advanced_parameters.modelfile
  
  const systemMatch = modelfile.match(/SYSTEM\s+"([^"]*)"/)
  
  const systemMultilineMatch = modelfile.match(/SYSTEM\s+"""([\s\S]*?)"""/)
  
  return systemMultilineMatch ? systemMultilineMatch[1] : 
         systemMatch ? systemMatch[1] : null
})

const basicInfo = computed(() => {
  if (!modelDetails.value) return {}
  
  const info: Record<string, any> = {
    [t('model.detail.info_labels.name')]: modelDetails.value.display_name || modelDetails.value.name,
    [t('model.detail.info_labels.family')]: modelDetails.value.family || '-',
    [t('model.detail.info_labels.parameter_size')]: modelDetails.value.parameter_size || '-',
    [t('model.detail.info_labels.quantization')]: modelDetails.value.quantization || '-',
    [t('model.detail.info_labels.format')]: modelDetails.value.format || '-',
    [t('model.detail.info_labels.created_at')]: modelDetails.value.created_at ? formatDate(modelDetails.value.created_at) : '-',
    [t('model.detail.info_labels.modified_at')]: modelDetails.value.modified_at ? formatDate(modelDetails.value.modified_at) : '-'
  }
  
  // 添加文件大小
  if (modelDetails.value.size) {
    info[t('model.detail.info_labels.file_size')] = formatFileSize(modelDetails.value.size)
  }
  
  // 添加系统提示词 - 优先使用从modelfile提取的系统提示词
  const systemPrompt = systemPromptFromModelfile.value || modelDetails.value.system_prompt
  if (systemPrompt) {
    info[t('model.detail.info_labels.system')] = {
      type: 'system_prompt',
      value: systemPrompt
    }
  }
  
  // 添加最后使用时间(如果有)
  if (modelDetails.value.last_used_at) {
    info[t('model.detail.info_labels.last_used')] = formatDate(modelDetails.value.last_used_at)
  }
  
  return info
})

const architectureInfo = computed(() => {
  if (!modelDetails.value || !modelDetails.value.advanced_parameters) return {}
  
  const architecture = modelDetails.value.advanced_parameters.architecture || {}
  
  // 使用统一的数据结构处理方式，后端现在始终会提供完整的architecture结构
  const archParams: Record<string, any> = {
    [t('model.detail.advanced_params.context_length')]: formatNumber(architecture.context_length),
    [t('model.detail.advanced_params.embedding_length')]: formatNumber(architecture.embedding_length),
    [t('model.detail.advanced_params.feed_forward')]: formatNumber(architecture.feed_forward),
    [t('model.detail.advanced_params.head_count')]: formatNumber(architecture.head_count),
    [t('model.detail.advanced_params.kv_head_count')]: formatNumber(architecture.kv_head_count),
    [t('model.detail.advanced_params.layer_count')]: formatNumber(architecture.layer_count),
    [t('model.detail.advanced_params.vocabulary_size')]: formatNumber(architecture.vocabulary_size),
    [t('model.detail.advanced_params.parameter_count')]: formatNumber(architecture.parameter_count),
    [t('model.detail.advanced_params.size_label')]: architecture.size_label || '-',
    [t('model.detail.advanced_params.version')]: architecture.version || '-'
  }
  
  // 添加其他模型信息
  const additionalFields = [
    { key: 'organization', label: t('model.detail.advanced_params.organization') },
    { key: 'repository_url', label: t('model.detail.advanced_params.repo_url') },
    { key: 'base_model', label: t('model.detail.advanced_params.base_model') }
  ]
  
  additionalFields.forEach(field => {
    if (architecture[field.key]) {
      archParams[field.label] = architecture[field.key]
    }
  })
  
  // 处理数组类型的字段
  const arrayFields = [
    { key: 'tags', label: t('model.detail.advanced_params.tags') },
    { key: 'languages', label: t('model.detail.advanced_params.languages') }
  ]
  
  arrayFields.forEach(field => {
    if (architecture[field.key]) {
      archParams[field.label] = Array.isArray(architecture[field.key]) ? 
        architecture[field.key].join(', ') : architecture[field.key]
    }
  })
  
  return archParams
})

const attentionParams = computed(() => {
  if (!modelDetails.value || !modelDetails.value.advanced_parameters) return {}
  
  const attention = modelDetails.value.advanced_parameters.attention || {}
  
  // 使用统一的数据结构处理方式
  const attParams: Record<string, any> = {
    [t('model.detail.advanced_params.rope_dimension')]: formatNumber(attention.rope_dimension),
    [t('model.detail.advanced_params.rope_freq_base')]: formatNumber(attention.rope_freq_base)
  }
  
  // 添加可选的注意力参数
  const optionalFields = [
    { key: 'sliding_window', label: t('model.detail.advanced_params.sliding_window') },
    { key: 'key_length', label: t('model.detail.advanced_params.key_length') },
    { key: 'value_length', label: t('model.detail.advanced_params.value_length') },
    { key: 'layer_norm_epsilon', label: t('model.detail.advanced_params.layer_norm_epsilon') }
  ]
  
  optionalFields.forEach(field => {
    if (attention[field.key] !== null && attention[field.key] !== undefined) {
      attParams[field.label] = formatNumber(attention[field.key])
    }
  })
  
  return attParams
})

const tokenizerParams = computed(() => {
  if (!modelDetails.value || !modelDetails.value.advanced_parameters) return {}
  
  const tokenizer = modelDetails.value.advanced_parameters.tokenizer || {}
  
  // 使用统一的数据结构处理方式
  const tokParams: Record<string, any> = {
    [t('model.detail.advanced_params.type')]: tokenizer.type || '-',
    [t('model.detail.advanced_params.model')]: tokenizer.model || '-',
    [t('model.detail.advanced_params.tokens')]: formatNumber(tokenizer.tokens)
  }
  
  return tokParams
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
    
    // 添加详细结构的日志，以便更好地调试
    console.log('详细的模型结构:', JSON.stringify(modelDetails.value, null, 2))
  }
}

const toggleModelFileConfig = () => {
  showModelFileConfig.value = !showModelFileConfig.value
}

const toggleLicense = () => {
  showLicense.value = !showLicense.value
}

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

const getModelfileWithoutLicense = computed(() => {
  if (!modelDetails.value?.advanced_parameters?.modelfile) {
    return t('common.not_available')
  }
  
  // 如果已经单独显示License，则在modelfile中移除LICENSE相关内容
  if (modelDetails.value?.advanced_parameters?.license) {
    const modelfile = modelDetails.value.advanced_parameters.modelfile
    
    // 使用正则表达式移除LICENSE部分，包括被"""包裹的情况
    // 匹配 LICENSE 开头的行到下一个指令开始，包括被"""包裹的情况
    return modelfile.replace(/LICENSE\s+"""[\s\S]*?"""|LICENSE\s+.*?(?=\n\w+|\s*$)/gs, '')
      // 清理可能留下的多余空行
      .replace(/\n{3,}/g, '\n\n')
      .trim()
  }
  
  return modelDetails.value.advanced_parameters.modelfile
})

const showSystemPromptDialog = (promptContent: string) => {
  currentSystemPrompt.value = promptContent
  isSystemPromptDialogVisible.value = true
}

const closeSystemPromptDialog = () => {
  isSystemPromptDialogVisible.value = false
}

const truncateSystemPrompt = (text: string): string => {
  if (!text) return '-'
  
  // 将系统提示词截断为2行
  const lines = text.split('\n')
  if (lines.length <= 2) {
    return text
  }
  
  return lines.slice(0, 2).join('\n') + ' ...'
}

const formatSystemPrompt = (text: string): string => {
  if (!text) return ''
  
  // 对文本进行基本格式化，保持段落结构
  return text.trim()
    // 确保段落之间有一致的空行
    .replace(/\n{3,}/g, '\n\n')
    // 确保代码块和列表有适当的缩进
    .replace(/^(```[\s\S]*?```)/gm, '\n$1\n')
}
</script>

<style scoped>
@import '@/styles/ModelDetailPage.css';

</style>