<template>
  <div class="network-settings-section">
    <div class="network-section-title">应用网络设置</div>
    
    <!-- IP和端口显示 -->
    <div class="network-setting-group">      
      <!-- 本地地址 -->
      <div class="network-setting-item">
        <div class="network-setting-label">本地地址</div>
        <div class="network-setting-content">
          <div class="network-url-container">
            <div class="network-url-display">
              <span>{{ showLocalUrl ? localUrl : '••••••••••••••••••••' }}</span>
            </div>
            <div class="network-url-actions">
              <button
                @click="toggleShowLocalUrl"
                class="network-url-action"
                type="button"
                :title="showLocalUrl ? '隐藏地址' : '显示地址'"
                :disabled="!localUrl || localUrl.trim() === ''"
              >
                <img :src="showLocalUrl ? eyeOffIcon : eyeOnIcon" alt="toggle visibility" />
              </button>
              <button
                @click="copyUrl(localUrl)"
                class="network-url-action"
                type="button"
                title="复制地址"
                :disabled="loading.copyUrl || !localUrl || localUrl.trim() === ''"
              >
                <img :src="copyIcon" alt="copy" />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 局域网地址列表 -->
      <div class="network-setting-item">
        <div class="network-setting-label">局域网地址</div>
        <div class="network-setting-content">
          <div v-if="networkUrls.length > 0" class="network-urls-list">
            <div v-for="(url, index) in networkUrls" :key="index" class="network-url-item">
              <span>{{ showNetworkUrls ? (typeof url === 'string' ? url : `http://${url.address}`) : '••••••••••••••••••••' }}</span>
              <div class="network-url-item-actions">
                <button
                  @click="toggleShowNetworkUrls"
                  class="network-url-action"
                  type="button"
                  :title="showNetworkUrls ? '隐藏地址' : '显示地址'"
                >
                  <img :src="showNetworkUrls ? eyeOffIcon : eyeOnIcon" alt="toggle visibility" />
                </button>
                <button 
                  @click="copyUrl(typeof url === 'string' ? url : `http://${url.address}`)"
                  class="network-url-action"
                  type="button"
                  title="复制地址"
                  :disabled="loading.copyUrl"
                >
                  <img :src="copyIcon" alt="copy" />
                </button>
              </div>
            </div>
          </div>
          <div v-else class="network-no-urls">
            未检测到局域网地址
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { networkApi, type NetworkSettings, type NetworkInterface } from '@/api/network'


// 导入图标
import eyeOnIcon from '@/assets/icons/sys_eyeon.svg'
import eyeOffIcon from '@/assets/icons/sys_eyeoff.svg'
import copyIcon from '@/assets/icons/chat_copy.svg'

const notificationStore = useNotificationStore()

// 状态变量
const localUrl = ref('')
const networkUrls = ref<(string | NetworkInterface)[]>([])
const loading = ref({
  settings: false,
  copyUrl: false
})
const showLocalUrl = ref(false)
const showNetworkUrls = ref(false)

// 获取当前应用的URL
const getCurrentAppUrls = () => {
  const protocol = window.location.protocol
  const hostname = window.location.hostname
  const port = window.location.port
  
  // 本地URL
  const localUrl = `${protocol}//${hostname}:${port}`
  
  // 网络URL列表
  const networkUrls: (string | NetworkInterface)[] = []
  
  // 不再区分本地主机和其他情况，统一使用当前地址作为默认值
  // 后续会尝试从后端API获取更准确的地址
  networkUrls.push({
    name: '局域网',
    address: `${hostname}:${port}`
  })
  
  return {
    localUrl,
    networkUrls
  }
}

// 获取网络设置
const fetchNetworkSettings = async () => {
  loading.value.settings = true
  try {
    // 先获取当前应用的URL作为默认值
    const urls = getCurrentAppUrls()
    localUrl.value = urls.localUrl
    networkUrls.value = urls.networkUrls
    
    // 尝试从后端API获取网络设置
    try {
      const settings = await networkApi.getNetworkSettings()
      
      // 尝试获取所有网络接口地址
      try {
        const interfaces = await networkApi.getAllNetworkInterfaces()
        if (interfaces && interfaces.length > 0) {
          // 直接使用接口返回的地址列表，这些是后端检测到的真实网络地址
          networkUrls.value = interfaces.filter(iface => 
            // 过滤掉本地回环地址，只保留局域网地址
            !iface.address.startsWith('127.0.0.1') && 
            !iface.address.startsWith('localhost')
          )
          
          // 如果过滤后没有地址，则使用所有地址
          if (networkUrls.value.length === 0) {
            networkUrls.value = interfaces
          }
        } else if (settings.lanUrls && settings.lanUrls.length > 0) {
          // 如果没有获取到网络接口地址，使用设置中的 lanUrls
          networkUrls.value = settings.lanUrls.map(url => ({
            name: '局域网',
            address: url.replace(/^https?:\/\//, '')
          }))
        }
      } catch (error) {
        console.error('获取网络接口地址失败:', error)
        
        // 如果获取网络接口失败，但设置中有 lanUrls，则使用它们
        if (settings.lanUrls && settings.lanUrls.length > 0) {
          networkUrls.value = settings.lanUrls.map(url => ({
            name: '局域网',
            address: url.replace(/^https?:\/\//, '')
          }))
        }
      }
    } catch (error) {
      console.error('获取网络设置失败:', error)
      // 使用当前 URL 作为备用
      // 已经在函数开始时设置了 localUrl 和 networkUrls
    }
  } catch (error) {
    console.error('获取网络设置失败:', error)
    notificationStore.showError('获取网络设置失败，请稍后重试')
  } finally {
    loading.value.settings = false
  }
}

// 复制URL到剪贴板
const copyUrl = async (url: string | any) => {
  loading.value.copyUrl = true
  try {
    // 如果url是对象，则提取地址并添加http://前缀
    const urlToCopy = typeof url === 'string' 
      ? url 
      : (url && url.address ? `http://${url.address}` : '');
    
    await navigator.clipboard.writeText(urlToCopy)
    notificationStore.showSuccess('链接已复制到剪贴板')
  } catch (error) {
    console.error('复制链接失败:', error)
    notificationStore.showError('复制链接失败，请手动复制')
  } finally {
    loading.value.copyUrl = false
  }
}

// 切换显示/隐藏本地URL
const toggleShowLocalUrl = () => {
  showLocalUrl.value = !showLocalUrl.value
}

// 切换显示/隐藏网络URL
const toggleShowNetworkUrls = () => {
  showNetworkUrls.value = !showNetworkUrls.value
}

// 组件挂载时获取网络设置
onMounted(() => {
  fetchNetworkSettings()
})
</script>

<style scoped>
@import './NetworkSettings.css'
</style>
