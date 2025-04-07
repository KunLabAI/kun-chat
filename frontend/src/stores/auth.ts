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

// 定义本地存储键名前缀，便于用户隔离
const STORAGE_KEY_PREFIX = 'kunlab_user_'
const LAST_LOGGED_USER_KEY = 'kunlab_last_user'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  // 获取最后登录的用户名
  const lastLoggedUsername = localStorage.getItem(LAST_LOGGED_USER_KEY) || ''
  // 根据最后登录用户获取对应token
  const token = ref(lastLoggedUsername 
    ? localStorage.getItem(`${STORAGE_KEY_PREFIX}token_${lastLoggedUsername}`) || '' 
    : '')
  // 根据最后登录用户获取对应用户信息
  const user = ref<User>(lastLoggedUsername 
    ? JSON.parse(localStorage.getItem(`${STORAGE_KEY_PREFIX}user_${lastLoggedUsername}`) || '{}') 
    : {} as User)
  const isAuthenticated = ref(false)
  const isLoading = ref(false)

  // 获取用户信息
  async function fetchUserInfo() {
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

  // 初始化时验证token
  const initAuth = async () => {
    if (token.value) {
      try {
        await fetchUserInfo()
        isAuthenticated.value = true
      } catch (error) {
        console.error('Token验证失败:', error)
        logout()
      }
    }
  }

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
    // 如果有用户名，则使用用户名关联保存token
    if (user.value.username) {
      localStorage.setItem(`${STORAGE_KEY_PREFIX}token_${user.value.username}`, newToken)
      // 记录最后登录的用户
      localStorage.setItem(LAST_LOGGED_USER_KEY, user.value.username)
    }
    isAuthenticated.value = true
  }

  const setUser = (userData: User) => {
    user.value = userData
    // 保存用户信息到特定用户的存储位置
    if (userData.username) {
      localStorage.setItem(`${STORAGE_KEY_PREFIX}user_${userData.username}`, JSON.stringify(userData))
      // 记录最后登录的用户
      localStorage.setItem(LAST_LOGGED_USER_KEY, userData.username)
    }
  }

  const updateUser = (updates: Partial<User>) => {
    const updatedUser = { ...user.value, ...updates }
    setUser(updatedUser)
  }

  const logout = () => {
    // 保留当前用户名，仅用于清除对应用户的token
    const currentUsername = user.value.username
    
    console.log('开始登出处理:', { currentUsername })
    
    token.value = ''
    user.value = {} as User
    isAuthenticated.value = false
    
    // 清除旧版token
    localStorage.removeItem('token')
    console.log('已清除旧版token')
    
    // 如果有当前用户名，则只清除该用户的token
    if (currentUsername) {
      localStorage.removeItem(`${STORAGE_KEY_PREFIX}token_${currentUsername}`)
      localStorage.removeItem(`${STORAGE_KEY_PREFIX}user_${currentUsername}`)
      // 清除最后登录用户记录
      localStorage.removeItem(LAST_LOGGED_USER_KEY)
      console.log('已清除用户特定信息:', currentUsername)
    }
    
    console.log('登出完成，重定向到登录页')
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
    initAuth,
    fetchUserInfo
  }
})