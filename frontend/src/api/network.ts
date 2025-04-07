import { API_BASE_URL, fetchWithRetry, getApiUrl } from './config'

// 网络接口类型
interface NetworkInterface {
  name: string
  address: string
}

// 网络设置类型
interface NetworkSettings {
  appUrl: string
  lanAccess: boolean
  lanAccessStatus: boolean
  lanUrls: string[]
}

// 局域网地址响应类型
interface LanUrlsResponse {
  urls: string[]
  status: boolean
}

// 网络 API
const networkApi = {
  /**
   * 获取网络设置
   * @returns {Promise<NetworkSettings>} 网络设置信息
   */
  async getNetworkSettings(): Promise<NetworkSettings> {
    try {
      const apiUrl = await getApiUrl();
      const response = await fetchWithRetry(`${apiUrl}/network/network/settings`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      const data = await response.json()
      return data
    } catch (error) {
      console.error('获取网络设置失败:', error)
      // 如果 API 不可用，返回默认值
      return {
        appUrl: '',
        lanAccess: false,
        lanAccessStatus: false,
        lanUrls: []
      }
    }
  },

  /**
   * 更新局域网访问设置
   * @param {boolean} enabled - 是否启用局域网访问
   * @returns {Promise<{success: boolean}>} 更新结果
   */
  async updateLanAccess(enabled: boolean): Promise<{success: boolean}> {
    try {
      const apiUrl = await getApiUrl();
      const response = await fetchWithRetry(`${apiUrl}/network/network/lan-access`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled }),
      })
      const data = await response.json()
      return data
    } catch (error) {
      console.error('更新局域网访问设置失败:', error)
      return { success: false }
    }
  },

  /**
   * 获取局域网地址列表
   * @returns {Promise<LanUrlsResponse>} 局域网地址信息
   */
  async getLanUrls(): Promise<LanUrlsResponse> {
    try {
      const apiUrl = await getApiUrl();
      const response = await fetchWithRetry(`${apiUrl}/network/network/lan-urls`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      const data = await response.json()
      return data
    } catch (error) {
      console.error('获取局域网地址失败:', error)
      return {
        urls: [],
        status: false
      }
    }
  },
  
  /**
   * 获取所有网络接口地址
   * @returns {Promise<NetworkInterface[]>} 网络接口地址列表
   */
  async getAllNetworkInterfaces(): Promise<NetworkInterface[]> {
    try {
      const apiUrl = await getApiUrl();
      const response = await fetchWithRetry(`${apiUrl}/network/network/interfaces`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      const data = await response.json()
      return data.interfaces || []
    } catch (error) {
      console.error('获取网络接口地址失败:', error)
      // 如果 API 不可用，返回空数组
      return []
    }
  }
}

export { networkApi }
export type { NetworkSettings, LanUrlsResponse, NetworkInterface }
