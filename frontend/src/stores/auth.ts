import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export interface User {
  id: string
  username: string
  email: string
  avatar?: string
  [key: string]: any
}

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<User>(JSON.parse(localStorage.getItem('user') || '{}'))
  const isAuthenticated = ref(!!token.value)
  const isLoading = ref(false)

  // 计算属性：获取用户头像，如果没有则使用默认头像
  const userAvatar = computed(() => {
    if (!user.value.avatar) return '/user_avatar.svg'
    
    // 统一处理头像URL格式
    if (user.value.avatar.startsWith('http') || user.value.avatar.startsWith('/static/')) {
      return user.value.avatar
    } else if (user.value.avatar.startsWith('/')) {
      // 确保以/开头的相对路径正确处理
      return import.meta.env.VITE_API_BASE_URL + user.value.avatar
    } else {
      // 其他情况，添加前缀
      return import.meta.env.VITE_API_BASE_URL + '/' + user.value.avatar
    }
  })

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    isAuthenticated.value = true
  }

  const setUser = (userData: User) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const updateUser = (updates: Partial<User>) => {
    const updatedUser = { ...user.value, ...updates }
    setUser(updatedUser)
  }

  const logout = () => {
    token.value = ''
    user.value = {} as User
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  return {
    token,
    user,
    isAuthenticated,
    userAvatar,
    isLoading,
    setToken,
    setUser,
    updateUser,
    logout,
    
    // 获取用户信息
    async fetchUserInfo() {
      try {
        isLoading.value = true
        const { authApi } = await import('@/api/auth')
        const userData = await authApi.getUserInfo(token.value)
        updateUser(userData)
        return userData
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      } finally {
        isLoading.value = false
      }
    }
  }
})