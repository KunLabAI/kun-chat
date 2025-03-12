<template>
  <MainLayout>
    <div class="pull-model-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="main-title">{{ t('model.pull_page.title') }}</h1>
            <p class="sub-title">{{ t('model.pull_page.subtitle') }}</p>
          </div>
          <div class="header-actions">
            <Button
              variant="link"
              size="md"
              @click="goBack"
              :disabled="isPulling"
            >
              {{ t('model.pull_page.back') }}
            </Button>
            <Button
              variant="primary"
              size="md"
              @click="startPull"
              :disabled="!isValidModelName || isPulling"
            >
              {{ isPulling ? t('model.pull_page.pulling') : t('model.pull_page.start_pull') }}
            </Button>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-group">
          <label for="modelName">{{ t('model.pull_page.form.model_name') }}</label>
          <input
            id="modelName"
            v-model="modelName"
            type="text"
            :class="{ 'error': modelNameError }"
            :placeholder="t('model.pull_page.form.model_name_placeholder')"
            @input="validateModelName"
            :disabled="isPulling"
          />
          <span v-if="modelNameError" class="error-text">{{ modelNameError }}</span>
        </div>
      </div>

      <!-- 进度区域 -->
      <div v-if="isPulling" class="progress-section">
        <div class="progress-card">
          <div class="progress-header">
            <h3>{{ t('model.pull_page.progress.pulling') }}: {{ modelName }}</h3>
            <div class="status-badge" :class="pullStatus.status">
              {{ statusText }}
            </div>
          </div>
          
          <div class="progress-details">
            <div class="progress-bar">
              <div 
                class="progress-fill"
                :style="{ 
                  width: `${pullStatus.progress}%`,
                  transition: pullStatus.status === 'downloading' ? 'width 0.3s ease' : 'none'
                }"
              />
            </div>
            <div class="progress-stats">
              <span class="percentage">{{ Math.round(pullStatus.progress) }}%</span>
              <span class="size" v-if="pullStatus.total_size">
                {{ formatSize(pullStatus.downloaded_size) }} / {{ formatSize(pullStatus.total_size) }}
              </span>
            </div>
            <div v-if="downloadSpeed > 0" class="download-info">
              <span class="speed">{{ t('model.pull_page.progress.download_speed') }}: {{ formatSpeedSize(downloadSpeed) }}</span>
              <span v-if="estimatedTimeLeft" class="time-left">
                {{ t('model.pull_page.progress.time_left') }}: {{ estimatedTimeLeft }}
              </span>
            </div>
          </div>

          <div v-if="pullStatus.error" class="error-message">
            {{ pullStatus.error }}
          </div>

          <div class="progress-actions">
            <Button
              v-if="isPulling && pullStatus.status !== 'completed' && pullStatus.status !== 'failed' && pullStatus.status !== 'cancelled'"
              variant="danger"
              @click="showCancelDialog = true"
            >
              {{ t('common.actions.cancel') }}
            </Button>
            <Button
              v-if="pullStatus.status === 'failed'"
              variant="primary"
              @click="startPull"
            >
              {{ t('model.pull_page.progress.retry') }}
            </Button>
            <Button
              v-if="pullStatus.status === 'completed'"
              variant="primary"
              @click="goBack"
            >
              {{ t('model.pull_page.progress.done') }}
            </Button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="progress-section empty-state">
        <template v-if="pullStatus.status === 'completed'">
          <img 
            :src="SysCongratulationIcon" 
            alt="Congratulation Icon" 
            class="empty-state-icon congratulation-icon" 
          />
          <h3>{{ t('model.pull_page.empty_state.completed.title') }}</h3>
          <p>{{ t('model.pull_page.empty_state.completed.subtitle') }}</p>
        </template>
        <template v-else>
          <div class="icons-container">
            <a 
              href="https://ollama.com/search" 
              target="_blank" 
              rel="noopener noreferrer"
              class="icon-circle"
            >
              <img src="@/assets/modelslogo/Ollama_icon.svg" alt="Ollama" class="model-icon" />
            </a>
            <span class="plus-icon">+</span>
            <a 
              href="https://huggingface.co/models" 
              target="_blank" 
              rel="noopener noreferrer"
              class="icon-circle"
            >
              <img src="@/assets/modelslogo/Huggingface_icon.svg" alt="HuggingFace" class="model-icon" />
            </a>
          </div>
          <h3>{{ t('model.pull_page.empty_state.default.title') }}</h3>
          <p class="hint-text">{{ t('model.pull_page.empty_state.default.subtitle') }}</p>
        </template>
      </div>
    </div>
  </MainLayout>
  <Dialog
    v-model="showCancelDialog"
    :title="t('model.pull_page.progress.cancel_dialog.title')"
    :confirm-text="t('model.pull_page.progress.cancel_dialog.confirm')"
    :cancel-text="t('model.pull_page.progress.cancel_dialog.cancel')"
    @confirm="confirmCancel"
  >
    <p>{{ t('model.pull_page.progress.cancel_dialog.message') }}</p>
  </Dialog>
  
  <!-- 覆盖模型确认对话框 -->
  <Dialog
    v-model="showOverwriteDialog"
    :title="t('model.pull_page.overwrite_dialog.title')"
    :confirm-text="t('model.pull_page.overwrite_dialog.confirm')"
    :cancel-text="t('model.pull_page.overwrite_dialog.cancel')"
    @confirm="confirmOverwrite"
    @cancel="cancelOverwrite"
  >
    <p>{{ t('model.pull_page.overwrite_dialog.message', { modelName }) }}</p>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import { useLocalization } from '@/i18n'
import MainLayout from '@/layouts/MainLayout.vue'
import Button from '@/components/common/Button.vue'
import Dialog from '@/components/common/Dialog.vue'
import SysCongratulationIcon from '@/assets/icons/sys_congratulation.svg'
import { modelApi } from '@/api/models'

interface PullStatus {
  status: string;
  progress: number;
  total_size: number;
  downloaded_size: number;
  details: any[];
  error: string | null;
}

interface SpeedSample {
  timestamp: number;
  bytes: number;
}

const router = useRouter()
const notificationStore = useNotificationStore()
const { t } = useLocalization()

const modelName = ref('')
const modelNameError = ref('')
const isPulling = ref(false)
const eventSource = ref<EventSource | null>(null)
const pullStatus = ref<PullStatus>({
  status: '',
  progress: 0,
  total_size: 0,
  downloaded_size: 0,
  details: [],
  error: null
})

// 下载速度计算相关
const downloadSpeedSamples = ref<SpeedSample[]>([])
const lastSpeedUpdate = ref<number>(0)
const lastTimeEstimate = ref<number>(0)

// 重连相关
const reconnectAttempts = ref<number>(0)
const maxReconnectAttempts = 5
const reconnectTimer = ref<number | null>(null)
const reconnectDelay = 2000 // 初始重连延迟（毫秒）

// 对话框控制
const showCancelDialog = ref(false)
const showOverwriteDialog = ref(false)
const forceOverwrite = ref(false)

// 计算属性
const downloadSpeed = computed(() => {
  return calculateMovingAverageSpeed()
})

const estimatedTimeLeft = computed(() => {
  if (downloadSpeed.value <= 0 || !pullStatus.value.total_size || !pullStatus.value.downloaded_size) {
    return ''
  }

  const remainingBytes = pullStatus.value.total_size - pullStatus.value.downloaded_size
  const estimatedSeconds = remainingBytes / downloadSpeed.value

  return formatTimeLeft(smoothTimeEstimate(estimatedSeconds))
})

const statusText = computed(() => {
  switch (pullStatus.value.status) {
    case 'downloading':
      return t('model.pull_page.progress.status.downloading')
    case 'completed':
      return t('model.pull_page.progress.status.completed')
    case 'failed':
      return t('model.pull_page.progress.status.failed')
    case 'cancelled':
      return t('model.pull_page.progress.status.cancelled')
    default:
      return pullStatus.value.status
  }
})

const isValidModelName = computed(() => {
  return modelName.value && !modelNameError.value
})

// 功能函数
function calculateMovingAverageSpeed(): number {
  const now = Date.now()
  const windowSize = 5000 // 5秒窗口
  const minSamples = 2 // 最少需要的样本数

  // 移除旧样本
  while (
    downloadSpeedSamples.value.length > 0 &&
    downloadSpeedSamples.value[0].timestamp < now - windowSize
  ) {
    downloadSpeedSamples.value.shift()
  }

  if (downloadSpeedSamples.value.length < minSamples) {
    return 0
  }

  const firstSample = downloadSpeedSamples.value[0]
  const lastSample = downloadSpeedSamples.value[downloadSpeedSamples.value.length - 1]
  const timeSpan = (lastSample.timestamp - firstSample.timestamp) / 1000 // 转换为秒
  const bytesDiff = lastSample.bytes - firstSample.bytes

  return timeSpan > 0 ? bytesDiff / timeSpan : 0
}

function smoothTimeEstimate(newEstimate: number): number {
  if (lastTimeEstimate.value === 0) {
    lastTimeEstimate.value = newEstimate
    return newEstimate
  }

  const alpha = 0.2 // 平滑因子
  lastTimeEstimate.value = alpha * newEstimate + (1 - alpha) * lastTimeEstimate.value
  return lastTimeEstimate.value
}

function formatSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

function formatSpeedSize(bytesPerSecond: number): string {
  const units = ['B/s', 'KB/s', 'MB/s', 'GB/s']
  let size = bytesPerSecond
  let exponent = 0
  
  while (size >= 1024 && exponent < units.length - 1) {
    size /= 1024
    exponent++
  }
  
  return `${size.toFixed(1)} ${units[exponent]}`
}

function formatTimeLeft(seconds: number): string {
  if (seconds < 60) {
    return `${Math.ceil(seconds)}秒`
  } else if (seconds < 3600) {
    return `${Math.ceil(seconds / 60)}分钟`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.ceil((seconds % 3600) / 60)
    return `${hours}小时${minutes}分钟`
  }
}

// 状态管理函数
function saveDownloadState() {
  if (isPulling.value) {
    // 如果是模型已存在状态，不保存
    if (pullStatus.value.status === 'exists') {
      console.log('模型已存在状态，不保存')
      return
    }
    
    // 保存更详细的状态信息
    const state = {
      modelName: modelName.value,
      isPulling: true,
      status: pullStatus.value,
      timestamp: Date.now(),
      lastUpdate: Date.now(), // 最后更新时间
      downloadSpeedData: {
        samples: downloadSpeedSamples.value.slice(-10), // 仅保存最近的10个样本
        lastSpeed: downloadSpeed.value,
        lastTimeEstimate: lastTimeEstimate.value
      },
      reconnectInfo: {
        attempts: reconnectAttempts.value,
        maxAttempts: maxReconnectAttempts,
        lastAttemptTime: lastSpeedUpdate.value
      },
      browserInfo: {
        isVisible: !document.hidden,
        userAgent: navigator.userAgent,
        lastVisibilityChange: Date.now()
      },
      // 添加更多连接信息
      connectionInfo: {
        connected: eventSource.value ? eventSource.value.readyState === 1 : false,
        readyState: eventSource.value ? eventSource.value.readyState : -1,
        lastConnectTime: Date.now()
      }
    }
    
    try {
      // 尝试使用 sessionStorage 和 localStorage 两种方式保存
      // sessionStorage 在浏览器关闭时会清除，但在页面刷新时保留
      sessionStorage.setItem('modelPullState', JSON.stringify(state))
      // localStorage 在浏览器关闭后仍然保留
      localStorage.setItem('modelPullState', JSON.stringify(state))
      console.log('成功保存下载状态')
      
      // 尝试使用 IndexedDB 保存更大的状态数据
      saveStateToIndexedDB(state)
    } catch (error) {
      console.error('保存下载状态失败:', error)
      // 如果数据过大导致存储失败，尝试保存简化版本
      const simpleState = {
        modelName: modelName.value,
        isPulling: true,
        status: pullStatus.value,
        timestamp: Date.now(),
        lastUpdate: Date.now()
      }
      try {
        localStorage.setItem('modelPullState', JSON.stringify(simpleState))
      } catch (e) {
        console.error('保存简化状态也失败:', e)
      }
    }
  } else {
    // 清除所有存储
    localStorage.removeItem('modelPullState')
    sessionStorage.removeItem('modelPullState')
    clearStateFromIndexedDB()
    
    downloadSpeedSamples.value = []
    lastSpeedUpdate.value = 0
    lastTimeEstimate.value = 0
    reconnectAttempts.value = 0
    isPulling.value = false
  }
}

// 使用 IndexedDB 保存状态数据
function saveStateToIndexedDB(state: any) {
  // 仅在浏览器环境下执行
  if (typeof window === 'undefined' || !window.indexedDB) return
  
  try {
    // 创建一个可序列化的状态对象副本
    // 使用 JSON 序列化和反序列化来确保所有内容都是可克隆的
    const serializableState = JSON.parse(JSON.stringify({
      modelName: state.modelName,
      isPulling: state.isPulling,
      status: {
        status: state.status.status,
        progress: state.status.progress,
        total_size: state.status.total_size,
        downloaded_size: state.status.downloaded_size,
        error: state.status.error
      },
      timestamp: state.timestamp,
      lastUpdate: state.lastUpdate,
      downloadSpeedData: {
        samples: state.downloadSpeedData?.samples || [],
        lastSpeed: state.downloadSpeedData?.lastSpeed,
        lastTimeEstimate: state.downloadSpeedData?.lastTimeEstimate
      },
      reconnectInfo: {
        attempts: state.reconnectInfo?.attempts,
        maxAttempts: state.reconnectInfo?.maxAttempts,
        lastAttemptTime: state.reconnectInfo?.lastAttemptTime
      },
      browserInfo: {
        isVisible: !document.hidden,
        lastVisibilityChange: Date.now()
      },
      connectionInfo: {
        connected: state.connectionInfo?.connected,
        readyState: state.connectionInfo?.readyState,
        lastConnectTime: state.connectionInfo?.lastConnectTime
      }
    }))
    
    const request = window.indexedDB.open('kun-lab', 1)
    
    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result
      if (!db.objectStoreNames.contains('downloadState')) {
        db.createObjectStore('downloadState', { keyPath: 'id' })
      }
    }
    
    request.onsuccess = (event) => {
      const db = (event.target as IDBOpenDBRequest).result
      const transaction = db.transaction(['downloadState'], 'readwrite')
      const store = transaction.objectStore('downloadState')
      
      // 保存状态数据
      const stateWithId = { ...serializableState, id: 'currentDownload' }
      store.put(stateWithId)
      
      transaction.oncomplete = () => {
        console.log('成功将状态保存到 IndexedDB')
        db.close()
      }
      
      transaction.onerror = (error) => {
        console.error('保存状态到 IndexedDB 失败:', error)
        db.close()
      }
    }
    
    request.onerror = (event) => {
      console.error('打开 IndexedDB 失败:', event)
    }
  } catch (error) {
    console.error('准备 IndexedDB 数据时出错:', error)
  }
}

// 从 IndexedDB 清除状态数据
function clearStateFromIndexedDB() {
  // 仅在浏览器环境下执行
  if (typeof window === 'undefined' || !window.indexedDB) return
  
  const request = window.indexedDB.open('kun-lab', 1)
  
  request.onsuccess = (event) => {
    const db = (event.target as IDBOpenDBRequest).result
    const transaction = db.transaction(['downloadState'], 'readwrite')
    const store = transaction.objectStore('downloadState')
    
    // 删除状态数据
    store.delete('currentDownload')
    
    transaction.oncomplete = () => {
      console.log('成功从 IndexedDB 清除状态')
      db.close()
    }
    
    transaction.onerror = (error) => {
      console.error('从 IndexedDB 清除状态失败:', error)
      db.close()
    }
  }
  
  request.onerror = (event) => {
    console.error('打开 IndexedDB 失败:', event)
  }
}

async function restoreDownloadState() {
  try {
    const savedState = localStorage.getItem('modelPullState')
    if (savedState) {
      const state = JSON.parse(savedState)
      const elapsedTime = Date.now() - state.timestamp
      
      // 如果超过10分钟，不恢复状态
      if (elapsedTime > 600000) {
        cleanupDownloadState()
        return
      }

      // 确保状态对象包含所需的所有属性
      if (!state.status || !state.modelName) {
        console.error('保存的状态数据不完整')
        cleanupDownloadState()
        return
      }

      // 如果状态是"exists"，不恢复状态
      if (state.status.status === 'exists') {
        console.log('检测到模型已存在的状态，不恢复')
        cleanupDownloadState()
        return
      }

      // 如果是正在下载中的状态，直接恢复
      if (state.status.status === 'downloading') {
        modelName.value = state.modelName
        isPulling.value = state.isPulling
        pullStatus.value = state.status
        
        // 添加初始延迟
        console.log('等待后端准备就绪...')
        await new Promise(resolve => setTimeout(resolve, 1000))
        await connectSSE()
        return
      }

      // 对于其他状态（比如失败或取消），询问用户是否要恢复
      const shouldRestore = window.confirm(
        `检测到未完成的下载任务：${state.modelName}\n是否要恢复下载？`
      )
      
      if (shouldRestore) {
        modelName.value = state.modelName
        isPulling.value = state.isPulling
        pullStatus.value = state.status
        
        // 添加初始延迟
        console.log('等待后端准备就绪...')
        await new Promise(resolve => setTimeout(resolve, 1000))
        await connectSSE()
      } else {
        cleanupDownloadState()
      }
    }
  } catch (error) {
    console.error('恢复下载状态失败:', error)
    cleanupDownloadState()
  }
}

function cleanupDownloadState(keepState = false) {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }

  if (reconnectTimer.value) {
    clearTimeout(reconnectTimer.value)
    reconnectTimer.value = null
  }

  if (!keepState) {
    // 清除所有存储
    localStorage.removeItem('modelPullState')
    sessionStorage.removeItem('modelPullState')
    clearStateFromIndexedDB()
    
    downloadSpeedSamples.value = []
    lastSpeedUpdate.value = 0
    lastTimeEstimate.value = 0
    reconnectAttempts.value = 0
    isPulling.value = false
  }
}

// 核心功能函数
async function updateProgress(data: any) {
  try {
    const parsedData = typeof data === 'string' ? JSON.parse(data) : data
    
    // 更新下载状态
    pullStatus.value = {
      ...pullStatus.value,
      ...parsedData
    }

    // 如果模型已存在，显示覆盖确认对话框
    if (parsedData.status === 'exists') {
      isPulling.value = false
      showOverwriteDialog.value = true
      return
    }

    // 更新下载速度样本
    if (parsedData.downloaded_size) {
      const now = Date.now()
      if (now - lastSpeedUpdate.value >= 1000) { // 每秒更新一次
        downloadSpeedSamples.value.push({
          timestamp: now,
          bytes: parsedData.downloaded_size
        })
        lastSpeedUpdate.value = now
      }
    }

    // 处理各种状态
    if (parsedData.status === 'completed') {
      notificationStore.success(t('model.pull_page.progress.status.completed'))
      cleanupDownloadState()
    } else if (parsedData.status === 'cancelled') {
      notificationStore.info(t('model.pull_page.progress.status.cancelled'))
      cleanupDownloadState()
    } else if (parsedData.status === 'failed') {
      const errorMessage = parsedData.error || t('model.pull_page.progress.status.failed')
      notificationStore.error(`${t('model.pull_page.progress.status.failed')}: ${errorMessage}`)
      cleanupDownloadState()
    }

    // 保存状态到 localStorage
    if (isPulling.value) {
      saveDownloadState()
    }
  } catch (error) {
    console.error('Error parsing progress data:', error)
    notificationStore.error(t('model.pull_page.progress.error'))
  }
}

async function connectSSE() {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }

  try {
    eventSource.value = modelApi.pullModel(modelName.value, forceOverwrite.value)

    // 上次收到消息的时间戳
    let lastMessageTime = Date.now()
    // 心跳检测定时器
    let heartbeatTimer: number | null = null
    
    // 设置心跳检测，确保连接活跃
    const setupHeartbeat = () => {
      if (heartbeatTimer) {
        clearInterval(heartbeatTimer)
      }
      
      // 每10秒检查一次连接状态
      heartbeatTimer = window.setInterval(() => {
        const now = Date.now()
        // 如果超过30秒没有收到消息，认为连接可能已断开
        if (now - lastMessageTime > 30000 && isPulling.value) {
          console.log('心跳检测：长时间未收到消息，尝试重新连接...')
          // 清除当前心跳检测
          if (heartbeatTimer) {
            clearInterval(heartbeatTimer)
            heartbeatTimer = null
          }
          // 重新连接
          reconnectSSE()
        } else {
          // 保存当前状态到本地存储
          saveDownloadState()
        }
      }, 10000)
    }
    
    // 启动心跳检测
    setupHeartbeat()

    // 创建重连函数
    const reconnectSSE = async () => {
      if (isPulling.value && reconnectAttempts.value < maxReconnectAttempts) {
        reconnectAttempts.value++
        const delay = Math.min(reconnectDelay * Math.pow(1.5, reconnectAttempts.value - 1), 30000)
        
        console.log(`尝试在 ${delay}ms 后重新连接 (尝试 ${reconnectAttempts.value}/${maxReconnectAttempts})`)
        
        if (reconnectTimer.value) {
          clearTimeout(reconnectTimer.value)
        }
        
        // 在重连前保存当前状态
        saveDownloadState()
        
        reconnectTimer.value = window.setTimeout(async () => {
          if (isPulling.value) {
            // 关闭可能存在的连接
            if (eventSource.value) {
              eventSource.value.close()
              eventSource.value = null
            }
            // 重新连接
            await connectSSE()
          }
        }, delay)
      } else if (reconnectAttempts.value >= maxReconnectAttempts) {
        isPulling.value = false
        pullStatus.value.status = 'failed'
        pullStatus.value.error = t('model.pull_page.progress.connection_error')
        notificationStore.error(t('model.pull_page.progress.connection_error'))
        
        // 清理下载状态
        cleanupDownloadState()
      }
    }

    eventSource.value.onerror = (event) => {
      console.error('SSE连接错误:', event)
      // 记录错误发生时间
      lastMessageTime = Date.now() - 25000 // 设置为接近心跳检测阈值，促使快速重连
      
      // 如果仍在下载中，尝试重连
      if (isPulling.value) {
        reconnectSSE()
      }
    }

    eventSource.value.onmessage = (event) => {
      try {
        // 更新最后收到消息的时间
        lastMessageTime = Date.now()
        reconnectAttempts.value = 0 // 重置重连次数
        
        // 处理keep-alive消息
        if (event.data === 'keep-alive' || event.data.trim() === '') {
          console.log('收到keep-alive消息')
          return
        }
        
        const data = JSON.parse(event.data)
        console.log('收到SSE消息:', data)
        
        // 处理模型已存在的情况
        if (data.status === 'exists') {
          console.log('模型已存在，显示覆盖确认对话框')
          isPulling.value = false
          showOverwriteDialog.value = true
          
          // 关闭 SSE 连接
          if (eventSource.value) {
            eventSource.value.close()
            eventSource.value = null
          }
          
          // 重置状态
          pullStatus.value = {
            status: '',
            progress: 0,
            total_size: 0,
            downloaded_size: 0,
            details: [],
            error: null
          }
          
          // 清理下载状态
          cleanupDownloadState()
          return
        }
        
        // 处理错误状态
        if (data.status === 'failed') {
          isPulling.value = false
          pullStatus.value.status = 'failed'
          
          // 检查是否包含模型名称错误信息
          if (data.error && data.error.includes('file does not exist')) {
            pullStatus.value.error = t('model.pull_page.validation.model_not_found')
            notificationStore.error(t('model.pull_page.validation.model_not_found'))
          } else {
            pullStatus.value.error = data.error || t('model.pull_page.progress.error')
            notificationStore.error(data.error || t('model.pull_page.progress.error'))
          }
          
          cleanupDownloadState()
          return
        }
        
        // 处理其他状态
        updateProgress(data)
        
        // 每收到消息就保存一次状态
        saveDownloadState()
      } catch (error) {
        console.error('处理SSE消息时出错:', error)
      }
    }
  } catch (error) {
    console.error('连接SSE时出错:', error)
    notificationStore.error(t('model.pull_page.progress.error'))
    isPulling.value = false
  }
}

async function validateModelName() {
  modelNameError.value = ''
  
  let name = modelName.value.trim()
  if (!name) {
    modelNameError.value = t('model.pull_page.validation.model_name_required')
    return false
  }
  
  // 处理包含 "ollama run" 前缀的模型名称
  let modelNameToValidate = name
  if (name.startsWith('ollama run ')) {
    modelNameToValidate = name.replace('ollama run ', '').trim()
  }
  
  // 更新的格式验证规则
  // 支持：
  // 1. 基本模型名称：qwen:0.5b-chat-v1.5
  // 2. 带量化参数：qwen:0.5b-chat-v1.5-q3_K_L
  // 3. 带用户名的格式：deepseek-140B/DeepSeekAI140B
  // 4. 更复杂的组合：username/model-name:tag-q4_K_M
  // 5. HuggingFace格式：hf.co/username/model:Q4_K_M
  const validModelPattern = /^(?:(?:hf\.co|huggingface\.co)\/)?[\w.-]+(?:\/[\w.-]+)?(?::[.\w-]+)?$/
  
  if (!validModelPattern.test(modelNameToValidate)) {
    modelNameError.value = t('model.pull_page.validation.model_name_invalid')
    return false
  }
  
  return true
}

async function startPull() {
  try {
    if (!isValidModelName.value) {
      return
    }

    // 重置覆盖标志
    if (!forceOverwrite.value) {
      forceOverwrite.value = false
    }
    
    isPulling.value = true
    pullStatus.value = {
      status: 'downloading',
      progress: 0,
      total_size: 0,
      downloaded_size: 0,
      details: [],
      error: null
    }

    // 重置状态
    downloadSpeedSamples.value = []
    lastSpeedUpdate.value = 0
    lastTimeEstimate.value = 0
    reconnectAttempts.value = 0

    await connectSSE()
    saveDownloadState()
  } catch (error) {
    console.error('Error starting pull:', error)
    notificationStore.error(t('model.pull_page.progress.error'))
    isPulling.value = false
  }
}

async function confirmCancel() {
  showCancelDialog.value = false
  await handleCancel()
}

async function handleCancel() {
  try {
    // 先更新状态为取消中
    pullStatus.value.status = 'cancelling'
    
    // 关闭 SSE 连接
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }
    
    // 发送取消请求
    await modelApi.cancelPull(modelName.value)
    
    // 清理状态
    cleanupDownloadState()
    notificationStore.info(t('model.pull_page.progress.status.cancelled'))
  } catch (error) {
    console.error('取消下载失败:', error)
    notificationStore.error(t('model.pull_page.progress.error'))
    // 如果取消失败，恢复之前的状态
    pullStatus.value.status = 'downloading'
  }
}

async function confirmOverwrite() {
  showOverwriteDialog.value = false
  forceOverwrite.value = true
  await startPull()
}

function cancelOverwrite() {
  showOverwriteDialog.value = false
  
  // 关闭 SSE 连接
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }
  
  // 完全重置状态
  isPulling.value = false
  forceOverwrite.value = false
  pullStatus.value = {
    status: '',
    progress: 0,
    total_size: 0,
    downloaded_size: 0,
    details: [],
    error: null
  }
  
  // 清理下载状态和重连计时器
  cleanupDownloadState()
  
  // 清除重连计时器
  if (reconnectTimer.value) {
    clearTimeout(reconnectTimer.value)
    reconnectTimer.value = null
  }
  
  // 重置重连尝试次数
  reconnectAttempts.value = 0
}

function goBack() {
  router.push('/models')
}

// 页面可见性处理
function handleVisibilityChange() {
  if (document.hidden) {
    // 页面隐藏时保存状态并记录时间戳
    if (isPulling.value) {
      console.log('页面隐藏，保存下载状态')
      // 在状态中记录页面隐藏的时间戳
      const state = {
        modelName: modelName.value,
        isPulling: true,
        status: pullStatus.value,
        timestamp: Date.now(),
        hiddenAt: Date.now() // 记录页面隐藏时间
      }
      localStorage.setItem('modelPullState', JSON.stringify(state))
      
      // 不关闭 SSE 连接，让它在后台继续运行
      // 即使页面不可见，下载仍会继续
    }
  } else {
    // 页面重新可见时检查状态并恢复连接
    if (isPulling.value) {
      console.log('页面重新可见，检查下载状态')
      
      // 尝试从本地存储恢复最新状态
      const savedState = localStorage.getItem('modelPullState')
      if (savedState) {
        const state = JSON.parse(savedState)
        const currentTime = Date.now()
        const hiddenTime = state.hiddenAt ? currentTime - state.hiddenAt : 0
        
        console.log(`页面隐藏时间: ${Math.round(hiddenTime / 1000)}秒`)
        
        // 如果页面隐藏时间超过30秒，重新连接SSE
        // 这是因为某些浏览器可能会在页面隐藏一段时间后暂停后台连接
        if (hiddenTime > 30000 || !eventSource.value || eventSource.value.readyState !== 1) {
          console.log('重新连接SSE...')
          connectSSE()
        } else {
          console.log('SSE连接仍然活跃，无需重连')
        }
      } else {
        // 如果没有保存的状态但仍在拉取中，重新连接
        connectSSE()
      }
    }
  }
}

// 生命周期钩子
onMounted(() => {
  document.addEventListener('visibilitychange', handleVisibilityChange)
  restoreDownloadState()
})

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  if (isPulling.value) {
    saveDownloadState()
    // 只关闭连接，但保持状态
    cleanupDownloadState(true)
  }
})
</script>

<style scoped>
@import '@/styles/PullModelPage.css';
</style>