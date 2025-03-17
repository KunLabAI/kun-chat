<template>
  <div class="plain-text-renderer">
    <div class="plain-text-content">{{ content }}</div>
  </div>
</template>

<script setup>
const props = defineProps({
  content: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.plain-text-renderer {
  width: 100%;
}

.plain-text-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-family);
  color: var(--text-color);
  line-height: 1.6;
  font-size: 1rem;
  padding-top: 0.8rem;
  padding-bottom: 0.8rem;
}
</style>
