<template>
  <div class="markdown-renderer" ref="markdownRef">
    <div 
      class="markdown-content"
      v-html="renderedContent"
    ></div>
    <!-- HTML渲染器 -->
    <div v-if="activeHtmlRender" class="html-render-container">
      <div class="html-render-header">
        <span class="html-render-title">HTML代码预览</span>
        <div class="html-render-actions">
          <button class="html-render-action" @click="openInNewWindow" title="在新窗口打开">
            <img src="/src/assets/icons/sys_jump.svg" alt="open" class="action-icon" />
          </button>
          <button class="html-render-close" @click="closeHtmlRender" title="关闭">
            <img src="/src/assets/icons/sys_close.svg" alt="close" class="action-icon" />
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
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import { useLocalization } from '@/i18n'
import HtmlRenderer from './HtmlRenderer.vue'

const props = defineProps({
  content: {
    type: String,
    required: true
  }
})

const { t } = useLocalization()

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
  
  // 为HTML和SVG代码块添加渲染按钮
  const renderButton = (lang === 'html' || lang === 'svg' || lang === 'javascript') 
    ? `<button class="render-button" data-lang="${lang}" data-code="${encodeURIComponent(code)}" title="预览代码">
        <img src="/src/assets/icons/sys_codepreview.svg" alt="preview" class="preview-icon" />
      </button>`
    : ''
  
  return `<div class="code-block code-block-container">
    <div class="code-header">
      ${lang ? `<span class="language-label">${lang}</span>` : ''}
      <div class="code-actions">
        ${renderButton}
        <button class="copy-button" title="复制代码">
          <img src="/src/assets/icons/chat_copy.svg" alt="copy" class="copy-icon" />
        </button>
      </div>
    </div>
    <pre><code class="hljs ${lang ? 'language-' + lang : ''}">${highlightedCode}</code></pre>
  </div>`
}

// 计算属性：渲染markdown内容
const renderedContent = computed(() => {
  return md.render(props.content || '')
})

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
      iconImg.src = '/src/assets/icons/sys_check.svg'
      iconImg.classList.add('copied')
      
      setTimeout(() => {
        iconImg.classList.remove('copied')
        iconImg.src = '/src/assets/icons/chat_copy.svg'
      }, 2000)
    } catch (err) {
      console.error('Failed to copy code:', err)
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

// 使用ref获取当前组件的DOM元素
const markdownRef = ref(null)

onMounted(() => {
  // 使用nextTick确保DOM已经更新
  setTimeout(() => {
    if (markdownRef.value) {
      markdownRef.value.addEventListener('click', handleClick)
    }
  }, 0)
})

// 组件卸载时移除事件监听器
onBeforeUnmount(() => {
  if (markdownRef.value) {
    markdownRef.value.removeEventListener('click', handleClick)
  }
})
</script>

<style >
@import '@/styles/MarkdownStyles.css';
</style>