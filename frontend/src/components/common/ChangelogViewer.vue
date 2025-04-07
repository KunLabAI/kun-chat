<template>
  <div class="changelog-viewer">
    <div v-if="loading" class="changelog-loading">
      {{ t('about.changelog.loading') }}
    </div>
    <div v-else-if="error" class="changelog-error">
      {{ t('about.changelog.error') }}
    </div>
    <div v-else class="changelog-content">
      <div v-for="release in releases" :key="release.tag_name" class="changelog-release">
        <div class="changelog-release-header">
          <h3 class="changelog-version">v{{ release.tag_name }}</h3>
          <span class="changelog-date">{{ formatDate(release.published_at) }}</span>
        </div>
        <div class="changelog-body" v-html="formatChangelog(release.body)"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';
import { getChangelog } from '@/api/changelogApi';
const { t } = useI18n();
const loading = ref(true);
const error = ref(null);
const releases = ref([]);

// 解析 CHANGELOG.md 内容
function parseChangelogContent(content) {
  const releasesList = [];
  const lines = content.split('\n');
  let currentRelease = null;
  
  for (const line of lines) {
    // 检查是否是版本标题行（例如：## [1.0.0] - 2023-01-01）
    const versionMatch = line.match(/^## \[(.*?)\] - (.*?)$/);
    if (versionMatch) {
      if (currentRelease) {
        releasesList.push(currentRelease);
      }
      currentRelease = {
        tag_name: versionMatch[1],
        published_at: versionMatch[2],
        body: ''
      };
    } else if (currentRelease) {
      currentRelease.body += line + '\n';
    }
  }
  
  // 添加最后一个版本
  if (currentRelease) {
    releasesList.push(currentRelease);
  }
  
  return releasesList;
}

async function fetchReleases() {
  try {
    loading.value = true;
    error.value = null;
    releases.value = [];
    
    // 检查是否在 Electron 环境中
    if (window.electronAPI) {
      // Electron 环境：从 GitHub API 获取
      const config = await window.electronAPI.getGitHubConfig();
      if (!config || !config.owner || !config.repo) {
        console.log('GitHub 配置不完整，跳过更新日志获取');
        return;
      }
      
      console.log('正在获取更新日志，配置:', {
        owner: config.owner,
        repo: config.repo
      });
      
      const response = await axios.get(`https://api.github.com/repos/${config.owner}/${config.repo}/releases`, {
        headers: {
          'Authorization': `Bearer ${config.token}`,
          'Accept': 'application/vnd.github.v3+json'
        },
        timeout: 10000
      });
      
      if (!response.data || !Array.isArray(response.data)) {
        throw new Error('无效的响应数据格式');
      }
      
      releases.value = response.data;
    } else {
      // Web 环境：从后端 API 获取
      console.log('在 Web 环境中，从后端获取更新日志');
      const response = await getChangelog();
      if (!response || !response.content) {
        throw new Error('无效的响应数据格式');
      }
      
      // 解析 CHANGELOG.md 内容并设置 releases
      releases.value = parseChangelogContent(response.content);
    }
    
    console.log('成功获取更新日志，版本数:', releases.value.length);
  } catch (err) {
    console.error('获取更新日志失败:', err);
    error.value = err.message;
    
    // 如果是网络错误，显示更友好的错误信息
    if (err.code === 'ECONNABORTED') {
      error.value = '网络连接超时，请检查网络设置';
    } else if (err.response?.status === 401) {
      error.value = 'GitHub API 认证失败';
    } else if (err.response?.status === 403) {
      error.value = '没有权限访问 GitHub 仓库';
    }
  } finally {
    loading.value = false;
  }
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

function formatChangelog(content) {
  try {
    if (!content) return '';
    
    // 转义 HTML 特殊字符
    let safeContent = content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
    
    // 将换行符转换为 <br>
    safeContent = safeContent.replace(/\n/g, '<br>');
    
    // 处理 Markdown 格式
    safeContent = safeContent
      // 处理加粗
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // 处理斜体
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // 处理代码
      .replace(/`(.*?)`/g, '<code>$1</code>')
      // 处理链接
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
      // 处理列表
      .replace(/^\s*[-*]\s+(.*)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      // 处理标题
      .replace(/^#\s+(.*)$/gm, '<h1>$1</h1>')
      .replace(/^##\s+(.*)$/gm, '<h2>$1</h2>')
      .replace(/^###\s+(.*)$/gm, '<h3>$1</h3>');
    
    return safeContent;
  } catch (err) {
    console.error('更新日志格式化失败:', err);
    // 如果格式化失败，返回原始内容，但确保安全
    return content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
      .replace(/\n/g, '<br>');
  }
}

onMounted(async () => {
  console.log('ChangelogViewer 组件已挂载');
  try {
    await fetchReleases();
  } catch (err) {
    console.error('获取更新日志失败:', err);
    error.value = '获取更新日志失败，请稍后重试';
  }
});
</script>

<style scoped>
.changelog-viewer {
  max-width: 100%;
  margin: 0 auto;
  position: relative;
  padding-left: 32px;
}

.changelog-content {
  position: relative;
}

.changelog-content::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: -32px;
  width: 2px;
  background-color: var(--primary-400);
}

.changelog-release {
  position: relative;
  margin-bottom: 32px;
  padding: 20px;
  border-radius: 8px;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.changelog-release::before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  left: -40px;
  top: 24px;
  border-radius: 50%;
  background-color: var(--primary-500);
  border: 2px solid var(--bg-color-light);
  z-index: 1;
}

.changelog-release::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 2px;
  left: -22px;
  top: 31px;
  background-color: var(--primary-400);
}

.changelog-release:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.changelog-release-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.changelog-version {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-600);
}

.changelog-date {
  color: var(--text-color-lighter);
  font-size: 14px;
}

.changelog-body {
  line-height: 1.6;
  color: var(--text-color);
}

.changelog-body :deep(code) {
  background-color: var(--gray-100);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

.changelog-body :deep(strong) {
  font-weight: 600;
}

.changelog-body :deep(em) {
  font-style: italic;
}

.changelog-body :deep(ul) {
  padding-left: 20px;
}

.changelog-body :deep(li) {
  margin-bottom: 8px;
}

.changelog-loading,
.changelog-error {
  text-align: center;
  padding: 20px;
  color: var(--text-color-lighter);
}

/* 深色模式适配 */
:deep(.dark) .changelog-release {
  background-color: var(--gray-800);
  border-color: var(--gray-700);
}

:deep(.dark) .changelog-release::before {
  border-color: var(--gray-700);
}

:deep(.dark) .changelog-version {
  color: var(--primary-400);
}

:deep(.dark) .changelog-body code {
  background-color: var(--gray-700);
}
</style>