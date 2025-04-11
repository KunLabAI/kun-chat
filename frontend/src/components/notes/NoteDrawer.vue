<template>
  <div>
    <div class="note-drawer-container" :class="{ 'note-drawer-open': isOpen }">
      <div class="note-drawer">
        <div class="note-drawer-header">
          <div class="drawer-title-container">
            <img src="@/assets/icons/sys_note.svg" alt="note" class="drawer-icon" />
            <h2 class="drawer-title">{{ t('notes.quick_note') }}</h2>
          </div>
          <button class="close-button" @click="close" :title="t('common.actions.close')">
            <img src="@/assets/icons/sys_close.svg" alt="close" class="close-icon" />
          </button>
        </div>
        <div class="note-drawer-content">
          <div class="editor-section">
            <div class="form-group">
              <input
                id="note-title"
                type="text"
                v-model="noteTitle"
                class="form-input"
                :placeholder="t('notes.form.title_placeholder')"
                required
              />
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
                  id="note-content"
                  v-model="noteContent"
                  class="form-textarea"
                  :placeholder="t('notes.form.content_placeholder')"
                  @input="updateTextStats"
                  @paste="handlePaste"
                  required
                ></textarea>
              </div>
            </div>
          </div>
        </div>
        
        <div class="note-drawer-footer">
          <Button 
            @click="close" 
            variant="secondary" 
            size="md"
          >
            {{ t('common.actions.cancel') }}
          </Button>
          <Button 
            @click="saveNote" 
            variant="primary" 
            size="md"
            :loading="isSaving"
            :disabled="!isValid || isSaving"
          >
            {{ t('common.actions.save') }}
          </Button>
        </div>
      </div>
    </div>

    <!-- 使用Teleport将预览面板传送到主布局中 -->
    <Teleport to="body">
      <!-- 预览抽屉 - 移到responsive-container内部 -->
      <div class="preview-drawer" :class="{ 'preview-drawer-open': isPreviewOpen }">
        <div class="preview-drawer-header">
          <div class="preview-title-container">
            <h3 class="preview-drawer-title">{{ t('notes.preview') }}</h3>
          </div>
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
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Teleport } from 'vue'
import { useNotesStore } from '@/stores/notes'
import { useNotificationStore } from '@/stores/notification'
import Button from '@/components/common/Button.vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { useLocalization } from '@/i18n'
import TurndownService from 'turndown'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  initialContent: {
    type: String,
    default: ''
  },
  conversationId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'saved'])

const { t } = useLocalization()
const notesStore = useNotesStore()
const notificationStore = useNotificationStore()

const noteTitle = ref('')
const noteContent = ref('')
const isSaving = ref(false)
const linesCount = ref(0)
const charsCount = ref(0)
const isPreviewOpen = ref(false)

// 初始化turndown服务
const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced'
})

// 添加代码块转换规则
turndownService.addRule('codeBlocks', {
  filter: function(node) {
    return (
      node.nodeName === 'PRE' &&
      node.firstChild &&
      node.firstChild.nodeName === 'CODE'
    );
  },
  replacement: function(content, node) {
    const language = node.firstChild.getAttribute('class') || '';
    const langMatch = language.match(/language-(\w+)/);
    const lang = langMatch ? langMatch[1] : '';
    return `\n\`\`\`${lang}\n${node.textContent}\n\`\`\`\n`;
  }
});

// 表单是否有效
const isValid = computed(() => {
  return noteTitle.value.trim() && noteContent.value.trim()
})

// 关闭抽屉
const close = () => {
  // 确保关闭预览
  isPreviewOpen.value = false
  emit('close')
}

// 切换预览显示
const togglePreview = () => {
  // 如果预览已经打开，直接关闭它，不管内容是否为空
  if (isPreviewOpen.value) {
    isPreviewOpen.value = false
    return
  }
  
  // 如果预览未打开，要打开预览前检查内容是否为空
  if (noteContent.value.trim()) {
    isPreviewOpen.value = true
  } else {
    notificationStore.info(t('notes.preview_requires_content'))
    // 确保预览面板关闭
    isPreviewOpen.value = false
  }
}

// 处理粘贴事件，将HTML转换为Markdown
const handlePaste = (e) => {
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
        replacement: function(content) {
          return content.trim() ? content : '';
        }
      });
      
      // 转换HTML到Markdown
      const markdown = turndownService.turndown(processedHtml);
      
      // 处理特殊转换失败的情况，尝试使用纯文本
      if (!markdown.trim() && e.clipboardData.getData('text/plain')) {
        const plainText = e.clipboardData.getData('text/plain');
        // 获取当前光标位置
        const textarea = e.target;
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
      const textarea = e.target;
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

// 追加内容到笔记
const appendContent = (content) => {
  if (!content || !content.trim()) return;
  
  // 如果当前内容不为空，添加换行符
  if (noteContent.value.trim()) {
    // 检查当前内容是否已经以换行符结束
    if (!noteContent.value.endsWith('\n') && !noteContent.value.endsWith('\r\n')) {
      noteContent.value += '\n\n';
    } else if (!noteContent.value.endsWith('\n\n') && !noteContent.value.endsWith('\r\n\r\n')) {
      // 确保有两个换行符
      noteContent.value += '\n';
    }
  }
  
  // 追加新内容
  noteContent.value += content;
  
  // 内容更新后更新文本统计
  updateTextStats();
  
  // 聚焦文本区域并滚动到底部
  nextTick(() => {
    const textarea = document.getElementById('note-content');
    if (textarea) {
      textarea.focus();
      textarea.scrollTop = textarea.scrollHeight;
    }
  });
}

// 将追加内容方法暴露给父组件
defineExpose({
  appendContent
})

// 保存笔记
const saveNote = async () => {
  if (!isValid.value || isSaving.value) return
  
  console.log('开始保存笔记:', { 
    title: noteTitle.value, 
    content: noteContent.value, 
    conversation_id: props.conversationId
  })
  
  isSaving.value = true
  
  try {
    // 确保conversationId正确传递
    const noteData = {
      title: noteTitle.value,
      content: noteContent.value,
      conversation_id: props.conversationId || undefined
    };
    
    console.log('发送笔记数据:', noteData);
    
    const result = await notesStore.createNote(noteData);
    
    console.log('保存笔记结果:', result);
    
    if (result && result.success) {
      emit('saved');
      close();
    } else {
      throw new Error('保存笔记失败');
    }
  } catch (error) {
    console.error('保存笔记失败:', error);
    notificationStore.showError(t('notes.notifications.create_error'));
  } finally {
    isSaving.value = false;
  }
}

// 清空内容
const clearContent = () => {
  noteContent.value = '';
  updateTextStats();
}

// 导出为Markdown文件
const exportToMarkdown = () => {
  if (!noteContent.value.trim()) {
    notificationStore.info(t('notes.export.empty_content'))
    return
  }
  
  try {
    // 创建Blob对象
    const blob = new Blob([noteContent.value], { type: 'text/markdown;charset=utf-8' })
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 设置文件名
    const fileName = noteTitle.value.trim() 
      ? `${noteTitle.value.trim()}.md` 
      : `note_${new Date().toISOString().slice(0, 10)}.md`
    
    link.download = fileName
    document.body.appendChild(link)
    
    // 触发下载
    link.click()
    
    // 清理
    URL.revokeObjectURL(url)
    document.body.removeChild(link)
    
    notificationStore.success(t('notes.notifications.export_success'))
  } catch (error) {
    console.error('导出笔记失败:', error)
    notificationStore.showError(t('notes.notifications.export_error'))
  }
}

// 更新文本统计信息
const updateTextStats = () => {
  const content = noteContent.value
  
  // 计算行数（根据换行符分割）
  linesCount.value = content ? content.split(/\r\n|\r|\n/).length : 0
  
  // 计算字符数
  charsCount.value = content.length
}

// 监听初始内容的变化
watch(() => props.initialContent, (newContent) => {
  if (newContent) {
    noteContent.value = newContent;
    updateTextStats();
  }
}, { immediate: true });

// 当抽屉打开时，将焦点放在标题输入框上
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    nextTick(() => {
      const titleInput = document.getElementById('note-title');
      if (titleInput) {
        titleInput.focus();
      }
    });
  } else {
    // 关闭抽屉时也关闭预览
    isPreviewOpen.value = false;
  }
});
</script>

<style scoped>
@import './NoteDrawer.css';
</style>