<template>
  <MainLayout>
    <div class="about-page">
      <!-- 页面头部 -->
      <div class="about-page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="about-main-title">{{ t('about.title') }}</h1>
            <p class="about-sub-title">{{ t('about.subtitle') }}</p>
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="about-main-content">
        <!-- 页签导航 -->
        <div class="about-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.key"
            class="about-tab-item"
            :class="{ 'about-tab-item-active': currentTab === tab.key }"
            @click="switchTab(tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 页签内容 -->
        <div class="about-tab-content">
          <!-- 应用信息页签 -->
          <div v-show="currentTab === 'app'" class="about-tab-pane">
            <!-- 应用简介卡片 -->
            <div class="about-section">
              <div class="about-logo-banner">
                <img src="@/assets/logobanner.svg" alt="Kun-Lab Logo" class="about-logo-image">
                <div class="about-description">
                  <div class="about-detail-title">{{ t('about.appInfo.title') }}</div>
                  <div class="about-detail-value">
                    {{ t('about.appInfo.description') }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 应用详情卡片 -->
            <div class="about-section">
              <h3 class="about-section-title">{{ t('about.appInfo.details') }}</h3>
              <div class="about-details-grid">
                <div class="about-detail-item">
                  <div class="about-detail-label">{{ t('about.appInfo.developer') }}</div>
                  <div class="about-detail-value">{{ t('about.appInfo.developerText') }}</div>
                </div>
                <div class="about-detail-item">
                  <div class="about-detail-label">{{ t('about.appInfo.website') }}</div>
                  <div class="about-detail-value">
                    <a href="https://lab.kunpuai.com" target="_blank" rel="noopener noreferrer" class="about-link">
                      {{ t('about.appInfo.websiteText') }}
                    </a>
                  </div>
                </div>
                <div class="about-detail-item">
                  <div class="about-detail-label">{{ t('about.appInfo.email') }}</div>
                  <div class="about-detail-value">
                    <a href="mailto:info@kunpuai.com" class="about-link">
                       info@kunpuai.com 
                    </a>
                  </div>
                </div>
                <div class="about-detail-item">
                  <div class="about-detail-label">{{ t('about.appInfo.github') }}</div>
                  <div class="about-detail-value">
                    <a href="https://github.com/bahamutww/kun-lab.git" target="_blank" rel="noopener noreferrer" class="about-link">
                      {{ t('about.appInfo.githubText') }}
                    </a>
                  </div>
                </div>
              </div>
            </div>

            <!-- 版本信息卡片 -->
            <div class="about-section">
              <h3 class="about-section-title">{{ t('about.appInfo.versionInfo') }}</h3>
              <div class="about-form-group-version">
                <div class="about-setting-name">{{ t('about.appInfo.version') }}</div>
                <div class="about-version-tag">
                  <span class="about-version-label">v{{ appVersion }}</span>
                </div>
              </div>

              <div class="about-form-group-version">
                <div class="about-setting-name">{{ t('about.appInfo.lastCheck') }}</div>
                <div class="about-version-tag">
                  <span class="about-version-label">{{ lastCheckTime ? formatDate(lastCheckTime) : t('about.appInfo.never') }}</span>
                </div>
              </div>

              <div class="about-form-group-version" v-if="updateStatus.status">
                <div class="about-setting-name">{{ t('about.appInfo.updateStatus') }}</div>
                <div class="about-version-tag" :class="{
                  'about-version-tag-success': updateStatus.status === 'not-available',
                  'about-version-tag-warning': updateStatus.status === 'available',
                  'about-version-tag-info': updateStatus.status === 'downloading',
                  'about-version-tag-primary': updateStatus.status === 'downloaded',
                  'about-version-tag-error': updateStatus.status === 'error'
                }">
                  <span class="about-version-label-text">{{ updateStatusText }}</span>
                </div>
              </div>

              <div class="about-form-group-version" v-if="updateStatus.status === 'downloading' && updateStatus.progress">
                <div class="about-progress-bar">
                  <div class="about-progress-bar-inner" :style="{ width: `${downloadProgress}%` }"></div>
                </div>
                <div class="about-progress-info">
                  <div class="about-progress-text">
                    {{ Math.round(updateStatus.progress.transferred / 1024 / 1024 * 100) / 100 }} MB / {{ Math.round(updateStatus.progress.total / 1024 / 1024 * 100) / 100 }} MB
                  </div>
                </div>
              </div>

              <div class="about-form-group-version">
                <button 
                  v-if="!updateStatus.status || updateStatus.status === 'not-available' || updateStatus.status === 'error'"
                  class="about-submit-button" 
                  @click="checkForUpdates" 
                  :disabled="isCheckingUpdate"
                >
                  <span v-if="isCheckingUpdate">{{ t('about.appInfo.checking') }}</span>
                  <span v-else>{{ t('about.appInfo.checkNow') }}</span>
                </button>

                <button 
                  v-if="updateStatus.status === 'available'"
                  class="about-submit-button" 
                  @click="downloadUpdate"
                  :disabled="isDownloading"
                >
                  {{ t('about.appInfo.downloadNow') }}
                </button>

                <button 
                  v-if="updateStatus.status === 'downloading'"
                  class="about-submit-button" 
                  disabled
                  style="cursor: not-allowed;"
                >
                  {{ t('about.appInfo.downloading') }}
                </button>

                <button 
                  v-if="updateStatus.status === 'error'"
                  class="about-submit-button" 
                  @click="retryDownload"
                >
                  {{ t('about.appInfo.retryDownload') }}
                </button>

                <button 
                  v-if="updateStatus.status === 'downloaded'"
                  class="about-submit-button about-submit-button-install" 
                  @click="installUpdate"
                >
                  {{ t('about.appInfo.installNow') }}
                </button>

                <button 
                  v-if="updateStatus.status === 'downloaded'"
                  class="about-submit-button about-submit-button-cancel" 
                  @click="cancelInstall"
                >
                  {{ t('about.appInfo.cancelInstall') }}
                </button>
              </div>
            </div>
          </div>

          <!-- 许可证信息页签 -->
          <div v-show="currentTab === 'license'" class="about-tab-pane">
            <div class="about-section">
              <h3 class="about-section-title">{{ t('about.license.title') }}</h3>
              <div class="about-license-content">
                <div v-if="isLoadingLicense" class="about-loading-text">
                  {{ t('about.license.loading') }}
                </div>
                <pre v-else>{{ licenseContent }}</pre>
              </div>
            </div>
          </div>

          <!-- 更新日志页签 -->
          <div v-show="currentTab === 'changelog'" class="about-tab-pane">
            <div class="about-section">
              <h3 class="about-section-title">{{ t('about.changelog.title') }}</h3>
              <ChangelogViewer />
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { useLocalization } from '@/i18n';
import { getLicense } from '@/api/licenseApi';
import axios from 'axios';
import MainLayout from '@/layouts/MainLayout.vue';
import { useRoute, useRouter } from 'vue-router';
import ChangelogViewer from '@/components/common/ChangelogViewer.vue';
import { 
  isElectron as checkIsElectron, 
  getCurrentVersion, 
  checkForUpdates as apiCheckForUpdates,
  downloadUpdate as apiDownloadUpdate,
  installUpdate as apiInstallUpdate,
  onUpdateStatus
} from '@/api/updateApi';
import { useNotificationStore } from '@/stores/notification';


// 许可证信息
const licenseContent = ref('');
const isLoadingLicense = ref(false);

const { t } = useLocalization();
const route = useRoute();
const router = useRouter();
const notificationStore = useNotificationStore();


// 标签页定义
const tabs = ref([
  { key: 'app', label: t('about.tabs.app') },
  { key: 'license', label: t('about.tabs.license') },
  { key: 'changelog', label: t('about.tabs.changelog') }
]);

// 当前标签页
const currentTab = ref(route.query.tab || 'app');

// 切换标签页并更新URL
const switchTab = (tab) => {
  currentTab.value = tab;
  router.push({ query: { ...route.query, tab } });
};

// 监听路由变化，更新当前标签页
watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.value.some(tab => tab.key === newTab)) {
    currentTab.value = newTab;
  }
});

// 应用信息
const appVersion = ref('0.0.1');
const electronVersion = ref('');
const isElectron = ref(false);
const lastCheckTime = ref(null);
const isCheckingUpdate = ref(false);

// 更新状态
const updateStatus = ref({
  status: null,
  version: null,
  releaseDate: null,
  progress: null,
  error: null,
  downloadSpeed: 0,
  estimatedTime: 0,
  updatePath: null  // 添加更新包路径
});

// 下载控制
const isDownloading = ref(false);
const downloadStartTime = ref(null);
const downloadTimer = ref(null);

// 加载许可证内容
const loadLicenseContent = async () => {
  if (currentTab.value === 'license') {
    try {
      isLoadingLicense.value = true;
      console.log('开始加载许可证内容...');
      licenseContent.value = await getLicense();
      console.log('许可证内容加载成功:', licenseContent.value ? '内容已加载' : '内容为空');
    } catch (error) {
      console.error('Failed to load license:', error);
      notificationStore.error(t('about.license.error'));
    } finally {
      isLoadingLicense.value = false;
    }
  }
};

// 监听标签页切换
watch(currentTab, (newTab) => {
  if (newTab === 'license') {
    loadLicenseContent();
  }
});

// 格式化日期
function formatDate(date) {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleString();
}

// 格式化下载速度
function formatSpeed(bytesPerSecond) {
  if (bytesPerSecond < 1024) {
    return `${bytesPerSecond.toFixed(1)} B/s`;
  } else if (bytesPerSecond < 1024 * 1024) {
    return `${(bytesPerSecond / 1024).toFixed(1)} KB/s`;
  } else {
    return `${(bytesPerSecond / (1024 * 1024)).toFixed(1)} MB/s`;
  }
}

// 格式化剩余时间
function formatTime(seconds) {
  if (seconds < 60) {
    return `${Math.round(seconds)}秒`;
  } else if (seconds < 3600) {
    return `${Math.round(seconds / 60)}分${Math.round(seconds % 60)}秒`;
  } else {
    return `${Math.round(seconds / 3600)}小时${Math.round((seconds % 3600) / 60)}分`;
  }
}

// 检查更新
async function checkForUpdates() {
  if (!isElectron.value || isCheckingUpdate.value) return;
  
  isCheckingUpdate.value = true;
  updateStatus.value = { status: 'checking' };
  
  try {
    const result = await apiCheckForUpdates();
    console.log('检查更新结果:', result);
    
    // 更新最后检查时间
    lastCheckTime.value = new Date();
    localStorage.setItem('lastUpdateCheck', lastCheckTime.value.toISOString());
    
    if (result.success) {
      // 检查成功，等待更新事件通知结果
    } else {
      // 检查失败
      updateStatus.value = { 
        status: 'error', 
        error: result.error || result.message || t('about.appInfo.checkFailed') 
      };
      notificationStore.error(t('about.appInfo.checkFailed'));
    }
  } catch (error) {
    console.error('检查更新失败:', error);
    updateStatus.value = { 
      status: 'error', 
      error: error instanceof Error ? error.message : String(error)
    };
    notificationStore.error(t('about.appInfo.checkFailed'));
  } finally {
    setTimeout(() => {
      isCheckingUpdate.value = false;
    }, 1000);
  }
}

// 下载更新
async function downloadUpdate() {
  if (!isElectron.value || updateStatus.value.status !== 'available' || isDownloading.value) return;
  
  try {
    isDownloading.value = true;
    downloadStartTime.value = Date.now();
    updateStatus.value.status = 'downloading';
    
    // 开始定时更新下载速度
    downloadTimer.value = setInterval(() => {
      if (updateStatus.value.progress) {
        const elapsed = (Date.now() - downloadStartTime.value) / 1000;
        const bytesPerSecond = updateStatus.value.progress.transferred / elapsed;
        updateStatus.value.downloadSpeed = bytesPerSecond;
        
        // 计算预计剩余时间
        const remainingBytes = updateStatus.value.progress.total - updateStatus.value.progress.transferred;
        updateStatus.value.estimatedTime = remainingBytes / bytesPerSecond;
      }
    }, 1000);

    const result = await apiDownloadUpdate();
    console.log('下载更新结果:', result);
    
    if (!result.success) {
      throw new Error(result.error || t('about.appInfo.downloadFailed'));
    }
  } catch (error) {
    console.error('下载更新失败:', error);
    updateStatus.value = { 
      status: 'error', 
      error: error instanceof Error ? error.message : String(error)
    };
    notificationStore.error(t('about.appInfo.downloadFailed'));
  } finally {
    if (downloadTimer.value) {
      clearInterval(downloadTimer.value);
      downloadTimer.value = null;
    }
    isDownloading.value = false;
  }
}

// 重试下载
async function retryDownload() {
  if (updateStatus.value.status === 'error') {
    updateStatus.value.status = 'available';
    await downloadUpdate();
  }
}

// 安装更新
async function installUpdate() {
  if (!isElectron.value || updateStatus.value.status !== 'downloaded') return;
  
  try {
    await apiInstallUpdate();
    notificationStore.success(t('about.appInfo.installSuccess'));
  } catch (error) {
    console.error('安装更新失败:', error);
    updateStatus.value = { 
      status: 'error', 
      error: error instanceof Error ? error.message : String(error)
    };
    notificationStore.error(t('about.appInfo.installFailed'));
  }
}

// 取消安装
async function cancelInstall() {
  if (updateStatus.value.status !== 'downloaded') return;
  
  try {
    // 这里需要调用后端的取消安装API
    await window.electronAPI.cancelUpdateInstall?.();
    updateStatus.value.status = 'available';
    notificationStore.info(t('about.appInfo.installCancelled'));
  } catch (error) {
    console.error('取消安装失败:', error);
  }
}

// 计算属性：下载进度百分比
const downloadProgress = computed(() => {
  try {
    if (!updateStatus.value || updateStatus.value.status !== 'downloading' || !updateStatus.value.progress) {
      return 0;
    }
    return Math.round(updateStatus.value.progress.percent || 0);
  } catch (err) {
    console.error('下载进度计算失败:', err);
    return 0;
  }
});

// 计算属性：更新状态文本
const updateStatusText = computed(() => {
  try {
    if (!updateStatus.value) return '';
    
    switch (updateStatus.value.status) {
      case 'checking':
        return t('about.appInfo.checking');
      case 'available':
        return t('about.appInfo.updateAvailable', { version: updateStatus.value.version || '未知版本' });
      case 'not-available':
        return t('about.appInfo.upToDate');
      case 'downloading':
        return t('about.appInfo.downloading', { progress: downloadProgress.value });
      case 'downloaded':
        return t('about.appInfo.readyToInstall', { version: updateStatus.value.version || '未知版本' });
      case 'error':
        return t('about.appInfo.updateError', { error: updateStatus.value.error || '未知错误' });
      default:
        return '';
    }
  } catch (err) {
    console.error('更新状态文本计算失败:', err);
    return '状态显示错误';
  }
});

// 更新状态监听器清理函数
let removeUpdateStatusListener = null;

// 组件挂载时
onMounted(async () => {
  try {
    // 检查是否在 Electron 环境
    isElectron.value = checkIsElectron();
    
    if (isElectron.value) {
      // 获取应用版本
      appVersion.value = await getCurrentVersion();
      
      // 获取 Electron 版本
      if (window.electronAPI) {
        electronVersion.value = window.electronAPI.getElectronVersion?.() || '';
      }
      
      // 设置更新状态监听
      removeUpdateStatusListener = onUpdateStatus((status) => {
        try {
          console.log('更新状态变化:', status);
          
          // 验证状态对象
          if (!status || typeof status !== 'object') {
            console.error('无效的更新状态:', status);
            return;
          }
          
          // 确保必要的字段存在
          updateStatus.value = {
            status: status.status || null,
            version: status.version || null,
            releaseDate: status.releaseDate || null,
            progress: status.progress || null,
            error: status.error || null,
            updatePath: status.updatePath || null  // 添加更新包路径
          };
          
          // 根据状态显示通知
          switch (status.status) {
            case 'available':
              notificationStore.info(t('about.appInfo.updateAvailable', { version: status.version || '未知版本' }));
              break;
            case 'downloaded':
              notificationStore.success(t('about.appInfo.downloadSuccess'));
            case 'error':
              notificationStore.error(status.error || t('about.appInfo.updateError'));
              break;
          }
        } catch (err) {
          console.error('处理更新状态失败:', err);
          updateStatus.value = {
            status: 'error',
            error: '处理更新状态时发生错误'
          };
        }
      });
    }

    // 如果当前是许可证标签页，加载许可证内容
    if (currentTab.value === 'license') {
      await loadLicenseContent();
    }
    
    // 加载上次检查时间
    const lastCheck = localStorage.getItem('lastUpdateCheck');
    if (lastCheck) {
      lastCheckTime.value = new Date(lastCheck);
    }
  } catch (error) {
    console.error('初始化应用信息失败:', error);
  }
});

// 组件卸载时清理监听器
onUnmounted(() => {
  if (removeUpdateStatusListener) {
    removeUpdateStatusListener();
  }
});
</script>

<style scoped>
@import '@/styles/AboutPage.css';
</style>
