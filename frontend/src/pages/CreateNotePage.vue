<template>
  <MainLayout>
    <!-- 分屏预览布局 -->
    <div class="split-view-container" :class="{ 'active': isPreviewOpen }">
      <!-- 预览区域（左侧） -->
      <div class="split-view-preview">
        <div class="preview-drawer">
          <div class="preview-drawer-header">
            <div class="preview-title-container">
              <h3 class="preview-drawer-title">{{ t('notes.preview') }}</h3>
            </div>
            <button class="back-to-edit-button" @click="togglePreview" :title="t('notes.back_to_edit')">
              <img src="@/assets/icons/sys_close.svg" alt="close preview" class="close-icon" />
            </button>
          </div>
          <div class="preview-drawer-content">
            <div v-if="noteContent" class="preview-content">
              <MarkdownRenderer :content="noteContent" />
            </div>
            <div v-else class="preview-empty">
              {{ t('notes.preview_empty') }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 笔记创建区域（右侧） -->
      <div class="split-view-editor">
        <div class="note-create">
          <!-- 页面头部 -->
          <div class="page-header">
            <div class="header-content">
              <div class="title-group">
                <h1 class="main-title">{{ isEditMode ? t('notes.edit_note') : t('notes.create_note') }}</h1>
                <p class="sub-title">{{ isEditMode ? t('notes.edit_subtitle') : t('notes.create_subtitle') }}</p>
              </div>
              <div class="header-actions">
                <Button 
                  @click="cancelEdit" 
                  variant="secondary" 
                  size="md"
                  :disabled="isSubmitting"
                >
                  {{ t('common.actions.cancel') }}
                </Button>
                <Button 
                  @click="submitForm" 
                  variant="primary" 
                  size="md"
                  :loading="isSubmitting"
                  :disabled="isSubmitting || !isValid"
                >
                  {{ isEditMode ? t('common.actions.save') : t('common.actions.create') }}
                </Button>
              </div>
            </div>
          </div>

          <!-- 表单部分重构 - 采用快速笔记的布局样式 -->
          <div class="content-card">
            <div class="editor-section">
              <div class="form-group">
                <input
                  id="title"
                  type="text"
                  v-model="noteTitle"
                  class="form-input"
                  :class="{ error: formErrors.title }"
                  :placeholder="t('notes.form.title_placeholder')"
                  @input="clearError('title')"
                  required
                />
                <span v-if="formErrors.title" class="error-text">{{ formErrors.title }}</span>
              </div>

              <div class="form-group">
                <div class="code-block">
                  <div class="code-header">
                    <div class="language-info">
                      <span class="text-stats-tag">
                        <span class="stats-dot"></span>
                        {{ linesCount }} {{ t('notes.stats.lines') }} | {{ charsCount }} {{ t('notes.stats.chars') }}
                      </span>
                    </div>
                    <div class="header-right">
                      <button class="icon-button" @click="togglePreview" :title="t('notes.toggle_preview')" :class="{ 'active': isPreviewOpen }">
                        <img src="@/assets/icons/sys_notepreview.svg" alt="preview" class="button-icon" />
                      </button>
                      <button class="icon-button" @click="exportToMarkdown" :title="t('notes.export.tooltip')" :disabled="!noteContent.trim()">
                        <img src="@/assets/icons/sys_output.svg" alt="export" class="button-icon" />
                      </button>
                      <button class="icon-button" @click="clearContent" :title="t('common.actions.clear')">
                        <img src="@/assets/icons/model_delete.svg" alt="clear" class="button-icon" />
                      </button>
                    </div>
                  </div>
                  <textarea
                    id="content"
                    v-model="noteContent"
                    class="form-textarea"
                    :class="{ error: formErrors.content }"
                    :placeholder="t('notes.form.content_placeholder')"
                    @input="updateTextStats"
                    @paste="handlePaste"
                    required
                  ></textarea>
                </div>
                <span v-if="formErrors.content" class="error-text">{{ formErrors.content }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 在预览未激活时显示的主笔记创建区域 -->
    <div class="note-create" v-if="!isPreviewOpen">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="main-title">{{ isEditMode ? t('notes.edit_note') : t('notes.create_note') }}</h1>
            <p class="sub-title">{{ isEditMode ? t('notes.edit_subtitle') : t('notes.create_subtitle') }}</p>
          </div>
          <div class="header-actions">
            <Button 
              @click="cancelEdit" 
              variant="secondary" 
              size="md"
              :disabled="isSubmitting"
            >
              {{ t('common.actions.cancel') }}
            </Button>
            <Button 
              @click="submitForm" 
              variant="primary" 
              size="md"
              :loading="isSubmitting"
              :disabled="isSubmitting || !isValid"
            >
              {{ isEditMode ? t('common.actions.save') : t('common.actions.create') }}
            </Button>
          </div>
        </div>
      </div>

      <!-- 表单部分重构 - 采用快速笔记的布局样式 -->
      <div class="content-card">
        <div class="editor-section">
          <div class="form-group">
            <input
              id="title-main"
              type="text"
              v-model="noteTitle"
              class="form-input"
              :class="{ error: formErrors.title }"
              :placeholder="t('notes.form.title_placeholder')"
              @input="clearError('title')"
              required
            />
            <span v-if="formErrors.title" class="error-text">{{ formErrors.title }}</span>
          </div>

          <div class="form-group">
            <div class="code-block">
              <div class="code-header">
                <div class="language-info">
                  <span class="text-stats-tag">
                    <span class="stats-dot"></span>
                    {{ linesCount }} {{ t('notes.stats.lines') }} | {{ charsCount }} {{ t('notes.stats.chars') }}
                  </span>
                </div>
                <div class="header-right">
                  <button class="icon-button" @click="togglePreview" :title="t('notes.toggle_preview')" :class="{ 'active': isPreviewOpen }">
                    <img src="@/assets/icons/sys_notepreview.svg" alt="preview" class="button-icon" />
                  </button>
                  <button class="icon-button" @click="exportToMarkdown" :title="t('notes.export.tooltip')" :disabled="!noteContent.trim()">
                    <img src="@/assets/icons/sys_output.svg" alt="export" class="button-icon" />
                  </button>
                  <button class="icon-button" @click="clearContent" :title="t('common.actions.clear')">
                    <img src="@/assets/icons/model_delete.svg" alt="clear" class="button-icon" />
                  </button>
                </div>
              </div>
              <textarea
                id="content-main"
                v-model="noteContent"
                class="form-textarea"
                :class="{ error: formErrors.content }"
                :placeholder="t('notes.form.content_placeholder')"
                @input="updateTextStats"
                @paste="handlePaste"
                required
              ></textarea>
            </div>
            <span v-if="formErrors.content" class="error-text">{{ formErrors.content }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 取消确认对话框 -->
    <Dialog
      v-model="showCancelDialog"
      :title="t('notes.cancel_dialog.title')"
      :confirm-text="t('notes.cancel_dialog.confirm')"
      :cancel-text="t('notes.cancel_dialog.cancel')"
      @confirm="confirmCancel"
    >
      <p>{{ t('notes.cancel_dialog.message') }}</p>
    </Dialog>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNotesStore } from '@/stores/notes'
import { useNotificationStore } from '@/stores/notification'
import { useLocalization } from '@/i18n'
import MainLayout from '@/layouts/MainLayout.vue'
import Button from '@/components/common/Button.vue'
import Dialog from '@/components/common/Dialog.vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import TurndownService from 'turndown'

// 多语言
const { t } = useLocalization()

// Store
const notesStore = useNotesStore()
const notificationStore = useNotificationStore()
const router = useRouter()
const route = useRoute()

// 获取路由参数
const noteId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})

// 编辑模式判断
const isEditMode = computed(() => !!noteId.value)

// 表单数据
const noteTitle = ref('')
const noteContent = ref('')
const isSubmitting = ref(false)
const formErrors = ref({
  title: '',
  content: ''
})

// 取消对话框
const showCancelDialog = ref(false)

// 语言检测和预览功能
const isPreviewOpen = ref(false)
const copySuccess = ref(false)
const clearSuccess = ref(false)
const linesCount = ref(0)
const charsCount = ref(0)

// 表单是否有效
const isValid = computed(() => {
  return noteTitle.value.trim() && noteContent.value.trim()
})

// 初始化turndown服务
const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced'
})

// 添加代码块转换规则
turndownService.addRule('codeBlocks', {
  filter: function(node: Element) {
    return (
      node.nodeName === 'PRE' &&
      node.firstChild &&
      node.firstChild.nodeName === 'CODE'
    );
  },
  replacement: function(_content: string, node: Element) {
    const codeElement = node.firstChild as Element;
    const language = codeElement?.getAttribute?.('class') || '';
    const langMatch = language.match(/language-(\w+)/);
    const lang = langMatch ? langMatch[1] : '';
    return `\n\`\`\`${lang}\n${node.textContent}\n\`\`\`\n`;
  }
});

// 为聊天消息添加特殊规则
turndownService.addRule('chatMessages', {
  filter: '.message-bubble, .message-content, .chat-message',
  replacement: function(content: string) {
    return content.trim() ? content : '';
  }
});

// 加载笔记数据（编辑模式）
const loadNote = async () => {
  if (!isEditMode.value || !noteId.value) return

  try {
    const { success, data } = await notesStore.fetchNote(noteId.value)
    
    if (success && data) {
      noteTitle.value = data.title
      noteContent.value = data.content || ''
      updateTextStats()
    } else {
      notificationStore.showError(t('notes.notifications.load_error'))
      router.push('/notes')
    }
  } catch (error) {
    console.error('加载笔记失败:', error)
    notificationStore.showError(t('notes.notifications.load_error'))
    router.push('/notes')
  }
}

// 表单验证
const validateForm = () => {
  let isValid = true
  formErrors.value = {
    title: '',
    content: ''
  }

  if (!noteTitle.value.trim()) {
    formErrors.value.title = t('notes.form.title_required')
    isValid = false
  }

  if (!noteContent.value.trim()) {
    formErrors.value.content = t('notes.form.content_required')
    isValid = false
  }

  return isValid
}

// 提交表单
const submitForm = async () => {
  if (!validateForm() || isSubmitting.value) return
  
  isSubmitting.value = true
  
  try {
    if (isEditMode.value && noteId.value) {
      // 更新笔记
      const { success } = await notesStore.updateNote(noteId.value, {
        title: noteTitle.value,
        content: noteContent.value
      })
      
      if (success) {
        router.push('/notes')
      }
    } else {
      // 创建笔记
      const { success } = await notesStore.createNote({
        title: noteTitle.value,
        content: noteContent.value
      })
      
      if (success) {
        router.push('/notes')
      }
    }
  } catch (error) {
    console.error('保存笔记失败:', error)
    isEditMode.value 
      ? notificationStore.showError(t('notes.notifications.update_error'))
      : notificationStore.showError(t('notes.notifications.create_error'))
  } finally {
    isSubmitting.value = false
  }
}

// 取消创建/编辑
const cancelEdit = () => {
  if (noteTitle.value || noteContent.value) {
    showCancelDialog.value = true
  } else {
    router.push('/notes')
  }
}

// 确认放弃编辑
const confirmCancel = () => {
  showCancelDialog.value = false
  router.push('/notes')
}

// 监听表单输入，清除相应的错误
const clearError = (field: string) => {
  if (field in formErrors.value) {
    formErrors.value[field as keyof typeof formErrors.value] = ''
  }
}

// 切换预览显示
const togglePreview = () => {
  if (isPreviewOpen.value) {
    isPreviewOpen.value = false
    return
  }
  
  if (noteContent.value.trim()) {
    isPreviewOpen.value = true
  } else {
    notificationStore.info(t('notes.preview_requires_content'))
    isPreviewOpen.value = false
  }
}

// 复制笔记内容
async function copyContent() {
  if (!noteContent.value) return
  
  try {
    await navigator.clipboard.writeText(noteContent.value)
    copySuccess.value = true
    notificationStore.showSuccess(t('chat.notifications.copy_success'))
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('复制失败:', error)
    notificationStore.showError(t('chat.notifications.copy_error'))
  }
}

// 导出为Markdown文件
const exportToMarkdown = () => {
  if (!noteContent.value.trim()) {
    notificationStore.info(t('notes.export.empty_content'))
    return
  }
  
  try {
    // 设置文件名
    const fileName = noteTitle.value.trim() 
      ? `${noteTitle.value.trim()}.md` 
      : `note_${new Date().toISOString().slice(0, 10)}.md`
    
    // 检测是否在Electron环境中
    const isElectron = () => {
      // 在Electron中，userAgent通常包含Electron字样
      return navigator.userAgent.toLowerCase().indexOf('electron') !== -1
    }
    
    // 创建Blob对象
    const blob = new Blob([noteContent.value], { type: 'text/markdown;charset=utf-8' })
    
    if (isElectron()) {
      console.log('在Electron环境中导出文件')
      
      // 对于Electron环境，使用dataURL来避免file://协议问题
      const dataUrl = URL.createObjectURL(blob)
      
      // 创建一个不可见的a元素，但不添加到DOM
      const a = document.createElement('a')
      a.style.position = 'absolute'
      a.style.opacity = '0'
      a.style.visibility = 'hidden'
      a.style.pointerEvents = 'none'  
      a.href = dataUrl
      a.download = fileName
      a.setAttribute('target', '_self') // 重要：确保在当前窗口打开
      
      // 使用click事件而不是直接点击DOM元素
      const clickEvent = new MouseEvent('click', {
        view: window,
        bubbles: false,
        cancelable: true
      })
      a.dispatchEvent(clickEvent)
      
      // 立即销毁URL
      setTimeout(() => {
        URL.revokeObjectURL(dataUrl)
      }, 100)
    } else {
      // 浏览器环境 - 标准下载方式
      const url = URL.createObjectURL(blob)
      
      // 使用新的a元素进行下载
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      
      // 立即从DOM中移除
      document.body.removeChild(a)
      
      // 延迟释放URL对象
      setTimeout(() => {
        URL.revokeObjectURL(url)
      }, 100)
    }
    
    notificationStore.success(t('notes.notifications.export_success'))
  } catch (error) {
    console.error('导出笔记失败:', error)
    notificationStore.showError(t('notes.notifications.export_error'))
  }
}

// 清空笔记内容
function clearContent() {
  noteContent.value = ''
  clearSuccess.value = true
  setTimeout(() => {
    clearSuccess.value = false
  }, 2000)
  
  // 同时清除相关错误
  clearError('content')
  
  // 更新文本统计
  updateTextStats()
}

// 更新文本统计
function updateTextStats() {
  const content = noteContent.value
  
  // 计算行数（根据换行符分割）
  linesCount.value = content ? content.split(/\r\n|\r|\n/).length : 0
  
  // 计算字符数
  charsCount.value = content.length
  
  // 清除内容错误
  clearError('content')
}

// 处理粘贴事件，将HTML转换为Markdown
const handlePaste = (e: ClipboardEvent) => {
  try {
    // 如果粘贴的是HTML内容
    if (e.clipboardData && e.clipboardData.getData('text/html')) {
      e.preventDefault();
      const html = e.clipboardData.getData('text/html');
      
      // 对HTML进行预处理，增强转换能力
      let processedHtml = html
        // 移除可能干扰转换的一些元素和属性
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
        .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
        .replace(/ class="[^"]*"/g, '')
        .replace(/ style="[^"]*"/g, '');
      
      // 为聊天消息添加特殊规则
      turndownService.addRule('chatMessages', {
        filter: '.message-bubble, .message-content, .chat-message',
        replacement: function(content: string) {
          return content.trim() ? content : '';
        }
      });
      
      // 转换HTML到Markdown
      const markdown = turndownService.turndown(processedHtml);
      
      // 处理特殊转换失败的情况，尝试使用纯文本
      if (!markdown.trim() && e.clipboardData.getData('text/plain')) {
        const plainText = e.clipboardData.getData('text/plain');
        // 获取当前光标位置
        const textarea = e.target as HTMLTextAreaElement;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        
        // 在光标位置插入文本
        noteContent.value = 
          noteContent.value.substring(0, start) + 
          plainText + 
          noteContent.value.substring(end);
          
        // 更新光标位置
        nextTick(() => {
          textarea.selectionStart = textarea.selectionEnd = start + plainText.length;
        });
        
        updateTextStats();
        return;
      }
      
      // 在光标位置插入转换后的markdown
      const textarea = e.target as HTMLTextAreaElement;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      noteContent.value = 
        noteContent.value.substring(0, start) + 
        markdown + 
        noteContent.value.substring(end);
        
      // 更新光标位置
      nextTick(() => {
        textarea.selectionStart = textarea.selectionEnd = start + markdown.length;
      });
      
      updateTextStats();
    }
  } catch (error) {
    console.error('处理粘贴内容失败:', error);
    // 出错时不拦截，让浏览器默认行为处理粘贴
  }
};

// 生命周期钩子
onMounted(() => {
  loadNote()
})
</script>

<style scoped>
@import '@/styles/CreateNotePage.css';
</style> 