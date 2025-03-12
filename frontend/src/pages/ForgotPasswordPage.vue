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
          <h1 class="auth-title">重置密码</h1>
          <p class="auth-subtitle">通过验证邮箱地址重置密码</p>
        </div>

        <form class="auth-form" @submit.prevent="handleSubmit">
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
                :disabled="step === 2"
              />
            </div>
          </div>

          <template v-if="step === 1">
            <div class="form-group">
              <label for="email" class="form-label">邮箱地址</label>
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
                  placeholder="请输入注册时使用的邮箱地址"
                />
              </div>
            </div>
          </template>

          <template v-if="step === 2">
            <div class="form-group">
              <label for="newPassword" class="form-label">新密码</label>
              <div class="relative">
                <span class="input-icon">
                  <img src="@/assets/icons/sys_password.svg" class="icon-image" alt="密码图标" />
                </span>
                <input
                  id="newPassword"
                  v-model="newPassword"
                  name="newPassword"
                  type="password"
                  required
                  class="form-input"
                  placeholder="请输入新密码"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">确认新密码</label>
              <div class="relative">
                <span class="input-icon">
                  <img src="@/assets/icons/sys_password.svg" class="icon-image" alt="密码图标" />
                </span>
                <input
                  id="confirmPassword"
                  v-model="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  class="form-input"
                  placeholder="请再次输入新密码"
                />
              </div>
            </div>
          </template>

          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="auth-button"
          >
            {{ buttonText }}
          </button>

          <div class="auth-divider">
            <div class="auth-divider-text">记起密码了？</div>
          </div>

          <router-link to="/login" class="auth-link">
            返回登录
          </router-link>
        </form>
      </div>
    </div>
    <footer class="auth-footer">
      2025 <a href="https://kunpuai.com" target="_blank" rel="noopener">鲲谱智能</a>, Inc. All rights reserved.
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { KeyIcon } from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import { verifyEmailForReset, resetPassword } from '@/api/auth'
import SolarSystem from '@/components/Solarsystem.vue'
import StarryBackground from '@/components/StarryBackground.vue'

const router = useRouter()
const notificationStore = useNotificationStore()

const step = ref(1)
const username = ref('')
const email = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)

const buttonText = computed(() => {
  if (loading.value) return '处理中...'
  return step.value === 1 ? '验证' : '重置密码'
})

const isFormValid = computed(() => {
  if (step.value === 1) {
    return username.value && email.value
  } else {
    return newPassword.value && 
           confirmPassword.value && 
           newPassword.value === confirmPassword.value &&
           newPassword.value.length >= 6
  }
})

const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  loading.value = true
  try {
    if (step.value === 1) {
      // 验证邮箱
      await verifyEmailForReset(username.value, email.value)
      notificationStore.showSuccess('验证成功，请设置新密码')
      step.value = 2
    } else {
      // 重置密码
      await resetPassword(username.value, newPassword.value)
      notificationStore.showSuccess('密码重置成功，请登录')
      router.push('/login')
    }
  } catch (error) {
    notificationStore.showError(error.message || '操作失败，请重试')
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

/* 图标样式 */
.icon-image {
  width: 1.25rem;
  height: 1.25rem;
  opacity: 0.7;
  filter: invert(70%);
}

/* 其他样式 */
.p-3 {
  padding: 0.75rem;
}

.rounded-lg {
  border-radius: 0.5rem;
}

.bg-primary-50 {
  background-color: rgba(168, 85, 247, 0.1);
}

.text-primary-700 {
  color: var(--primary-700);
}
</style>
