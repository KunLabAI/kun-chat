<template>
  <div class="auth-container">
    <!-- 添加星空背景 -->
    <div class="auth-starry-background">
      <StarryBackground />
    </div>
    <div class="auth-solar-system">
      <SolarSystem>
      </SolarSystem>
    </div>
    <div class="auth-content">
      <div class="auth-card">
        <div class="auth-header">
          <h1 class="auth-title">创建kun-lab账号</h1>
          <p class="auth-subtitle">注册新账号以开始使用</p>
        </div>

        <form class="auth-form" @submit.prevent="handleRegister">
          <div class="form-group">
            <div class="relative">
              <span class="input-icon">
                <img src="@/assets/icons/sys_user.svg" class="icon-image" alt="用户图标" />
              </span>
              <input
                id="username"
                v-model="username"
                name="username"
                type="text"
                required
                class="form-input"
                placeholder="请输入用户名"
                @input="validateUsername"
                autocomplete="username"
              />
            </div>
            <div v-if="usernameError" class="email-error">
              <div class="password-requirement invalid">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ usernameError }}</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <div class="relative">
              <span class="input-icon">
                <img src="@/assets/icons/sys_mail.svg" class="icon-image" alt="邮箱图标" />
              </span>
              <input
                id="email"
                v-model="email"
                name="email"
                type="email"
                required
                class="form-input"
                placeholder="请输入邮箱"
                @input="validateEmail"
                autocomplete="email"
              />
            </div>
            <div v-if="emailError" class="email-error">
              <div class="password-requirement invalid">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ emailError }}</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <div class="relative">
              <span class="input-icon">
                <img src="@/assets/icons/sys_password.svg" class="icon-image" alt="密码图标" />
              </span>
              <input
                id="password"
                v-model="password"
                name="password"
                type="password"
                required
                class="form-input"
                placeholder="请输入密码"
                @input="validatePasswordInput"
                autocomplete="new-password"
              />
            </div>
            <!-- 密码要求提示 -->
            <div v-if="passwordErrors.length > 0" class="password-requirements">
              <div
                v-for="(error, index) in passwordErrors"
                :key="index"
                class="password-requirement invalid"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ error }}</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <div class="relative">
              <span class="input-icon">
                <img src="@/assets/icons/sys_password.svg" class="icon-image" alt="确认密码图标" />
              </span>
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                class="form-input"
                placeholder="请再次输入密码"
                @input="validateConfirmPassword"
                autocomplete="new-password"
              />
            </div>
            <div v-if="confirmPasswordError" class="email-error">
              <div class="password-requirement invalid">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ confirmPasswordError }}</span>
              </div>
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="auth-button"
          >
            {{ loading ? '注册中...' : '注册' }}
          </button>

          <div class="auth-divider">
            <div class="auth-divider-text">已有账号？</div>
          </div>

          <router-link to="/login" class="auth-link">
            返回登录
          </router-link>
        </form>
      </div>
    </div>
    <footer class="auth-footer">
      2025 <a href="https://kun-lab.com" target="_blank" rel="noopener">kun-lab</a>, Inc. All rights reserved.
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { UserPlusIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { authApi } from '@/api/auth'
import SolarSystem from '@/components/Solarsystem.vue'
import StarryBackground from '@/components/StarryBackground.vue'


const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const passwordErrors = ref([])
const emailError = ref('')
const confirmPasswordError = ref('')
const usernameError = ref('')

const validatePasswordInput = () => {
  const result = authApi.validatePassword(password.value)
  passwordErrors.value = result.errors
  
  // 如果确认密码已经有值，则同时验证确认密码
  if (confirmPassword.value) {
    validateConfirmPassword()
  }
}

const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value) {
    emailError.value = ''
  } else if (!emailRegex.test(email.value)) {
    emailError.value = '请输入有效的邮箱地址'
  } else {
    emailError.value = ''
  }
}

const validateConfirmPassword = () => {
  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = '两次输入的密码不一致'
  } else {
    confirmPasswordError.value = ''
  }
}

const validateUsername = () => {
  const usernameRegex = /^[a-zA-Z0-9]+$/
  if (!username.value) {
    usernameError.value = ''
  } else if (!usernameRegex.test(username.value)) {
    usernameError.value = '用户名只能包含英文字母和数字'
  } else {
    usernameError.value = ''
  }
}

const isFormValid = computed(() => {
  return (
    username.value &&
    !usernameError.value &&
    email.value &&
    !emailError.value &&
    password.value &&
    confirmPassword.value &&
    !confirmPasswordError.value &&
    passwordErrors.value.length === 0
  )
})

const handleRegister = async () => {
  // 再次验证邮箱和确认密码
  validateEmail()
  validateConfirmPassword()
  validateUsername()
  
  if (!isFormValid.value) {
    notificationStore.showError(emailError.value || confirmPasswordError.value || usernameError.value || '请填写所有必填项')
    return
  }

  if (password.value !== confirmPassword.value) {
    notificationStore.showError('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    const response = await authApi.register({
      username: username.value,
      email: email.value,
      password: password.value,
      security_question: securityQuestion.value,
      security_answer: securityAnswer.value
    })
    
    // 注册成功后自动登录
    authStore.setToken(response.access_token || response.token)
    authStore.setUser({
      username: response.username,
      nickname: response.nickname || response.username,
      email: response.email || '',
      avatar: response.avatar || ''
    })
    
    // 确保token被正确存储到localStorage
    localStorage.setItem('token', response.access_token || response.token)
    
    notificationStore.showSuccess('注册成功，欢迎使用kun-lab')
    
    router.push('/')
  } catch (error) {
    console.error('注册失败:', error)
    let errorMessage = '注册失败，请稍后重试'
    
    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail
      
      if (status === 400) {
        errorMessage = detail || '输入数据有误'
      } else if (status === 409) {
        errorMessage = '用户名或邮箱已被使用'
      }
    }
    
    notificationStore.showError(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import '@/styles/auth.css';

/* 确保太阳系组件在左侧2/3区域中央显示 */
.auth-solar-system :deep(.solar-system-container) {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 确保太阳系标题在正确位置 */
.auth-solar-system :deep(.overlay-text) {
  position: absolute;
  left: 50%; /* 将标题位置调整回太阳系区域中央 */
  transform: translateX(-50%);
}

/* 密码要求提示样式 */
.password-requirements {
  margin-top: 0.5rem;
  border-radius: 0.375rem;
  background-color: rgba(var(--bg-color-light-rgb), 0.5);
}

.password-requirement {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 0.25rem;
  font-size: 0.75rem;
}

.password-requirement.invalid {
  color: #ef4444;
}

.password-requirement.invalid svg {
  color: #ef4444;
}

.password-requirement.valid {
  color: #10b981;
}

.password-requirement.valid svg {
  color: #10b981;
}

/* 图标样式 */
.icon-image {
  width: 1.25rem;
  height: 1.25rem;
  opacity: 0.7;
  filter: invert(70%);
}

.email-error {
  margin-top: 0.5rem;
  border-radius: 0.375rem;
  background-color: rgba(var(--bg-color-light-rgb), 0.5);
}

.email-error div {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 0.25rem;
  font-size: 0.75rem;
  color: #ef4444;
}

.email-error svg {
  color: #ef4444;
}
</style>
