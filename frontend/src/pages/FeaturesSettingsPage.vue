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

          <!-- 连接设置 -->
          <div v-show="currentTab === 'connection'" class="account-tab-pane">
            <!-- Ollama 连接管理设置 -->
            <OllamaSettings ref="ollamaSettingsRef" />
          </div>

          <!-- 网络设置 -->
          <div v-show="currentTab === 'network'" class="account-tab-pane">
            <!-- 网络设置组件 -->
            <NetworkSettings ref="networkSettingsRef" />
          </div>

          <!-- 工具设置 -->
          <div v-show="currentTab === 'tools'" class="account-tab-pane">
            <!-- Tavily 搜索设置 -->
            <TavilySettings ref="tavilySettingsRef" />
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import MainLayout from '@/layouts/MainLayout.vue'
import LanguageSwitcher from '@/components/common/LanguageSwitcher.vue'
import { useNotificationStore } from '@/stores/notification'
import { useThemeStore } from '@/stores/theme'
import { useRoute, useRouter } from 'vue-router'
import { useLocalization } from '@/i18n/composables'
import { SunIcon, MoonIcon, ComputerDesktopIcon } from '@heroicons/vue/24/solid'
import TavilySettings from '@/components/settings/TavilySettings.vue'
import OllamaSettings from '@/components/settings/OllamaSettings.vue'
import NetworkSettings from '@/components/settings/NetworkSettings.vue'

const { t } = useI18n()
const { language } = useLocalization()

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()
const themeStore = useThemeStore()
const tavilySettingsRef = ref(null)
const ollamaSettingsRef = ref(null)
const networkSettingsRef = ref(null)

// 标签页定义
const tabs = ref([
  { key: 'general', label: t('settings.tabs.general') },
  { key: 'connection', label: t('settings.tabs.connection') },
  { key: 'network', label: t('settings.tabs.network') },
  { key: 'tools', label: t('settings.tabs.tools') }
])

// 监听语言变化，更新标签页文本
watch(language, () => {
  tabs.value = [
    { key: 'general', label: t('settings.tabs.general') },
    { key: 'connection', label: t('settings.tabs.connection') },
    { key: 'network', label: t('settings.tabs.network') },
    { key: 'tools', label: t('settings.tabs.tools') }
  ]
})

// 当前标签页
const currentTab = ref(route.query.tab || 'general')

// 切换标签页并更新URL
const switchTab = (tab) => {
  currentTab.value = tab
  router.push({ query: { ...route.query, tab } })
}

// 监听路由变化，更新当前标签页
watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.value.some(tab => tab.key === newTab)) {
    currentTab.value = newTab
  }
})

// 在组件挂载时获取设置
onMounted(async () => {
  // 从URL获取当前标签页
  if (route.query.tab && tabs.value.some(tab => tab.key === route.query.tab)) {
    currentTab.value = route.query.tab
  }
  
  // 从数据库加载主题设置
  try {
    await themeStore.loadThemeFromDatabase()
  } catch (error) {
    console.error('从数据库加载主题设置失败:', error)
    notificationStore.showNotification({
      type: 'error',
      message: t('notifications.error.loadThemeSettings')
    })
  }
})
</script>

<style scoped>
@import '@/styles/FeaturesSettingsPage.css';
@import '@/styles/GeneralSettings.css';
</style>