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
          <h3 class="changelog-version">{{ release.tag_name }}</h3>
          <span class="changelog-date">{{ formatDate(release.published_at) }}</span>
        </div>
        <!-- 使用MarkdownRenderer组件渲染更新日志内容 -->
        <MarkdownRenderer :content="release.body" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';
import { getChangelog } from '@/api/changelogApi';
import MarkdownRenderer from './MarkdownRenderer.vue';

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
    
    // 首先从GitHub API获取更新日志（优先级最高）
    if (window.electronAPI) {
      try {
        console.log('尝试从 GitHub API 获取更新日志');
        const config = await window.electronAPI.getGitHubConfig();
        if (!config || !config.owner || !config.repo) {
          throw new Error('GitHub 配置不完整');
        }
        
        const headers = {
          'Accept': 'application/vnd.github.v3+json'
        };
        
        // 如果存在token，添加授权头
        if (config.token) {
          headers['Authorization'] = `token ${config.token}`;
          console.log('已添加GitHub授权令牌');
        }
        
        const response = await axios.get(`https://api.github.com/repos/${config.owner}/${config.repo}/releases`, {
          headers: headers,
          timeout: 15000,
          skipAuthRefresh: true,
          skipErrorHandler: true,
          withCredentials: false
        });
        
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          console.log('从 GitHub API 获取更新日志成功');
          releases.value = response.data;
          return;
        } else {
          console.log('GitHub API 未返回有效的发布信息，尝试其他方式');
          throw new Error('GitHub API 未返回有效的发布信息');
        }
      } catch (githubErr) {
        console.error('从 GitHub API 获取更新日志失败:', githubErr);
        // 继续尝试其他方式
      }
      
      // 次优先：从本地文件读取
      try {
        console.log('尝试直接读取本地 CHANGELOG.md 文件');
        const content = await window.electronAPI.readLocalFile('CHANGELOG.md');
        if (content) {
          const parsedReleases = parseChangelogContent(content);
          if (parsedReleases.length > 0) {
            console.log('从本地文件读取更新日志成功');
            releases.value = parsedReleases;
            return;
          }
        }
        throw new Error('无法读取本地 CHANGELOG.md 文件');
      } catch (fileErr) {
        console.error('读取本地 CHANGELOG.md 文件失败:', fileErr);
        // 继续尝试下一种方式
      }
    }
    
    // 最后尝试从后端 API 获取
    try {
      console.log('尝试从后端获取更新日志');
      const response = await getChangelog();
      if (response && response.content) {
        // 解析 CHANGELOG.md 内容并设置 releases
        const parsedReleases = parseChangelogContent(response.content);
        if (parsedReleases.length > 0) {
          console.log('从后端获取更新日志成功');
          releases.value = parsedReleases;
          return;
        }
      }
      throw new Error('从后端获取更新日志失败或内容无效');
    } catch (apiErr) {
      console.error('从后端获取更新日志失败:', apiErr);
      
      // 所有方式都失败，使用默认内容
      console.log('所有获取方式均失败，使用默认更新日志');
      const defaultChangelog = `# 更新日志\n\n## [0.0.1] - ${new Date().toISOString().split('T')[0]}\n\n### 新增\n- 初始版本发布\n`;
      const parsedReleases = parseChangelogContent(defaultChangelog);
      releases.value = parsedReleases;
    }
  } catch (err) {
    console.error('获取更新日志失败:', err);
    error.value = t('about.changelog.error');
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

<style>
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

/* 自定义标题样式 */
.changelog-body >>> .changelog-section-title {
  margin: 16px 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-500);
  border-bottom: none;
  padding-bottom: 0;
}

/* 自定义列表样式 */
.changelog-body >>> ul {
  margin: 8px 0 16px;
  padding-left: 20px;
  list-style-type: disc;
}

.changelog-body >>> li {
  margin-bottom: 8px;
  line-height: 1.5;
  position: relative;
  padding-left: 8px;
}

/* 自定义文本样式 */
.changelog-body >>> code {
  background-color: var(--gray-100);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.changelog-body >>> strong {
  font-weight: 600;
  color: var(--text-color-dark);
}

.changelog-body >>> em {
  font-style: italic;
}

.changelog-loading,
.changelog-error {
  text-align: center;
  padding: 20px;
  color: var(--text-color-lighter);
}

/* 深色模式适配 */
.dark .changelog-release {
  background-color: var(--gray-1000);
}

.dark .changelog-release::before {
  border-color: var(--gray-700);
}

.dark .changelog-version {
  color: var(--primary-400);
}

.dark .changelog-body >>> .changelog-section-title {
  color: var(--primary-300);
}

.dark .changelog-body >>> code {
  background-color: var(--gray-700);
}

.dark .changelog-body >>> strong {
  color: var(--text-color-light);
}
</style>