<!-- 语言切换组件 -->
<template>
  <div class="language-switcher">
    <div class="features-toggle-group">
      <button 
        @click="selectLanguage('zh-CN')"
        class="features-toggle-button"
        :class="{ 'features-toggle-button-active': selectedLanguage === 'zh-CN' }"
        :disabled="loading"
      >
        中文
      </button>
      <button 
        @click="selectLanguage('en-US')"
        class="features-toggle-button"
        :class="{ 'features-toggle-button-active': selectedLanguage === 'en-US' }"
        :disabled="loading"
      >
        English
      </button>
    </div>
    <div v-if="loading" class="language-loading">
      <i class="fas fa-spinner fa-spin"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { currentLanguage, setLanguage, SupportedLocale } from '@/i18n/index';
import { useNotificationStore } from '@/stores/notification';
import { useI18n } from 'vue-i18n';

const notificationStore = useNotificationStore();
const { t } = useI18n();

// 当前选择的语言
const selectedLanguage = ref<SupportedLocale>(currentLanguage.value || 'zh-CN');

// 加载状态
const loading = ref(false);

// 确保组件挂载时有正确的语言选择
onMounted(() => {
  console.log('LanguageSwitcher组件挂载，当前语言:', currentLanguage.value);
  
  if (!selectedLanguage.value || !['zh-CN', 'en-US'].includes(selectedLanguage.value)) {
    console.log('当前没有选择语言或选择的语言无效，设置为默认中文');
    selectedLanguage.value = 'zh-CN';
  }
  
  // 确保选择的语言与当前语言一致
  if (currentLanguage.value && selectedLanguage.value !== currentLanguage.value) {
    console.log(`组件语言(${selectedLanguage.value})与全局语言(${currentLanguage.value})不一致，同步为全局语言`);
    selectedLanguage.value = currentLanguage.value;
  }
});

// 监听语言变化
watch(() => currentLanguage.value, (newLang) => {
  console.log('全局语言变化:', newLang);
  if (newLang && ['zh-CN', 'en-US'].includes(newLang)) {
    console.log('同步组件语言为:', newLang);
    selectedLanguage.value = newLang;
  }
});

// 选择语言
const selectLanguage = async (lang: SupportedLocale) => {
  // 如果选择的是当前语言，不做任何操作
  if (lang === selectedLanguage.value) {
    console.log(`语言未变化 (${lang})，不进行切换`);
    return;
  }
  
  console.log(`开始切换语言: ${selectedLanguage.value} -> ${lang}`);
  loading.value = true;
  
  try {
    const success = await setLanguage(lang);
    if (success) {
      const message = lang === 'zh-CN' 
        ? '语言设置已更新为中文' 
        : 'Language has been updated to English';
      notificationStore.success(message);
      console.log('语言切换成功:', lang);
      
      // 确认当前语言是否已更新
      console.log(`切换后检查: currentLanguage=${currentLanguage.value}, selectedLanguage=${selectedLanguage.value}`);
    } else {
      // 如果失败，恢复原来的选择
      console.error('语言切换失败，恢复原语言:', currentLanguage.value);
      selectedLanguage.value = currentLanguage.value || 'zh-CN';
      
      const errorMessage = selectedLanguage.value === 'zh-CN'
        ? '语言切换失败，请稍后再试'
        : 'Failed to change language, please try again later';
      notificationStore.error(errorMessage);
    }
  } catch (error) {
    console.error('语言切换出错:', error);
    selectedLanguage.value = currentLanguage.value || 'zh-CN';
    
    const errorMessage = selectedLanguage.value === 'zh-CN'
      ? '语言切换出错，请稍后再试'
      : 'Error changing language, please try again later';
    notificationStore.error(errorMessage);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@import '@/styles/FeaturesSettings.css';

.language-switcher {
  position: relative;
}

.language-loading {
  position: absolute;
  top: 50%;
  right: -24px;
  transform: translateY(-50%);
  color: var(--primary-600);
}
</style>
