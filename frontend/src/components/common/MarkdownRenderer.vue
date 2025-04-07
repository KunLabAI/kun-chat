<template>
  <div class="markdown-renderer" ref="markdownRef">
    <div 
      class="markdown-content"
      v-html="renderedContent"
      :key="props.content"
    ></div>
    <!-- HTML渲染器 -->
    <div v-if="activeHtmlRender" class="html-render-container">
      <div class="html-render-header">
        <span class="html-render-title">{{ t('common.markdown.html_preview') }}</span>
        <div class="html-render-actions">
          <button class="html-render-action" @click="openInNewWindow" :title="t('common.markdown.open_in_new_window')">
            <img :src="getAssetPath('icons/sys_jump.svg')" alt="open" class="action-icon" />
          </button>
          <button class="html-render-close" @click="closeHtmlRender" :title="t('common.markdown.close')">
            <img :src="getAssetPath('icons/sys_close.svg')" alt="close" class="action-icon" />
          </button>
        </div>
      </div>
      <HtmlRenderer 
        :content="activeHtmlContent" 
        :language="activeHtmlLanguage"
        ref="htmlRendererRef"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import { useLocalization } from '@/i18n'
import HtmlRenderer from './HtmlRenderer.vue'

// 导入SVG图标
import copyIcon from '@/assets/icons/chat_copy.svg'
import previewIcon from '@/assets/icons/sys_codepreview.svg'
import checkIcon from '@/assets/icons/sys_check.svg'
import codeblockOpenIcon from '@/assets/icons/sys_codeblockcopen.svg'
import codeblockCloseIcon from '@/assets/icons/sys_codeblockclose.svg'

const props = defineProps({
  content: {
    type: String,
    required: true
  }
})

const { t } = useLocalization()

// 获取资源路径的辅助函数
function getAssetPath(path) {
  // 检测是否在Electron环境中
  if (window.electronAPI) {
    return new URL(`../../assets/${path}`, import.meta.url).href
  }
  return `/src/assets/${path}`
}

// HTML渲染相关状态
const activeHtmlRender = ref(false)
const activeHtmlContent = ref('')
const activeHtmlLanguage = ref('')

// 关闭HTML渲染
const closeHtmlRender = () => {
  activeHtmlRender.value = false
  activeHtmlContent.value = ''
  activeHtmlLanguage.value = ''
}

// 打开在新窗口
const openInNewWindow = () => {
  const newWindow = window.open('', '_blank');
  newWindow.document.write(activeHtmlContent.value);
}

// 初始化markdown-it
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
      } catch (__) {}
    }
    return '' // 使用默认的转义
  }
})

// 自定义fence渲染器来处理代码块
md.renderer.rules.fence = (tokens, idx) => {
  const token = tokens[idx]
  const code = token.content.trim()
  const lang = token.info.trim()
  
  let highlightedCode = code
  if (lang && hljs.getLanguage(lang)) {
    try {
      highlightedCode = hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
    } catch (__) {}
  }
  
  // 计算代码行数，用于显示行号
  const lineCount = code.split('\n').length
  const showLineNumbers = lineCount > 1 // 只有多行代码才显示行号
  
  // 为HTML和SVG代码块添加渲染按钮
  const renderButton = (lang === 'html' || lang === 'svg' || lang === 'javascript') 
    ? `<button class="render-button" data-lang="${lang}" data-code="${encodeURIComponent(code)}" title="${t('common.markdown.preview_code')}">
        <img src="${getAssetPath('icons/sys_codepreview.svg')}" alt="preview" class="preview-icon" />
      </button>`
    : ''
  
  // 只有当代码行数超过15行时才显示折叠/展开按钮
  const toggleButton = lineCount > 15 
    ? `<button class="toggle-button" data-expanded="false" title="${t('common.markdown.expand_code')}">
        <img src="${getAssetPath('icons/sys_codeblockcopen.svg')}" alt="expand" class="toggle-icon" />
      </button>`
    : ''
  
  return `<div class="code-block code-block-container">
    <div class="code-header">
      ${lang ? `<span class="language-label">${lang}${showLineNumbers ? ` • ${lineCount} 行` : ''}</span>` : ''}
      <div class="code-actions">
        ${renderButton}
        ${toggleButton}
        <button class="copy-button" title="${t('common.markdown.copy_code')}">
          <img src="${getAssetPath('icons/chat_copy.svg')}" alt="copy" class="copy-icon" />
        </button>
      </div>
    </div>
    <pre class="code-pre" data-auto-scroll="true"><code class="hljs ${lang ? 'language-' + lang : ''}">${highlightedCode}</code></pre>
  </div>`
}

// 计算属性：渲染markdown内容
const renderedContent = computed(() => {
  return md.render(props.content || '')
})

// 使用ref获取当前组件的DOM元素
const markdownRef = ref(null)
const htmlRendererRef = ref(null)

// 处理代码块的自动滚动
const handleCodeBlocksAutoScroll = () => {
  if (!markdownRef.value) return
  
  // 查找所有带有 data-auto-scroll 属性的代码块
  const codeBlocks = markdownRef.value.querySelectorAll('pre.code-pre[data-auto-scroll="true"]')
  
  codeBlocks.forEach(pre => {
    // 将滚动条滚动到底部
    pre.scrollTop = pre.scrollHeight
    
    // 标记为已处理，避免重复滚动
    pre.setAttribute('data-auto-scroll', 'false')
    
    // 阻止滚动事件冒泡，避免与页面滚动冲突
    pre.addEventListener('wheel', (e) => {
      e.stopPropagation()
    }, { passive: true })
    
    // 当用户手动滚动时，不再自动滚动
    pre.addEventListener('scroll', () => {
      pre.setAttribute('data-auto-scroll', 'false')
    }, { passive: true })
  })
}

// 添加复制和渲染功能
const handleClick = async (e) => {
  // 复制按钮功能
  const copyButton = e.target.closest('.copy-button')
  if (copyButton) {
    const codeBlock = copyButton.closest('.code-block')
    const code = codeBlock.querySelector('code').textContent
    
    try {
      await navigator.clipboard.writeText(code)
      
      // 替换为勾选图标
      const iconImg = copyButton.querySelector('img')
      if (iconImg) {
        const originalSrc = iconImg.src
        iconImg.src = getAssetPath('icons/sys_check.svg')
        iconImg.classList.add('copied')
        
        setTimeout(() => {
          iconImg.classList.remove('copied')
          iconImg.src = originalSrc
        }, 2000)
      }
    } catch (err) {
      console.error('Failed to copy code:', err)
    }
  }
  
  // 折叠/展开按钮功能
  const toggleButton = e.target.closest('.toggle-button')
  if (toggleButton) {
    const codeBlock = toggleButton.closest('.code-block')
    const pre = codeBlock.querySelector('pre.code-pre')
    const iconImg = toggleButton.querySelector('img')
    const isExpanded = toggleButton.getAttribute('data-expanded') === 'true'
    
    if (isExpanded) {
      // 折叠代码块
      pre.classList.remove('expanded')
      toggleButton.setAttribute('data-expanded', 'false')
      toggleButton.title = t('common.markdown.expand_code')
      iconImg.src = getAssetPath('icons/sys_codeblockcopen.svg')
      iconImg.alt = 'expand'
    } else {
      // 展开代码块
      pre.classList.add('expanded')
      toggleButton.setAttribute('data-expanded', 'true')
      toggleButton.title = t('common.markdown.collapse_code')
      iconImg.src = getAssetPath('icons/sys_codeblockclose.svg')
      iconImg.alt = 'collapse'
    }
  }
  
  // 渲染按钮功能
  const renderButton = e.target.closest('.render-button')
  if (renderButton && !activeHtmlRender.value) { 
    const lang = renderButton.getAttribute('data-lang')
    const code = decodeURIComponent(renderButton.getAttribute('data-code'))
    
    // 设置渲染状态
    activeHtmlLanguage.value = lang
    activeHtmlContent.value = code
    activeHtmlRender.value = true
  }
}

onMounted(() => {
  // 确保DOM已经更新后再添加事件监听器
  setTimeout(() => {
    if (markdownRef.value) {
      // 移除之前可能存在的事件监听器，避免重复添加
      markdownRef.value.removeEventListener('click', handleClick)
      // 添加新的事件监听器
      markdownRef.value.addEventListener('click', handleClick)
    }
    handleCodeBlocksAutoScroll()
  }, 0)
})

// 组件卸载时移除事件监听器
onBeforeUnmount(() => {
  if (markdownRef.value) {
    markdownRef.value.removeEventListener('click', handleClick)
  }
})

// 监听内容变化，处理代码块滚动
watch(() => props.content, () => {
  // 使用 nextTick 确保 DOM 已更新
  nextTick(() => {
    handleCodeBlocksAutoScroll()
  })
})
</script>

<style>
@import '@/styles/MarkdownStyles.css';
</style>