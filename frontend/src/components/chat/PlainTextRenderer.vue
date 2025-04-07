<template>
  <div class="plain-text-renderer">
    <div 
      class="plain-text-content" 
      :class="{ 'collapsed': isCollapsed && shouldCollapse }"
    >
      {{ content }}
    </div>
    <div 
      v-if="shouldCollapse" 
      class="text-toggle-button"
      @click="toggleCollapse"
    >
      <img 
        v-if="isCollapsed" 
        src="@/assets/icons/sys_arrowdown.svg" 
        alt="展开" 
        class="toggle-icon"
      />
      <img 
        v-else 
        src="@/assets/icons/sys_arrowup.svg" 
        alt="收起" 
        class="toggle-icon"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  maxLines: {
    type: Number,
    default: 5
  }
});

const isCollapsed = ref(true);
const lineCount = ref(0);

// 计算是否应该显示折叠/展开按钮
const shouldCollapse = computed(() => {
  return lineCount.value > props.maxLines;
});

// 切换折叠/展开状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

// 计算内容的行数
onMounted(() => {
  // 使用换行符数量加1来估算行数
  const newlineCount = (props.content.match(/\n/g) || []).length;
  lineCount.value = newlineCount + 1;
});
</script>

<style scoped>
.plain-text-renderer {
  width: 100%;
  position: relative;
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

.plain-text-content.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: v-bind('props.maxLines');
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-toggle-button {
  position: absolute;
    width: 32px;
    height: 32px;
    top: 0.65rem;
    right: 0rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0.5;
    transition: opacity 0.2s ease;
    border-radius: 8px;
    z-index: 0;
}

.text-toggle-button:hover {
  opacity: 1;
  background-color: var(--gray-300);
}

.toggle-icon {
  width: 24px;
  height: 24px;
  filter: var(--button-hover-border);
}

.dark .toggle-icon {
  filter: var(--filter-gray-100);
}

.dark .text-toggle-button:hover {
  opacity: 1;
  background-color: var(--gray-500);
}
</style>
