<template>
  <MainLayout>
    <div class="prompt-create">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="main-title">{{ isEdit ? t('prompt.edit_prompt') : t('prompt.create_prompt') }}</h1>
            <p class="sub-title">{{ isEdit ? t('prompt.subtitle') : t('prompt.subtitle') }}</p>
          </div>
          <div class="header-actions">
            <Button variant="link" size="md" @click="router.back()">
              {{ t('common.actions.back') }}
            </Button>
            <Button
              variant="primary"
              size="md"
              @click="handleSubmit"
              :loading="isSubmitting"
              :disabled="isSubmitting"
            >
              {{ isEdit ? t('common.actions.save') : t('prompt.form.create') }}
            </Button>
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="content-card">
        <div class="create-form">
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">{{ t('prompt.form.title_label') }}</h3>
            </div>
            <div class="section-content">
              <div class="form-group">
                <label class="form-label" for="title">
                  {{ t('prompt.form.title_label') }}
                  <span class="required">*</span>
                </label>
                <input
                  id="title"
                  v-model="form.title"
                  type="text"
                  class="form-input"
                  :class="{ error: errors.title }"
                  :placeholder="t('prompt.form.title_placeholder')"
                  required
                />
                <span v-if="errors.title" class="error-text">{{ errors.title }}</span>
              </div>

              <div class="form-group">
                <label class="form-label" for="tags">{{ t('prompt.form.tags_label') }}</label>
                <input
                  id="tags"
                  v-model="tagsInput"
                  type="text"
                  class="form-input"
                  :placeholder="t('prompt.form.tags_placeholder')"
                  @keydown.enter.prevent="handleTagInput"
                  @keydown.comma.prevent="handleTagInput"
                />
                <div v-if="currentTags.length > 0" class="tags-container">
                  <span 
                    v-for="tag in currentTags" 
                    :key="tag.text" 
                    class="tag"
                    :style="{ backgroundColor: tag.color }"
                  >
                    {{ tag.text }}
                    <button type="button" class="tag-remove" @click="removeTag(tag.text)">×</button>
                  </span>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label" for="content">
                  {{ t('prompt.form.content_label') }}
                  <span class="required">*</span>
                </label>
                <div class="code-block">
                  <div class="code-header">
                    <div class="header-right">
                      <button class="clear-button" @click="clearContent">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3-3h8M9 3v3M15 3v3M4 6h16"/>
                        </svg>
                        {{ t('common.actions.clear') }}
                      </button>
                      <button class="copy-button" @click="copyContent">{{ t('prompt.card.copy') }}</button>
                    </div>
                  </div>
                  <textarea
                    id="content"
                    v-model="form.content"
                    class="form-textarea"
                    :class="{ error: errors.content }"
                    :placeholder="t('prompt.form.content_placeholder')"
                    required
                  ></textarea>
                </div>
                <span v-if="errors.content" class="error-text">{{ errors.content }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Prompt } from '@/api/prompts'
import MainLayout from '@/layouts/MainLayout.vue'
import Button from '@/components/common/Button.vue'
import { usePromptStore } from '@/stores/promptStore'
import { useNotificationStore } from '@/stores/notification'
import { useLocalization } from '@/i18n'

const router = useRouter()
const route = useRoute()
const promptStore = usePromptStore()
const notification = useNotificationStore()
const { t } = useLocalization()

const isSubmitting = ref(false)
const tagsInput = ref('')
const currentTags = ref<{ text: string; color: string }[]>([])
const loadedPrompt = ref<Prompt | null>(null)

const form = reactive({
  title: '',
  content: '',
  tags: [] as { text: string; color: string }[]
})

const errors = reactive({
  title: '',
  content: ''
})

const isEdit = computed(() => route.name === 'editPrompt')

const tagColors = [
  '#f44336',
  '#e91e63',
  '#e040fb',
  '#7e57c2',
  '#5c6bc0',
  '#2196f3',
  '#03a9f4',
  '#00bcd4',
  '#ff5722',
  '#78909c'
]

const getRandomColor = () => {
  const index = Math.floor(Math.random() * tagColors.length)
  return tagColors[index]
}

onMounted(async () => {
  if (isEdit.value) {
    const promptId = route.params.id as string
    try {
      // 将获取的 prompt 存储到 ref 中
      loadedPrompt.value = await promptStore.getPrompt(promptId)
      form.title = loadedPrompt.value.title
      form.content = loadedPrompt.value.content
      currentTags.value = loadedPrompt.value.tags
      form.tags = currentTags.value
    } catch (error: any) {
      notification.error(t('prompt.notifications.get_error'))
      router.push('/prompts')
    }
  }
})

function validateForm() {
  let isValid = true
  errors.title = ''
  errors.content = ''

  if (!form.title.trim()) {
    errors.title = t('prompt.form.title_label') + ' ' + t('common.status.error')
    isValid = false
  }

  if (!form.content.trim()) {
    errors.content = t('prompt.form.content_label') + ' ' + t('common.status.error')
    isValid = false
  }

  return isValid
}

async function handleSubmit() {
  if (!validateForm()) return

  // 构建提交数据，确保格式正确
  const promptData = {
    title: form.title,
    content: form.content,
    tags: currentTags.value.map(tag => ({
      text: tag.text,
      color: tag.color
    }))
  }

  isSubmitting.value = true
  try {
    if (isEdit.value) {
      const updateData: Prompt = {
        id: route.params.id as string,
        title: promptData.title,
        content: promptData.content,
        tags: promptData.tags,
        created_at: loadedPrompt.value?.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      await promptStore.updatePrompt(updateData)
      notification.success(t('prompt.notifications.update_success'))
    } else {
      await promptStore.createPrompt(promptData)
      notification.success(t('prompt.notifications.create_success'))
    }
    router.push('/prompts')
  } catch (error: any) {
    notification.error(error?.message || (isEdit.value ? t('prompt.notifications.update_error') : t('prompt.notifications.create_error')))
  } finally {
    isSubmitting.value = false
  }
}

// 复制提示词内容
function copyContent() {
  if (!form.content) return
  navigator.clipboard.writeText(form.content).then(() => {
    notification.success(t('prompt.notifications.copied'))
  }).catch(() => {
    notification.error(t('common.status.error'))
  })
}

// 清空提示词内容
function clearContent() {
  form.content = ''
}

// 处理标签输入
function handleTagInput(event: KeyboardEvent) {
  const value = tagsInput.value.trim()
  if (!value) return

  // 移除逗号
  const tagText = value.replace(/,/g, '').trim()
  if (!tagText) return

  // 检查是否已存在相同的标签
  if (!currentTags.value.some(tag => tag.text === tagText)) {
    const color = getRandomColor()
    currentTags.value.push({ text: tagText, color })
    form.tags = currentTags.value
  }

  // 清空输入
  tagsInput.value = ''
}

// 移除标签
function removeTag(tagText: string) {
  currentTags.value = currentTags.value.filter(tag => tag.text !== tagText)
  form.tags = currentTags.value
}
</script>

<style scoped>
@import '@/styles/CreatePromptPage.css';
</style>
