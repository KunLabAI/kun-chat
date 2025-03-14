<!-- 功能设置页面 -->
<template>
  <MainLayout>
    <div class="account-settings-page">
      <!-- 页面头部 -->
      <div class="account-page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="account-main-title">{{ $t('features.title') }}</h1>
            <p class="account-sub-title">{{ $t('features.subtitle') }}</p>
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="account-main-content">
        <!-- 页签导航 -->
        <div class="account-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.key"
            class="account-tab-item"
            :class="{ 'account-tab-item-active': currentTab === tab.key }"
            @click="switchTab(tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 页签内容 -->
        <div class="account-tab-content">
          <!-- 常规设置 -->
          <div v-show="currentTab === 'general'" class="account-tab-pane">
            <div class="account-settings-section">
              <h3 class="account-section-title">{{ $t('settings.features.title') }}</h3>
              <div class="account-section-content">
                <!-- 语言设置 -->
                <div class="features-form-group">
                  <label class="features-form-label">{{ $t('settings.general.language.title') }}</label>
                  <p class="features-form-help mb-4">
                    {{ $t('settings.general.language.description') }}
                  </p>
                  <LanguageSwitcher />
                </div>
                
                <!-- 主题设置 -->
                <div class="features-form-group mt-8">
                  <label class="features-form-label">{{ $t('settings.account.theme.title') }}</label>
                  <p class="features-form-help mb-4">
                    {{ $t('settings.account.theme.switch.description') }}
                  </p>
                  <div class="features-toggle-group">
                    <button 
                      @click="themeStore.setTheme('system')"
                      class="features-toggle-button"
                      :class="{ 'features-toggle-button-active': themeStore.themeSource === 'system' }"
                    >
                      <span class="flex items-center justify-center">
                        <ComputerDesktopIcon class="h-5 w-5 mr-2" />
                        {{ $t('settings.account.theme.switch.system') }}
                      </span>
                    </button>
                    <button 
                      @click="themeStore.setTheme('light')"
                      class="features-toggle-button"
                      :class="{ 'features-toggle-button-active': themeStore.themeSource === 'light' }"
                    >
                      <span class="flex items-center justify-center">
                        <SunIcon class="h-5 w-5 mr-2" />
                        {{ $t('settings.account.theme.switch.light') }}
                      </span>
                    </button>
                    <button 
                      @click="themeStore.setTheme('dark')"
                      class="features-toggle-button"
                      :class="{ 'features-toggle-button-active': themeStore.themeSource === 'dark' }"
                    >
                      <span class="flex items-center justify-center">
                        <MoonIcon class="h-5 w-5 mr-2" />
                        {{ $t('settings.account.theme.switch.dark') }}
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 工具设置 -->
          <div v-show="currentTab === 'tools'" class="account-tab-pane">
            <div class="account-settings-section">
              <h3 class="account-section-title">{{ $t('settings.tools.tavily.title') }}</h3>
              <div class="account-section-content">
                <p class="account-setting-description mb-4">
                  {{ $t('settings.tools.tavily.description') }}
                  <a href="https://tavily.com" target="_blank" class="text-primary-600 hover:underline">{{ $t('common.actions.learn_more') }}</a>
                </p>

                <!-- API密钥 -->
                <div class="features-form-group">
                  <label class="features-form-label">{{ $t('settings.tools.tavily.api_key.label') }}</label>
                  <div class="features-api-key-container">
                    <input 
                      :type="showApiKey ? 'text' : 'password'" 
                      v-model="tavilyApiKey"
                      class="features-form-input"
                      :disabled="loading.tavilyApiKey"
                      :placeholder="$t('settings.tools.tavily.api_key.placeholder')"
                    >
                    <div class="features-api-key-actions">
                      <button
                        v-if="tavilyApiKey"
                        @click="toggleShowApiKey"
                        class="features-api-key-action"
                        type="button"
                        :title="showApiKey ? '隐藏密钥' : '显示密钥'"
                      >
                        <i class="fas" :class="showApiKey ? 'fa-eye-slash' : 'fa-eye'"></i>
                      </button>
                      <button
                        v-if="tavilyApiKey"
                        @click="clearApiKey"
                        class="features-api-key-action"
                        type="button"
                        title="删除密钥"
                      >
                        <i class="fas fa-trash-alt"></i>
                      </button>
                      <Button
                        @click="updateTavilyApiKey"
                        :disabled="loading.tavilyApiKey"
                        :loading="loading.tavilyApiKey"
                        size="sm"
                      >
                        {{ $t('common.actions.save') }}
                      </Button>
                    </div>
                  </div>
                  <p v-if="tavilyApiKey && !showApiKey" class="features-form-help">
                    {{ $t('settings.tools.tavily.api_key.description') }}: {{ maskedApiKey }}
                  </p>
                </div>

                <!-- 搜索深度 -->
                <div class="features-form-group">
                  <label class="features-form-label">{{ $t('settings.tools.tavily.search_depth.label') }}</label>
                  <div class="features-toggle-group">
                    <button 
                      @click="selectSearchDepth('basic')"
                      class="features-toggle-button"
                      :class="{ 'features-toggle-button-active': tavilySearchDepth === 'basic' }"
                      :disabled="loading.tavilySettings"
                    >
                      {{ $t('settings.tools.tavily.search_depth.basic') }}
                    </button>
                    <button 
                      @click="selectSearchDepth('advanced')"
                      class="features-toggle-button"
                      :class="{ 'features-toggle-button-active': tavilySearchDepth === 'advanced' }"
                      :disabled="loading.tavilySettings"
                    >
                      {{ $t('settings.tools.tavily.search_depth.advanced') }}
                    </button>
                  </div>
                  <p class="features-form-help">
                    {{ $t('settings.tools.tavily.search_depth.description') }}
                  </p>
                </div>

                <!-- 测试连接 -->
                <div class="features-form-group">
                  <Button
                    @click="testTavilyConnection"
                    :disabled="!tavilyApiKey || loading.tavilyTest"
                    :loading="loading.tavilyTest"
                    variant="primary"
                  >
                    {{ $t('settings.tools.tavily.test_button') }}
                  </Button>
                  <p v-if="tavilyTestResult" 
                     class="features-form-help"
                     :class="tavilyTestResult.success ? 'text-green-600' : 'text-red-600'">
                    {{ tavilyTestResult.message }}
                  </p>
                </div>

                <!-- 包含域名 -->
                <div class="features-form-group">
                  <label class="features-form-label">{{ $t('settings.tools.tavily.include_domains.label') }}</label>
                  <p class="features-form-help mb-2">
                    {{ $t('settings.tools.tavily.include_domains.description') }}
                  </p>
                  
                  <div class="features-tags-container">
                    <div 
                      v-for="(domain, index) in includeDomains" 
                      :key="index"
                      class="features-tag"
                    >
                      {{ domain }}
                      <button 
                        @click="removeIncludeDomain(index)" 
                        class="features-tag-remove"
                        :disabled="loading.tavilySettings"
                      >
                        &times;
                      </button>
                    </div>
                  </div>
                  
                  <div class="features-input-group mt-2">
                    <input 
                      type="text" 
                      v-model="newIncludeDomain"
                      class="features-form-input"
                      :disabled="loading.tavilySettings"
                      :placeholder="$t('settings.tools.tavily.include_domains.placeholder')"
                      @keyup.enter="addIncludeDomainAndSave"
                    >
                  </div>
                </div>

                <!-- 排除域名 -->
                <div class="features-form-group mt-4">
                  <label class="features-form-label">{{ $t('settings.tools.tavily.exclude_domains.label') }}</label>
                  <p class="features-form-help mb-2">
                    {{ $t('settings.tools.tavily.exclude_domains.description') }}
                  </p>
                  
                  <div class="features-tags-container">
                    <div 
                      v-for="(domain, index) in excludeDomains" 
                      :key="index"
                      class="features-tag"
                    >
                      {{ domain }}
                      <button 
                        @click="removeExcludeDomain(index)" 
                        class="features-tag-remove"
                        :disabled="loading.tavilySettings"
                      >
                        &times;
                      </button>
                    </div>
                  </div>
                  
                  <div class="features-input-group mt-2">
                    <input 
                      type="text" 
                      v-model="newExcludeDomain"
                      class="features-form-input"
                      :disabled="loading.tavilySettings"
                      :placeholder="$t('settings.tools.tavily.exclude_domains.placeholder')"
                      @keyup.enter="addExcludeDomainAndSave"
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { getAuthHeaders } from '@/api/config'
import { useI18n } from 'vue-i18n'
import { ref, computed, onMounted, watch } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import LanguageSwitcher from '@/components/common/LanguageSwitcher.vue'
import { useNotificationStore } from '@/stores/notification'
import { useThemeStore } from '@/stores/theme'
import { toolsApi } from '@/api/tools'
import { useRoute, useRouter } from 'vue-router'
import Button from '@/components/common/Button.vue'
import { useLocalization } from '@/i18n/composables'
import { SunIcon, MoonIcon, ComputerDesktopIcon } from '@heroicons/vue/24/solid'

const { t } = useI18n()
const { language } = useLocalization()

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()
const themeStore = useThemeStore()

// 标签页定义
const tabs = [
  { key: 'general', label: t('settings.tabs.general') },
  { key: 'tools', label: t('settings.tabs.tools') }
]

// 当前标签页
const currentTab = ref(route.query.tab || 'general')

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

// 计算属性：显示部分隐藏的API密钥
const maskedApiKey = computed(() => {
  if (!tavilyApiKey.value) return ''
  const key = tavilyApiKey.value
  if (key.length <= 4) return key
  return key.substring(0, 4) + '•'.repeat(key.length - 4)
})

// 切换显示/隐藏API密钥
const toggleShowApiKey = () => {
  showApiKey.value = !showApiKey.value
}

// 清除API密钥
const clearApiKey = () => {
  tavilyApiKey.value = ''
}

// 切换标签页并更新URL
const switchTab = (tab) => {
  currentTab.value = tab
  router.push({ query: { ...route.query, tab } })
}

// 监听路由变化，更新当前标签页
watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.some(tab => tab.key === newTab)) {
    currentTab.value = newTab
  }
})

// 监听语言变化，更新标签页标签
watch(() => language.value, () => {
  tabs[0].label = t('settings.tabs.general')
  tabs[1].label = t('settings.tabs.tools')
})

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
  if (!tavilyApiKey.value) {
    notificationStore.warning('请输入API密钥')
    return
  }

  loading.value.tavilyApiKey = true
  try {
    await toolsApi.updateTavilySettings({ api_key: tavilyApiKey.value })
    notificationStore.success('API密钥更新成功')
  } catch (error) {
    console.error('更新API密钥失败:', error)
    notificationStore.error('更新API密钥失败')
  } finally {
    loading.value.tavilyApiKey = false
  }
}

// 选择并更新搜索深度
const selectSearchDepth = async (depth) => {
  if (tavilySearchDepth.value === depth) return
  
  tavilySearchDepth.value = depth
  loading.value.tavilySettings = true
  
  try {
    await toolsApi.updateTavilySettings({ search_depth: depth })
    notificationStore.success('搜索深度设置更新成功')
  } catch (error) {
    console.error('更新搜索深度失败:', error)
    notificationStore.error('更新搜索深度失败')
    // 恢复原来的设置
    tavilySearchDepth.value = depth === 'basic' ? 'advanced' : 'basic'
  } finally {
    loading.value.tavilySettings = false
  }
}

// 添加包含域名
const addIncludeDomain = () => {
  if (!newIncludeDomain.value) return
  if (!includeDomains.value.includes(newIncludeDomain.value)) {
    includeDomains.value.push(newIncludeDomain.value)
    newIncludeDomain.value = ''
  }
}

// 添加包含域名并保存
const addIncludeDomainAndSave = async () => {
  if (!newIncludeDomain.value) return
  
  if (!includeDomains.value.includes(newIncludeDomain.value)) {
    includeDomains.value.push(newIncludeDomain.value)
    
    // 立即保存
    loading.value.tavilySettings = true
    try {
      await toolsApi.updateTavilySettings({ include_domains: includeDomains.value })
      notificationStore.success('包含域名更新成功')
    } catch (error) {
      console.error('更新包含域名失败:', error)
      notificationStore.error('更新包含域名失败')
      // 恢复原来的设置
      includeDomains.value.pop()
    } finally {
      loading.value.tavilySettings = false
    }
  }
  
  newIncludeDomain.value = ''
}

// 移除包含域名
const removeIncludeDomain = async (index) => {
  const removedDomain = includeDomains.value[index]
  includeDomains.value.splice(index, 1)
  
  // 立即保存
  loading.value.tavilySettings = true
  try {
    await toolsApi.updateTavilySettings({ include_domains: includeDomains.value })
    notificationStore.success('包含域名更新成功')
  } catch (error) {
    console.error('更新包含域名失败:', error)
    notificationStore.error('更新包含域名失败')
    // 恢复原来的设置
    includeDomains.value.splice(index, 0, removedDomain)
  } finally {
    loading.value.tavilySettings = false
  }
}

// 添加排除域名
const addExcludeDomain = () => {
  if (!newExcludeDomain.value) return
  if (!excludeDomains.value.includes(newExcludeDomain.value)) {
    excludeDomains.value.push(newExcludeDomain.value)
    newExcludeDomain.value = ''
  }
}

// 添加排除域名并保存
const addExcludeDomainAndSave = async () => {
  if (!newExcludeDomain.value) return
  
  if (!excludeDomains.value.includes(newExcludeDomain.value)) {
    excludeDomains.value.push(newExcludeDomain.value)
    
    // 立即保存
    loading.value.tavilySettings = true
    try {
      await toolsApi.updateTavilySettings({ exclude_domains: excludeDomains.value })
      notificationStore.success('排除域名更新成功')
    } catch (error) {
      console.error('更新排除域名失败:', error)
      notificationStore.error('更新排除域名失败')
      // 恢复原来的设置
      excludeDomains.value.pop()
    } finally {
      loading.value.tavilySettings = false
    }
  }
  
  newExcludeDomain.value = ''
}

// 移除排除域名
const removeExcludeDomain = async (index) => {
  const removedDomain = excludeDomains.value[index]
  excludeDomains.value.splice(index, 1)
  
  // 立即保存
  loading.value.tavilySettings = true
  try {
    await toolsApi.updateTavilySettings({ exclude_domains: excludeDomains.value })
    notificationStore.success('排除域名更新成功')
  } catch (error) {
    console.error('更新排除域名失败:', error)
    notificationStore.error('更新排除域名失败')
    // 恢复原来的设置
    excludeDomains.value.splice(index, 0, removedDomain)
  } finally {
    loading.value.tavilySettings = false
  }
}

// 测试Tavily API连接
const testTavilyConnection = async () => {
  if (!tavilyApiKey.value) {
    notificationStore.warning('请先输入API密钥')
    return
  }

  loading.value.tavilyTest = true
  tavilyTestResult.value = null
  
  try {
    const result = await toolsApi.testTavilyConnection()
    tavilyTestResult.value = {
      success: true,
      message: '连接成功！API密钥有效。'
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    tavilyTestResult.value = {
      success: false,
      message: '连接失败，请检查API密钥是否正确。'
    }
  } finally {
    loading.value.tavilyTest = false
  }
}

// 在组件挂载时获取Tavily设置
onMounted(async () => {
  // 从URL获取当前标签页
  if (route.query.tab && tabs.some(tab => tab.key === route.query.tab)) {
    currentTab.value = route.query.tab
  }
  
  // 获取Tavily设置
  await fetchTavilySettings()
})
</script>

<style scoped>
@import '@/styles/FeaturesSettings.css';
@import '@/styles/AccountSettings.css'

</style>