<template>
  <div class="auth-container">
    <!-- 星空背景 -->
    <div class="auth-starry-background">
      <StarryBackground />
    </div>
    <!-- 太阳系 -->
    <div class="auth-solar-system">
      <SolarSystem>
      </SolarSystem>
    </div>
    <div class="auth-content">
      <div class="auth-card">
        <div class="auth-header">
          <h1 class="auth-title">欢迎使用kun-lab</h1>
          <p class="auth-subtitle">登录您的账号以继续使用</p>
        </div>

        <form class="auth-form" @submit.prevent="handleLogin">
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
                autocomplete="username"
              />
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
                autocomplete="current-password"
              />
            </div>
            <div class="flex justify-end">
              <router-link to="/forgot-password" class="text-sm text-primary-500 hover:text-primary-600 hover:underline">
                忘记密码？
              </router-link>
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="auth-button"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>

          <div class="auth-divider">
            <div class="auth-divider-text">还没有账号？</div>
          </div>

          <router-link to="/register" class="auth-link">
            立即注册新账号
          </router-link>
        </form>
      </div>
    </div>
    <footer class="auth-footer">
      2025 <a href="https://kunpuai.com" target="_blank" rel="noopener">KunpuAI</a>, Inc. All rights reserved.
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { LockClosedIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { authApi } from '@/api/auth'
import SolarSystem from '@/components/Solarsystem.vue'
import StarryBackground from '@/components/StarryBackground.vue'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

const isFormValid = computed(() => username.value && password.value)

// 尝试自动登录
const tryAutoLogin = async () => {
  const token = localStorage.getItem('token')
  // 检查是否是第一次启动应用，如果是，则不进行自动登录
  const isFirstLaunch = localStorage.getItem('firstLaunch') !== 'false'
  
  if (token && !isFirstLaunch) {
    try {
      loading.value = true
      const response = await authApi.autoLogin(token)
      
      // 更新token（如果被刷新）和用户信息
      authStore.setToken(response.token)
      authStore.setUser({
        username: response.username,
        nickname: response.nickname || response.username,
        email: response.email || '',
        avatar: response.avatar || ''
      })
      
      router.push('/')
    } catch (err) {
      console.error('自动登录失败:', err)
      localStorage.removeItem('token')
    } finally {
      loading.value = false
    }
  } else if (isFirstLaunch) {
    // 标记应用已经启动过
    localStorage.setItem('firstLaunch', 'false')
  }
}

// 组件加载时尝试自动登录
onMounted(() => {
  tryAutoLogin()
})

async function handleLogin() {
  if (!isFormValid.value) {
    notificationStore.showError('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const response = await authApi.login(username.value, password.value)
    
    // 保存token和用户信息到store
    authStore.setToken(response.access_token)
    authStore.setUser({
      username: response.username,
      nickname: response.nickname || response.username,
      email: response.email || '',
      avatar: response.avatar || ''
    })

    // 确保token被正确存储到localStorage
    localStorage.setItem('token', response.access_token)

    // 显示成功消息
    notificationStore.showSuccess('登录成功')

    // 等待状态更新完成后再跳转
    await nextTick()
    await router.push({ name: 'home', replace: true })
  } catch (error) {
    console.error('登录失败:', error)
    let errorMessage = '登录失败，请稍后重试'
    
    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail
      
      if (status === 401) {
        errorMessage = '用户名或密码错误'
      } else if (status === 422) {
        errorMessage = detail || '输入格式有误'
      } else if (status === 404) {
        errorMessage = '用户不存在'
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

/* 使用主题色变量 */
.text-primary-500 {
  color: var(--gray-500);
}

.hover\:text-primary-600:hover {
  color: var(--primary-600);
}

/* 图标样式 */
.icon-image {
  width: 1.25rem;
  height: 1.25rem;
  opacity: 0.7;
  filter: invert(70%);
}
</style>
