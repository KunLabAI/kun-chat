import axios, { AxiosResponse } from 'axios'
import { API_URL } from './config'

// 认证相关的类型定义
export interface UserInfo {
  username: string
  nickname?: string
  email?: string
  avatar?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  username: string
  nickname?: string
  email?: string
  avatar?: string
}

export interface RegisterParams {
  username: string
  email: string
  password: string
  security_question: string
  security_answer: string
}

export interface RegisterResponse {
  access_token: string
  token_type: string
  username: string
  nickname?: string
  email?: string
  avatar?: string
}

export interface PasswordValidationResult {
  isValid: boolean
  errors: string[]
}

export interface PasswordRules {
  minLength: number
  maxLength: number
  allowedChars: string
}

// 创建axios实例
const authAxios = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
})

// 响应拦截器处理token刷新
authAxios.interceptors.response.use(
  (response) => {
    // 如果响应中包含新的token，更新本地存储
    if (response.data.token_refreshed) {
      localStorage.setItem('token', response.data.token)
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // 清除本地存储的token
      localStorage.removeItem('token')
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  async login(username: string, password: string): Promise<LoginResponse> {
    // 使用 URLSearchParams 来发送表单数据
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await authAxios.post('/auth/token', formData)
    return response.data
  },

  async register(params: RegisterParams): Promise<RegisterResponse> {
    const response = await axios.post(`${API_URL}/auth/register`, {
      username: params.username,
      password: params.password,
      email: params.email,
      security_question: params.security_question,
      security_answer: params.security_answer
    })
    return response.data
  },

  async getUserInfo(token: string): Promise<UserInfo> {
    try {
      // 使用fetchWithRetry替代直接的axios调用，增加重试机制
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        // 添加withCredentials确保跨域请求携带凭证
        withCredentials: true
      })
      return response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  },

  async autoLogin(token: string): Promise<LoginResponse> {
    try {
      const response = await axios.post(`${API_URL}/auth/auto-login`, 
        { token },
        {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          withCredentials: true
        }
      )
      return response.data
    } catch (error) {
      console.error('自动登录失败:', error)
      throw error
    }
  },

  async updateProfile(data: Partial<UserInfo>, token: string): Promise<UserInfo> {
    try {
      // 使用axios发送请求，确保一致的请求处理
      const response = await axios.put(
        `${API_URL}/auth/profile`,
        data,
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        }
      )
      return response.data
    } catch (error) {
      console.error('更新个人资料失败:', error)
      throw error
    }
  },

  async updatePassword(currentPassword: string, newPassword: string, token: string): Promise<any> {
    try {
      const response = await axios.post(
        `${API_URL}/auth/change-password`,
        {
          current_password: currentPassword,
          new_password: newPassword
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        }
      )
      return response.data
    } catch (error) {
      console.error('更新密码失败:', error)
      throw error
    }
  },

  async updateEmail(email: string, token: string): Promise<any> {
    try {
      const response = await axios.post(
        `${API_URL}/auth/update-email`,
        { email },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        }
      )
      return response.data
    } catch (error) {
      console.error('更新邮箱失败:', error)
      throw error
    }
  },

  // 获取用户偏好设置
  async getPreferences(token: string): Promise<any> {
    try {
      const response = await axios.get(
        `${API_URL}/auth/preferences`,
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        }
      )
      return response.data
    } catch (error) {
      console.error('获取用户偏好设置失败:', error)
      throw error
    }
  },

  // 更新用户偏好设置
  async updatePreferences(preferences: any, token: string): Promise<any> {
    try {
      const response = await axios.post(
        `${API_URL}/auth/preferences`,
        preferences,
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        }
      )
      return response.data
    } catch (error) {
      console.error('更新用户偏好设置失败:', error)
      throw error
    }
  },

  async updateAvatar(formData: FormData, token: string): Promise<any> {
    try {
      const response = await axios.post(
        `${API_URL}/auth/avatar`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
            'Accept': 'application/json'
          },
          withCredentials: true
        }
      )
      return response.data
    } catch (error) {
      console.error('更新头像失败:', error)
      throw error
    }
  },

  // 获取密码规则
  getPasswordRules(): PasswordRules {
    return {
      minLength: 6,
      maxLength: 20,
      allowedChars: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    }
  },

  // 验证密码强度
  validatePassword(password: string): PasswordValidationResult {
    const rules = this.getPasswordRules()
    const errors: string[] = []

    if (password.length < rules.minLength || password.length > rules.maxLength) {
      errors.push(`密码长度必须为${rules.minLength}-${rules.maxLength}个字符`)
    }

    if (![...password].every(c => rules.allowedChars.includes(c))) {
      errors.push('密码只能包含英文字母和数字')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  },

  async resetPassword(username: string, newPassword: string): Promise<any> {
    try {
      const response = await axios.post(
        `${API_URL}/auth/reset-password`,
        {
          username,
          new_password: newPassword
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        }
      )
      return response.data
    } catch (error: any) {
      console.error('重置密码失败:', error)
      throw new Error(error.response?.data?.detail || '重置密码失败')
    }
  },
}

export async function forgotPassword(email: string): Promise<any> {
  try {
    const response = await axios.post(
      `${API_URL}/auth/forgot-password`,
      { email },
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
    )
    return response.data
  } catch (error: any) {
    console.error('忘记密码请求失败:', error)
    throw new Error(error.response?.data?.message || '发送重置链接失败')
  }
}

export async function verifySecurityQuestion(username: string, answer: string | null = null): Promise<any> {
  try {
    const response = await axios.post(
      `${API_URL}/auth/verify-security-question`,
      { username, answer },
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
    )
    return response.data
  } catch (error: any) {
    console.error('验证安全问题失败:', error)
    throw new Error(error.response?.data?.detail || '验证失败')
  }
}

export async function verifyEmailForReset(username: string, email: string): Promise<any> {
  try {
    const response = await axios.post(
      `${API_URL}/auth/verify-email-reset`,
      { username, email },
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
    )
    return response.data
  } catch (error: any) {
    console.error('验证邮箱失败:', error)
    throw new Error(error.response?.data?.detail || '验证失败')
  }
}

export async function resetPassword(username: string, newPassword: string): Promise<any> {
  try {
    const response = await axios.post(
      `${API_URL}/auth/reset-password`,
      {
        username,
        new_password: newPassword
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
    )
    return response.data
  } catch (error: any) {
    console.error('重置密码失败:', error)
    throw new Error(error.response?.data?.detail || '重置密码失败')
  }
}
