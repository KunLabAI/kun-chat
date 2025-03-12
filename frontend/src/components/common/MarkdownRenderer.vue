<template>
  <div class="markdown-renderer">
    <div 
      class="markdown-content"
      v-html="renderedContent"
    ></div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import { useLocalization } from '@/i18n'

const props = defineProps({
  content: {
    type: String,
    required: true
  }
})

const { t } = useLocalization()

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
  
  return `<div class="code-block">
    <div class="code-header">
      ${lang ? `<span class="language-label">${lang}</span>` : ''}
      <button class="copy-button" title="${t('common.markdown.copy_code')}">
        <img src="/src/assets/icons/chat_copy.svg" alt="copy" class="copy-icon" />
      </button>
    </div>
    <pre><code class="hljs ${lang ? 'language-' + lang : ''}">${highlightedCode}</code></pre>
  </div>`
}

// 计算属性：渲染markdown内容
const renderedContent = computed(() => {
  return md.render(props.content || '')
})

// 添加复制功能
onMounted(() => {
  document.addEventListener('click', async (e) => {
    const button = e.target.closest('.copy-button')
    if (button) {
      const codeBlock = button.closest('.code-block')
      const code = codeBlock.querySelector('code').textContent
      
      try {
        await navigator.clipboard.writeText(code)
        
        // 替换为勾选图标
        const iconImg = button.querySelector('img')
        iconImg.src = '/src/assets/icons/chat_copy.svg'
        iconImg.classList.add('copied')
        
        setTimeout(() => {
          iconImg.classList.remove('copied')
        }, 2000)
      } catch (err) {
        console.error('Failed to copy code:', err)
      }
    }
  })
})
</script>

<style>
@import '@/styles/Markdown.css';
@import '@/styles/CodeBlock.css';

.markdown-renderer {
  width: 100%;
}

/* 覆盖 highlight.js 默认样式 */
.hljs {
  background: transparent !important;
  padding: 0 !important;
}


</style>