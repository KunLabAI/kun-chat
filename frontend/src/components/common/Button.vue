<template>
  <button
    :class="[
      'btn',
      `btn-${size}`,
      `btn-${variant}`,
      { 'btn-disabled': disabled },
      { 'btn-loading': loading },
      { 'btn-icon': icon }
    ]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <slot name="icon-left"></slot>
    <slot></slot>
    <slot name="icon-right"></slot>
  </button>
</template>

<script setup lang="ts">
import '@/styles/Button.css'

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'link'
type ButtonSize = 'sm' | 'md' | 'lg'

interface Props {
  variant?: ButtonVariant
  size?: ButtonSize
  disabled?: boolean
  loading?: boolean
  icon?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  icon: false
})
</script>
