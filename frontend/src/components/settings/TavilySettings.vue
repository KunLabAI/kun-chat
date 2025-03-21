<!-- Tavily搜索设置组件 -->
<template>
  <div class="tavily-settings-section">
    <h3 class="tavily-section-title">{{ $t('settings.tools.tavily.title') }}</h3>
    <div class="tavily-section-content">
      <p class="tavily-setting-description mb-4">
        {{ $t('settings.tools.tavily.description') }}
        <a href="https://tavily.com" target="_blank" class="text-primary-600 hover:underline">{{ $t('common.actions.learn_more') }}</a>
      </p>

      <!-- API密钥 -->
      <div class="tavily-features-form-group">
        <label class="tavily-features-form-label">{{ $t('settings.tools.tavily.api_key.label') }}</label>
        <div class="tavily-features-api-key-container">
          <input 
            :type="showApiKey ? 'text' : 'password'" 
            v-model="tavilyApiKey"
            class="tavily-features-form-input"
            :disabled="loading.tavilyApiKey"
            :placeholder="$t('settings.tools.tavily.api_key.placeholder')"
          >
          <div class="tavily-features-api-key-actions">
            <button
              @click="toggleShowApiKey"
              class="tavily-features-api-key-action"
              type="button"
              :title="showApiKey ? '隐藏密钥' : '显示密钥'"
              :disabled="!tavilyApiKey || tavilyApiKey.trim() === ''"
              :class="{ 'tavily-features-api-key-action-disabled': !tavilyApiKey || tavilyApiKey.trim() === '' }"
            >
              <img :src="showApiKey ? eyeOffIcon : eyeOnIcon" alt="toggle visibility" />
            </button>
            <button
              @click="clearApiKey"
              class="tavily-features-api-key-action"
              type="button"
              title="删除密钥"
              :disabled="!tavilyApiKey || tavilyApiKey.trim() === ''"
              :class="{ 'tavily-features-api-key-action-disabled': !tavilyApiKey || tavilyApiKey.trim() === '' }"
            >
              <img :src="deleteIcon" alt="clear" />
            </button>
            <button
              @click="updateTavilyApiKey"
              class="tavily-features-api-key-action"
              :disabled="loading.tavilyApiKey"
              :title="$t('common.actions.save')"
            >
              <img v-if="!loading.tavilyApiKey" :src="saveIcon" alt="save" />
              <div v-else class="tavily-loader-container">
                <DotLoader />
              </div>
            </button>
          </div>
        </div>
        <p class="tavily-features-form-hint">
          {{ $t('settings.tools.tavily.apiKeyHint') }}
        </p>
      </div>
      
      <!-- 测试连接 -->
      <div class="tavily-features-form-group">
        <Button
          @click="testTavilyConnection"
          class="tavily-features-test-button"
          :disabled="!tavilyApiKey || loading.tavilyTest"
          :loading="false"
          variant="secondary"
          size="sm"
        >
          <template v-if="loading.tavilyTest">
            <div class="tavily-button-loader">
              <DotLoader />
            </div>
          </template>
          <template v-else>
            {{ $t('settings.tools.tavily.test_button') }}
          </template>
        </Button>
        <p v-if="tavilyTestResult" 
           :class="tavilyTestResult.success ? 'text-green-600' : 'text-red-600'"
           class="text-sm mt-2">
          {{ tavilyTestResult.message }}
        </p>
      </div>

      <!-- 搜索深度 -->
      <div class="tavily-features-form-group">
        <label class="tavily-features-form-label">{{ $t('settings.tools.tavily.search_depth.label') }}</label>
        <div class="tavily-features-toggle-group">
          <button 
            @click="selectSearchDepth('basic')"
            class="tavily-features-toggle-button"
            :class="{ 'tavily-features-toggle-button-active': tavilySearchDepth === 'basic' }"
            :disabled="loading.tavilySettings"
          >
            {{ $t('settings.tools.tavily.search_depth.basic') }}
          </button>
          <button 
            @click="selectSearchDepth('advanced')"
            class="tavily-features-toggle-button"
            :class="{ 'tavily-features-toggle-button-active': tavilySearchDepth === 'advanced' }"
            :disabled="loading.tavilySettings"
          >
            {{ $t('settings.tools.tavily.search_depth.advanced') }}
          </button>
        </div>
      </div>

      <!-- 包含域名 -->
      <div class="tavily-features-form-group">
        <label class="tavily-features-form-label">{{ $t('settings.tools.tavily.include_domains.label') }}</label>
        
        <div class="tavily-features-tags-container">
          <div 
            v-for="(domain, index) in includeDomains" 
            :key="index"
            class="tavily-features-tag"
          >
            {{ domain }}
            <button 
              @click="removeIncludeDomain(index)" 
              class="tavily-features-tag-remove"
              :disabled="loading.tavilySettings"
            >
              &times;
            </button>
          </div>
        </div>
        
        <div class="tavily-features-input-group mt-2">
          <input 
            type="text" 
            v-model="newIncludeDomain"
            class="tavily-features-form-input"
            :class="{ 'border-red-500': newIncludeDomain && !isValidDomain(newIncludeDomain) }"
            :disabled="loading.tavilySettings"
            :placeholder="$t('settings.tools.tavily.include_domains.placeholder')"
            @keyup.enter="addIncludeDomainAndSave"
            @input="validateIncludeDomain"
          >
          <p v-if="newIncludeDomain && !isValidDomain(newIncludeDomain)" class="text-red-500 text-xs mt-1">
            请输入有效的域名格式
          </p>
        </div>
      </div>

      <!-- 排除域名 -->
      <div class="tavily-features-form-group mt-4">
        <label class="tavily-features-form-label">{{ $t('settings.tools.tavily.exclude_domains.label') }}</label>
        
        <div class="tavily-features-tags-container">
          <div 
            v-for="(domain, index) in excludeDomains" 
            :key="index"
            class="tavily-features-tag"
          >
            {{ domain }}
            <button 
              @click="removeExcludeDomain(index)" 
              class="tavily-features-tag-remove"
              :disabled="loading.tavilySettings"
            >
              &times;
            </button>
          </div>
        </div>
        
        <div class="tavily-features-input-group mt-2">
          <input 
            type="text" 
            v-model="newExcludeDomain"
            class="tavily-features-form-input"
            :class="{ 'border-red-500': newExcludeDomain && !isValidDomain(newExcludeDomain) }"
            :disabled="loading.tavilySettings"
            :placeholder="$t('settings.tools.tavily.exclude_domains.placeholder')"
            @keyup.enter="addExcludeDomainAndSave"
            @input="validateExcludeDomain"
          >
          <p v-if="newExcludeDomain && !isValidDomain(newExcludeDomain)" class="text-red-500 text-xs mt-1">
            请输入有效的域名格式
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useNotificationStore } from '@/stores/notification'
import { toolsApi } from '@/api/tools'
import Button from '@/components/common/Button.vue'
import DotLoader from '@/components/common/DotLoader.vue'
import eyeOnIcon from '@/assets/icons/sys_eyeon.svg'
import eyeOffIcon from '@/assets/icons/sys_eyeoff.svg'
import deleteIcon from '@/assets/icons/model_delete.svg'
import saveIcon from '@/assets/icons/sys_save.svg'

const { t } = useI18n()
const notificationStore = useNotificationStore()

// 加载状态
const loading = ref({
  tavilyApiKey: false,
  tavilySettings: false,
  tavilyTest: false
})

// Tavily 设置
const tavilyApiKey = ref('')
const showApiKey = ref(false)
const tavilySearchDepth = ref('basic')
const includeDomains = ref([])
const excludeDomains = ref([])
const newIncludeDomain = ref('')
const newExcludeDomain = ref('')
const tavilyTestResult = ref(null)

// 切换显示/隐藏API密钥
const toggleShowApiKey = () => {
  showApiKey.value = !showApiKey.value
}

// 清除API密钥
const clearApiKey = async () => {
  if (loading.value.tavilyApiKey) return
  
  loading.value.tavilyApiKey = true
  
  try {
    tavilyApiKey.value = ''
    
    // 发送空字符串到后端，清除API密钥
    await toolsApi.updateTavilySettings({
      api_key: ''
    })
    notificationStore.success('API密钥已清除')
  } catch (error) {
    console.error('清除API密钥失败:', error)
    notificationStore.error('清除API密钥失败')
    
    // 恢复原值
    await fetchTavilySettings()
  } finally {
    loading.value.tavilyApiKey = false
  }
}

// 获取Tavily API设置
const fetchTavilySettings = async () => {
  try {
    const settings = await toolsApi.getTavilySettings()
    if (settings) {
      tavilyApiKey.value = settings.api_key || ''
      tavilySearchDepth.value = settings.search_depth || 'basic'
      includeDomains.value = Array.isArray(settings.include_domains) 
        ? settings.include_domains 
        : (settings.include_domains ? settings.include_domains.split(',') : [])
      excludeDomains.value = Array.isArray(settings.exclude_domains) 
        ? settings.exclude_domains 
        : (settings.exclude_domains ? settings.exclude_domains.split(',') : [])
    }
  } catch (error) {
    console.error('获取Tavily设置失败:', error)
    notificationStore.error('获取Tavily设置失败，请稍后重试')
    
    // 设置默认值，避免界面显示异常
    tavilyApiKey.value = ''
    tavilySearchDepth.value = 'basic'
    includeDomains.value = []
    excludeDomains.value = []
  }
}

// 更新Tavily API密钥
const updateTavilyApiKey = async () => {
  if (!tavilyApiKey.value || tavilyApiKey.value.trim() === '') {
    notificationStore.error('请输入有效的API密钥')
    return
  }
  
  loading.value.tavilyApiKey = true
  console.log('开始保存Tavily API密钥')
  
  try {
    // 只发送需要更新的字段
    const result = await toolsApi.updateTavilySettings({
      api_key: tavilyApiKey.value
    })
    console.log('API密钥保存成功:', result)
    notificationStore.success('API密钥已保存，请点击"测试连接"按钮验证其有效性')
    showApiKey.value = false
    
    // 更新完成后重新加载设置
    await fetchTavilySettings()
  } catch (error) {
    console.error('保存API密钥失败:', error)
    notificationStore.error('保存API密钥失败，请稍后重试')
  } finally {
    loading.value.tavilyApiKey = false
  }
}

// 选择并更新搜索深度
const selectSearchDepth = async (depth) => {
  if (tavilySearchDepth.value === depth) return
  
  const originalDepth = tavilySearchDepth.value
  tavilySearchDepth.value = depth
  loading.value.tavilySettings = true
  
  try {
    // 只发送需要更新的字段
    await toolsApi.updateTavilySettings({
      search_depth: depth
    })
    notificationStore.success('搜索深度更新成功')
  } catch (error) {
    console.error('更新搜索深度失败:', error)
    notificationStore.error('更新搜索深度失败')
    
    // 恢复原值
    tavilySearchDepth.value = originalDepth
  } finally {
    loading.value.tavilySettings = false
  }
}

// 验证域名格式
const isValidDomain = (domain) => {
  // 域名格式验证正则表达式
  const domainRegex = /^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$/i;
  return domainRegex.test(domain);
}

// 添加包含域名
const addIncludeDomain = () => {
  if (!newIncludeDomain.value) return
  
  if (!includeDomains.value.includes(newIncludeDomain.value)) {
    includeDomains.value.push(newIncludeDomain.value)
  }
  newIncludeDomain.value = ''
}

// 添加包含域名并保存
const addIncludeDomainAndSave = async () => {
  if (!newIncludeDomain.value) return
  
  if (includeDomains.value.includes(newIncludeDomain.value)) {
    notificationStore.warning('该域名已存在')
    return
  }
  
  loading.value.tavilySettings = true
  
  try {
    includeDomains.value.push(newIncludeDomain.value)
    
    // 只发送需要更新的字段
    await toolsApi.updateTavilySettings({
      include_domains: includeDomains.value
    })
    notificationStore.success('包含域名更新成功')
    newIncludeDomain.value = ''
  } catch (error) {
    console.error('更新包含域名失败:', error)
    notificationStore.error('更新包含域名失败')
    
    // 恢复原值
    includeDomains.value.pop()
  } finally {
    loading.value.tavilySettings = false
  }
}

// 移除包含域名
const removeIncludeDomain = async (index) => {
  if (loading.value.tavilySettings) return
  
  loading.value.tavilySettings = true
  
  try {
    const removedDomain = includeDomains.value[index]
    includeDomains.value.splice(index, 1)
    
    // 只发送需要更新的字段
    await toolsApi.updateTavilySettings({
      include_domains: includeDomains.value
    })
    notificationStore.success('包含域名更新成功')
  } catch (error) {
    console.error('更新包含域名失败:', error)
    notificationStore.error('更新包含域名失败')
    
    // 恢复原值
    await fetchTavilySettings()
  } finally {
    loading.value.tavilySettings = false
  }
}

// 添加排除域名
const addExcludeDomain = () => {
  if (!newExcludeDomain.value) return
  
  if (!excludeDomains.value.includes(newExcludeDomain.value)) {
    excludeDomains.value.push(newExcludeDomain.value)
  }
  newExcludeDomain.value = ''
}

// 添加排除域名并保存
const addExcludeDomainAndSave = async () => {
  if (!newExcludeDomain.value) return
  
  if (excludeDomains.value.includes(newExcludeDomain.value)) {
    notificationStore.warning('该域名已存在')
    return
  }
  
  loading.value.tavilySettings = true
  
  try {
    excludeDomains.value.push(newExcludeDomain.value)
    
    // 只发送需要更新的字段
    await toolsApi.updateTavilySettings({
      exclude_domains: excludeDomains.value
    })
    notificationStore.success('排除域名更新成功')
    newExcludeDomain.value = ''
  } catch (error) {
    console.error('更新排除域名失败:', error)
    notificationStore.error('更新排除域名失败')
    
    // 恢复原值
    excludeDomains.value.pop()
  } finally {
    loading.value.tavilySettings = false
  }
}

// 移除排除域名
const removeExcludeDomain = async (index) => {
  if (loading.value.tavilySettings) return
  
  loading.value.tavilySettings = true
  
  try {
    const removedDomain = excludeDomains.value[index]
    excludeDomains.value.splice(index, 1)
    
    // 只发送需要更新的字段
    await toolsApi.updateTavilySettings({
      exclude_domains: excludeDomains.value
    })
    notificationStore.success('排除域名更新成功')
  } catch (error) {
    console.error('更新排除域名失败:', error)
    notificationStore.error('更新排除域名失败')
    
    // 恢复原值
    await fetchTavilySettings()
  } finally {
    loading.value.tavilySettings = false
  }
}

// 测试Tavily API连接
const testTavilyConnection = async () => {
  if (!tavilyApiKey.value) {
    notificationStore.warning('请先设置API密钥')
    return
  }
  
  loading.value.tavilyTest = true
  tavilyTestResult.value = null
  
  try {
    console.log('开始测试Tavily API连接')
    const result = await toolsApi.testTavilyConnection()
    console.log('Tavily API连接测试结果:', result)
    
    tavilyTestResult.value = {
      success: true,
      message: '连接测试成功，API密钥有效'
    }
    notificationStore.success('API密钥验证成功')
  } catch (error) {
    console.error('测试Tavily API连接失败:', error)
    
    // 提取详细的错误信息
    let errorMessage = '连接测试失败'
    
    if (error.response && error.response.data && error.response.data.detail) {
      // 直接使用后端返回的友好错误消息
      errorMessage = error.response.data.detail
    } else if (error.detail) {
      // 兼容旧的错误格式
      errorMessage = error.detail
    } else if (error.message) {
      // 如果没有详细信息，则使用一般错误消息
      errorMessage = error.message
    }
    
    tavilyTestResult.value = {
      success: false,
      message: errorMessage
    }
    notificationStore.error(errorMessage)
  } finally {
    loading.value.tavilyTest = false
  }
}

// 暴露方法给父组件
defineExpose({
  fetchTavilySettings
})

// 在组件挂载时获取Tavily设置
onMounted(async () => {
  await fetchTavilySettings()
})
</script>

<style scoped>
@import './TavilySettings.css';
</style>
