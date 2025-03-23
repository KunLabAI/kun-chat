<!-- 账户设置页面 -->
<template>
  <MainLayout>
    <div class="account-settings-page">
      <!-- 页面头部 -->
      <div class="account-page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="account-main-title">{{ $t('settings.account.title') }}</h1>
            <p class="account-sub-title">{{ $t('settings.account.subtitle') }}</p>
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
          <!-- 个人资料 -->
          <div v-show="currentTab === 'profile'" class="account-tab-pane">
            <div class="account-settings-section">
              <h3 class="account-section-title">{{ $t('settings.account.profile.title') }}</h3>
              <div class="account-section-content">
                <!-- 头像上传 -->
                <div class="account-avatar-section">
                  <div class="account-settings-avatar-container">
                    <img 
                      :src="avatarUrl" 
                      :alt="$t('settings.account.profile.avatar.alt')"
                      class="account-settings-avatar"
                    >
                    <label 
                      class="account-settings-avatar-upload"
                      :class="{ 'opacity-50 cursor-not-allowed': loading.avatar }"
                    >
                      <input 
                        type="file" 
                        class="hidden" 
                        accept="image/*"
                        @change="handleAvatarChange"
                        :disabled="loading.avatar"
                      >
                      <CameraIcon v-if="!loading.avatar" class="h-4 w-4" />
                      <ArrowUpTrayIcon v-else class="h-4 w-4 animate-spin" />
                    </label>
                  </div>
                  <div class="account-avatar-info">
                    <h4>{{ $t('settings.account.profile.avatar.title') }}</h4>
                    <p class="account-info-text">{{ $t('settings.account.profile.avatar.description') }}</p>
                  </div>
                </div>

                <!-- 用户信息表单 -->
                <div class="account-form-group">
                  <label class="account-form-label">{{ $t('settings.account.profile.username.label') }}</label>
                  <input 
                    type="text" 
                    v-model="username"
                    class="account-form-input"
                    disabled
                    :placeholder="$t('settings.account.profile.username.placeholder')"
                  >
                </div>

                <div class="account-form-group">
                  <label class="account-form-label">{{ $t('settings.account.profile.nickname.label') }}</label>
                  <div class="account-input-group">
                    <input
                      type="text"
                      v-model="nickname"
                      class="account-form-input"
                      :disabled="!isEditingNickname"
                      :placeholder="$t('settings.account.profile.nickname.placeholder')"
                    >
                    <button
                      v-if="!isEditingNickname"
                      @click="startEditNickname"
                      class="account-form-button"
                    >
                      {{ $t('common.actions.edit') }}
                    </button>
                    <button
                      v-else
                      @click="updateNickname"
                      class="account-form-button"
                      :disabled="loading.nickname"
                    >
                      {{ loading.nickname ? $t('status.loading') + '...' : $t('common.actions.update') }}
                    </button>
                  </div>
                </div>

                <div class="account-form-group">
                  <label class="account-form-label">{{ $t('settings.account.profile.email.label') }}</label>
                  <div class="account-input-group">
                    <input
                      type="email"
                      v-model="email"
                      class="account-form-input"
                      :disabled="!isEditingEmail"
                      :placeholder="$t('settings.account.profile.email.placeholder')"
                    >
                    <button
                      v-if="!isEditingEmail"
                      @click="startEditEmail"
                      class="account-form-button"
                    >
                      {{ $t('common.actions.edit') }}
                    </button>
                    <button
                      v-else
                      @click="updateEmailHandler"
                      class="account-form-button"
                      :disabled="loading.email"
                    >
                      {{ loading.email ? $t('status.loading') + '...' : $t('common.actions.update') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 安全设置 -->
          <div v-show="currentTab === 'security'" class="account-tab-pane">
            <div class="account-settings-section">
              <h3 class="account-section-title">{{ $t('settings.account.security.title') }}</h3>
              <div class="account-section-content">
                <form @submit.prevent="updatePassword" class="account-password-form">
                  <input 
                    type="text" 
                    :value="username" 
                    autocomplete="username" 
                    style="display: none;"
                  >
                  <div class="account-form-group">
                    <label class="account-form-label">{{ $t('settings.account.security.password.current.label') }}</label>
                    <input 
                      type="password" 
                      v-model="passwords.current"
                      class="account-form-input"
                      required
                      autocomplete="current-password"
                      :placeholder="$t('settings.account.security.password.current.placeholder')"
                    >
                  </div>
                  <div class="account-form-group">
                    <label class="account-form-label">{{ $t('settings.account.security.password.new.label') }}</label>
                    <input 
                      type="password" 
                      v-model="passwords.new"
                      class="account-form-input"
                      required
                      autocomplete="new-password"
                      :placeholder="$t('settings.account.security.password.new.placeholder')"
                      @input="validatePasswordInput"
                    >
                    <ul v-if="passwordErrors.length > 0" class="account-password-errors">
                      <li v-for="error in passwordErrors" :key="error">{{ error }}</li>
                    </ul>
                  </div>
                  <div class="account-form-group">
                    <label class="account-form-label">{{ $t('settings.account.security.password.confirm.label') }}</label>
                    <input 
                      type="password" 
                      v-model="passwords.confirm"
                      class="account-form-input"
                      required
                      autocomplete="new-password"
                      :placeholder="$t('settings.account.security.password.confirm.placeholder')"
                      @input="validateConfirmPassword"
                    >
                    <p v-if="confirmPasswordError" class="account-password-error">{{ confirmPasswordError }}</p>
                  </div>
                  <div class="account-form-actions">
                    <button
                      type="submit"
                      class="account-submit-button"
                      :class="{ 'opacity-50': !isPasswordValid || loading.password }"
                      :disabled="!isPasswordValid || loading.password"
                    >
                      <span v-if="!loading.password">{{ $t('common.actions.save') }}</span>
                      <span v-else class="account-loading-text">{{ $t('status.loading') }}...</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- 偏好设置 -->
          <div v-show="currentTab === 'preferences'" class="account-tab-pane">
            <div class="account-settings-section">
              <h3 class="account-section-title">{{ $t('settings.account.preferences.title') }}</h3>
              <div class="account-section-content">
                <!-- 偏好设置表单 -->
                <div class="account-preferences-form">
                  <!-- 个人偏好信息 -->
                  <div class="account-form-group">
                    <p class="account-form-help mb-2">
                      {{ $t('settings.account.preferences.personal_info.description') }}
                    </p>
                    <textarea 
                      v-model="personalInfo"
                      class="account-form-textarea"
                      rows="6"
                      :disabled="usePersonalInfo"
                      :placeholder="$t('settings.account.preferences.personal_info.placeholder')"
                    ></textarea>
                  </div>

                  <!-- 启用/关闭沉浸功能的一体化开关 -->
                  <div class="account-form-group">
                    <div class="account-immersive-switch">
                      <div class="switch-label-group">
                        <span class="switch-label">{{ $t('settings.account.preferences.use_personal_info.label') }}</span>
                        <div class="switch-status">
                          <span class="status-dot" :class="{ 'status-enabled': usePersonalInfo, 'status-disabled': !usePersonalInfo }"></span>
                          <span>{{ usePersonalInfo ? $t('common.status.enabled') : $t('common.status.disabled') }}</span>
                        </div>
                      </div>
                      <button
                        @click="togglePersonalInfo"
                        class="account-toggle-button"
                        :class="{ 'account-toggle-active': usePersonalInfo, 'account-toggle-loading': loading.preferences }"
                        :disabled="loading.preferences"
                      >
                        <span v-if="!loading.preferences">{{ usePersonalInfo ? $t('settings.account.preferences.disable_button') : $t('settings.account.preferences.enable_button') }}</span>
                        <span v-else class="account-loading-text">{{ $t('status.loading') }}</span>
                      </button>
                    </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { authApi } from '@/api/auth'
import { CameraIcon, ArrowUpTrayIcon } from '@heroicons/vue/24/solid'
import { API_BASE_URL } from '@/api/config'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const { t } = useI18n()

// 默认头像
const defaultAvatar = `${API_BASE_URL}/static/default-avatar.jpg`

// 标签页配置
const tabs = [
  { key: 'profile', label: t('settings.account.tabs.profile') },
  { key: 'security', label: t('settings.account.tabs.security') },
  { key: 'preferences', label: t('settings.account.tabs.preferences') }
]

// 当前选中的标签页
const currentTab = ref(route.query.tab || 'profile')

// 切换标签页并更新URL
function switchTab(tab) {
  currentTab.value = tab
  router.replace({ query: { ...route.query, tab } })
}

// 监听路由变化，更新当前标签页
watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.some(tab => tab.key === newTab)) {
    currentTab.value = newTab
  }
})

// 用户信息相关
const avatarUrl = computed(() => {
  if (authStore.user?.avatar) {
    // 检查是否是完整URL或相对路径
    if (authStore.user.avatar.startsWith('http')) {
      return authStore.user.avatar
    } else if (authStore.user.avatar.startsWith('/static/')) {
      // 直接使用API_BASE_URL，不需要再添加/api
      return `${API_BASE_URL}${authStore.user.avatar}`
    } else {
      // 添加API基础URL
      return `${API_BASE_URL}${authStore.user.avatar}`
    }
  }
  return defaultAvatar
})
const username = ref(authStore.user?.username || '')
const nickname = ref('')
const isEditingNickname = ref(false)
const email = ref('')
const isEditingEmail = ref(false)

const loading = ref({
  avatar: false,
  nickname: false,
  email: false,
  password: false,
  profile: false,
  preferences: false
})

// 密码相关
const passwords = ref({
  current: '',
  new: '',
  confirm: ''
})

// 密码错误提示
const passwordErrors = ref([])
const confirmPasswordError = ref('')

// 验证密码
const validatePasswordInput = () => {
  const result = authApi.validatePassword(passwords.value.new)
  passwordErrors.value = result.errors
  
  // 如果确认密码已经有值，则同时验证确认密码
  if (passwords.value.confirm) {
    validateConfirmPassword()
  }
}

// 验证确认密码
const validateConfirmPassword = () => {
  if (passwords.value.new !== passwords.value.confirm) {
    confirmPasswordError.value = '两次输入的密码不一致'
  } else {
    confirmPasswordError.value = ''
  }
}

const isPasswordValid = computed(() => {
  return passwordErrors.value.length === 0 && 
         passwords.value.new.length >= 6 && 
         passwords.value.new === passwords.value.confirm
})

const handleAvatarChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    loading.value.avatar = true
    
    // 压缩图片
    const compressedFile = await compressImage(file, 200, 200)
    
    const formData = new FormData()
    formData.append('avatar', compressedFile, file.name)

    const response = await authApi.updateAvatar(formData, authStore.token)
    
    // 确保头像URL包含完整的API基础URL
    let avatarUrl = response.avatar_url
    if (avatarUrl) {
      if (avatarUrl.startsWith('http')) {
        // 完整URL，直接使用
      } else if (avatarUrl.startsWith('/static/')) {
        // 静态文件路径，添加API_BASE_URL
        avatarUrl = `${API_BASE_URL}${avatarUrl}`
      } else {
        // 其他相对路径，添加API_BASE_URL
        avatarUrl = `${API_BASE_URL}${avatarUrl}`
      }
    }
    
    authStore.updateUser({ avatar: avatarUrl })
    notificationStore.success(t('settings.account.profile.avatar.success'))
  } catch (error) {
    console.error('Failed to update avatar:', error)
    notificationStore.error(t('settings.account.profile.avatar.error'))
  } finally {
    loading.value.avatar = false
  }
}

// 图片压缩函数
const compressImage = (file, maxWidth, maxHeight) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = (event) => {
      const img = new Image()
      img.src = event.target.result
      img.onload = () => {
        // 计算缩放比例
        let width = img.width
        let height = img.height
        
        if (width > height) {
          if (width > maxWidth) {
            height = Math.round((height * maxWidth) / width)
            width = maxWidth
          }
        } else {
          if (height > maxHeight) {
            width = Math.round((width * maxHeight) / height)
            height = maxHeight
          }
        }
        
        // 创建canvas并绘制压缩后的图片
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        
        // 转换为Blob
        canvas.toBlob((blob) => {
          // 创建新的文件对象
          const compressedFile = new File([blob], file.name, {
            type: file.type,
            lastModified: Date.now()
          })
          resolve(compressedFile)
        }, file.type, 0.8) // 0.8是压缩质量
      }
      img.onerror = (error) => {
        reject(error)
      }
    }
    reader.onerror = (error) => {
      reject(error)
    }
  })
}

const startEditNickname = () => {
  isEditingNickname.value = true
}

const updateNickname = async () => {
  if (!nickname.value) return

  try {
    loading.value.nickname = true
    await authApi.updateProfile({ nickname: nickname.value }, authStore.token)
    authStore.updateUser({ nickname: nickname.value })
    isEditingNickname.value = false
    notificationStore.success(t('settings.account.profile.nickname.success'))
  } catch (error) {
    console.error('Failed to update nickname:', error)
    notificationStore.error(t('settings.account.profile.nickname.error'))
  } finally {
    loading.value.nickname = false
  }
}

const startEditEmail = () => {
  isEditingEmail.value = true
}

const updateEmailHandler = async () => {
  if (!email.value) return

  try {
    loading.value.email = true
    await authApi.updateEmail(email.value, authStore.token)
    authStore.updateUser({ email: email.value })
    isEditingEmail.value = false
    notificationStore.success(t('settings.account.profile.email.success'))
  } catch (error) {
    console.error('Failed to update email:', error)
    notificationStore.error(t('settings.account.profile.email.error'))
  } finally {
    loading.value.email = false
  }
}

const updatePassword = async () => {
  if (!isPasswordValid.value) return

  try {
    loading.value.password = true
    await authApi.updatePassword(
      passwords.value.current,
      passwords.value.new,
      authStore.token
    )
    
    // 清空密码字段
    passwords.value = {
      current: '',
      new: '',
      confirm: ''
    }
    
    notificationStore.success(t('settings.account.security.password.success'))
  } catch (error) {
    console.error('Failed to update password:', error)
    notificationStore.error(t('settings.account.security.password.error'))
  } finally {
    loading.value.password = false
  }
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const userData = await authStore.fetchUserInfo()
    username.value = userData.username
    nickname.value = userData.nickname || ''
    email.value = userData.email || ''
    avatarUrl.value = userData.avatar || defaultAvatar
    
    // 获取用户偏好设置
    try {
      const preferencesData = await authApi.getPreferences(authStore.token)
      if (preferencesData) {
        personalInfo.value = preferencesData.personal_info || ''
        previousPersonalInfo.value = personalInfo.value // 初始化之前的个人偏好信息
        usePersonalInfo.value = preferencesData.use_personal_info || false
      }
    } catch (error) {
      console.error('获取用户偏好设置失败:', error)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    notificationStore.error('获取用户信息失败')
  }
}

// 在组件挂载时获取用户信息
onMounted(async () => {
  // 从URL获取当前标签页
  if (route.query.tab && tabs.some(tab => tab.key === route.query.tab)) {
    currentTab.value = route.query.tab
  }
  
  // 获取用户信息
  await fetchUserInfo()
})

// 偏好设置相关
const personalInfo = ref('')
const previousPersonalInfo = ref('') // 存储之前的个人偏好信息
const usePersonalInfo = ref(false)

// 切换个人偏好信息的启用状态
const togglePersonalInfo = async () => {
  try {
    loading.value.preferences = true
    
    if (!usePersonalInfo.value) {
      // 启用沉浸功能，保存当前输入的内容
      previousPersonalInfo.value = personalInfo.value
      
      await authApi.updatePreferences({
        personal_info: personalInfo.value,
        use_personal_info: true,
        nickname: nickname.value
      }, authStore.token)
      
      usePersonalInfo.value = true
      notificationStore.success(t('settings.account.preferences.enabled'))
    } else {
      // 关闭沉浸功能
      await authApi.updatePreferences({
        personal_info: personalInfo.value,
        use_personal_info: false,
        nickname: nickname.value
      }, authStore.token)
      
      usePersonalInfo.value = false
      notificationStore.success(t('settings.account.preferences.disabled'))
    }
  } catch (error) {
    console.error('更新偏好设置失败:', error)
    notificationStore.error(t('settings.account.preferences.error'))
  } finally {
    loading.value.preferences = false
  }
}
</script>

<style scoped>
/* 导入账户设置样式 */
@import '@/styles/FeaturesSettingsPage.css';

/* 密码错误提示样式 */
.account-password-errors {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
  list-style-type: disc;
  color: #e53e3e;
  font-size: 0.875rem;
}

.account-password-error {
  margin-top: 0.5rem;
  color: #e53e3e;
  font-size: 0.875rem;
}

/* 状态圆点样式 */
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.status-enabled {
  background-color: #34c759;
}

.status-disabled {
  background-color: #e53e3e;
}
</style>
