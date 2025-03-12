/**
 * i18n 组合式函数
 */
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { currentLanguage, setLanguage, loadLanguage, SUPPORTED_LANGUAGES, SupportedLocale, type MessageSchema } from './index';
import type { Messages } from './types';

/**
 * 使用国际化的组合式函数
 * 提供更便捷的方式访问和使用翻译功能
 */
export function useLocalization() {
  const { t, availableLocales } = useI18n<{message: Messages}>();
  
  // 当前语言
  const language = computed<SupportedLocale>({
    get: () => currentLanguage.value,
    set: async (value: SupportedLocale) => {
      await setLanguage(value);
    }
  });
  
  // 格式化带参数的消息
  const formatMessage = (key: string, params: Record<string, any> = {}) => {
    return t(key, params);
  };
  
  // 加载新的语言包
  const loadNewLanguage = async (lang: SupportedLocale) => {
    return await loadLanguage(lang);
  };
  
  // 获取当前可用的语言列表
  const getAvailableLanguages = () => {
    return availableLocales || [];
  };
  
  return {
    t,
    language,
    formatMessage,
    loadNewLanguage,
    getAvailableLanguages,
    supportedLanguages: SUPPORTED_LANGUAGES
  };
}
