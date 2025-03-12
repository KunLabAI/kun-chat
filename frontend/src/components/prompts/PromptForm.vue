<template>
  <form @submit.prevent="handleSubmit" class="prompt-form">
    <div class="form-group">
      <label for="title" class="form-label">{{ t('prompt.form.title_label') }}</label>
      <input
        id="title"
        v-model="form.title"
        type="text"
        class="form-input"
        :placeholder="t('prompt.form.title_placeholder')"
        required
      />
    </div>

    <div class="form-group">
      <label for="content" class="form-label">{{ t('prompt.form.content_label') }}</label>
      <textarea
        id="content"
        v-model="form.content"
        class="form-textarea"
        rows="6"
        :placeholder="t('prompt.form.content_placeholder')"
        required
      ></textarea>
    </div>

    <div class="form-group">
      <label for="tags" class="form-label">{{ t('prompt.form.tags_label') }}</label>
      <input
        id="tags"
        v-model="tagsInput"
        type="text"
        class="form-input"
        :placeholder="t('prompt.form.tags_placeholder')"
      />
    </div>

    <div class="form-actions">
      <Button
        type="button"
        variant="secondary"
        @click="$emit('cancel')"
      >
        {{ t('prompt.form.cancel') }}
      </Button>
      <Button
        type="submit"
        variant="primary"
        :loading="loading"
      >
        {{ initialData?.id ? t('prompt.form.save') : t('prompt.form.create') }}
      </Button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Button from '../common/Button.vue'
import type { Prompt, PromptBase } from '../../api/prompts'
import { useLocalization } from '@/i18n'

const { t } = useLocalization()

interface Props {
  initialData?: Partial<Prompt>
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({}),
  loading: false
})

const emit = defineEmits<{
  (e: 'submit', data: PromptBase): void
  (e: 'cancel'): void
}>()

const form = ref({
  title: props.initialData?.title || '',
  content: props.initialData?.content || '',
})

const tagsInput = ref(props.initialData?.tags?.join(',') || '')

function handleSubmit() {
  const tags = tagsInput.value
    ? tagsInput.value.split(',').map(tag => tag.trim()).filter(Boolean)
    : undefined

  emit('submit', {
    title: form.value.title,
    content: form.value.content,
    tags
  })
}
</script>


