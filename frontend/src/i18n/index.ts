import { createI18n } from 'vue-i18n';
import { useStorage } from '@vueuse/core';
import zhCN from './locales/zh-CN';
import enUS from './locales/en-US';
import { getLanguageSettings, updateLanguageSettings } from '@/api/languageApi';
import type { Messages } from './types';
import { watch } from 'vue';

// 定义支持的语言类型
export type SupportedLocale = 'zh-CN' | 'en-US';

// 支持的语言
export const SUPPORTED_LANGUAGES = [
  { code: 'zh-CN' as SupportedLocale, name: '中文' },
  { code: 'en-US' as SupportedLocale, name: 'English' }
];

// 定义 i18n 实例类型
export type MessageSchema = {
  [key in SupportedLocale]: Messages
};

// 默认语言
export const DEFAULT_LANGUAGE: SupportedLocale = 'zh-CN';

// 创建 i18n 实例
const i18n = createI18n<false>({
  legacy: false, // 使用组合式 API
  locale: DEFAULT_LANGUAGE,
  fallbackLocale: DEFAULT_LANGUAGE,
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  },
  // 处理未找到的翻译，返回键名
  missing: (locale, key) => {
    console.warn(`[i18n] 未找到翻译: ${key} (${locale})`);
    return key;
  }
});

// 获取类型化的全局实例
const typedI18n = i18n.global;

// 当前语言
const currentLanguage = useStorage<SupportedLocale>('kun-lab-language', DEFAULT_LANGUAGE);

// 提供简便的翻译函数
const t = (key: string, options?: any): string => {
  return typedI18n.t(key, options) as string;
};

// 检查是否为支持的语言
const isSupportedLocale = (locale: string): locale is SupportedLocale => {
  return SUPPORTED_LANGUAGES.some(lang => lang.code === locale);
};

// 切换语言
const setLanguage = async (lang: string): Promise<boolean> => {
  if (!isSupportedLocale(lang)) {
    console.warn(`不支持的语言: ${lang}`);
    return false;
  }

  if (typedI18n.availableLocales.includes(lang)) {
    try {
      console.log(`开始切换语言到: ${lang}`);
      
      // 更新 i18n 实例
      typedI18n.locale.value = lang;
      
      // 同步更新 currentLanguage
      currentLanguage.value = lang;
      
      // 尝试保存到后端
      try {
        console.log(`正在将语言设置 ${lang} 保存到后端...`);
        const result = await updateLanguageSettings(lang);
        if (result) {
          console.log(`语言设置已成功保存到后端: ${lang}`);
        } else {
          console.warn(`保存语言设置到后端失败: ${lang}`);
        }
      } catch (error) {
        console.warn('后端服务不可用，无法保存语言设置:', error);
      }
      
      // 更新文档标题
      updateDocumentTitle();
      
      return true;
    } catch (error) {
      console.error('切换语言失败:', error);
    }
  }
  return false;
};

// 更新文档标题
const updateDocumentTitle = () => {
  const appName = 'kun-lab';
  const title = typedI18n.locale.value === 'zh-CN' 
    ? `${appName} - 本地AI对话助手` 
    : `${appName} - Local AI Assistant`;
  document.title = title;
};

// 从后端获取语言设置
const fetchLanguageSettings = async (): Promise<void> => {
  try {
    console.log('正在从后端获取语言设置...');
    const data = await getLanguageSettings();
    console.log('后端返回的语言设置:', data);
    
    // 如果后端有有效的语言设置，则使用它
    if (data && data.language && isSupportedLocale(data.language) && typedI18n.availableLocales.includes(data.language)) {
      console.log(`使用后端返回的语言设置: ${data.language}`);
      typedI18n.locale.value = data.language;
      currentLanguage.value = data.language; // 同步更新 currentLanguage
      updateDocumentTitle();
    } else {
      // 否则使用默认语言
      console.log(`后端未返回有效的语言设置，使用默认语言: ${DEFAULT_LANGUAGE}`);
      typedI18n.locale.value = DEFAULT_LANGUAGE;
      currentLanguage.value = DEFAULT_LANGUAGE; // 同步更新 currentLanguage
      updateDocumentTitle();
      
      // 尝试将默认语言保存到后端
      try {
        await updateLanguageSettings(DEFAULT_LANGUAGE);
        console.log(`已将默认语言 ${DEFAULT_LANGUAGE} 保存到后端`);
      } catch (error) {
        console.warn('保存默认语言到后端失败:', error);
      }
    }
  } catch (error) {
    console.warn('获取语言设置失败，使用默认语言:', error);
    typedI18n.locale.value = DEFAULT_LANGUAGE;
    currentLanguage.value = DEFAULT_LANGUAGE; // 同步更新 currentLanguage
    updateDocumentTitle();
  }
};

// 动态加载语言包
const loadLanguage = async (lang: string): Promise<boolean> => {
  if (!isSupportedLocale(lang)) {
    console.warn(`不支持的语言: ${lang}`);
    return false;
  }

  if (!typedI18n.availableLocales.includes(lang)) {
    try {
      const module = await import(`./locales/${lang}.ts`);
      typedI18n.setLocaleMessage(lang as any, module.default);
      return true;
    } catch (e) {
      console.error(`无法加载语言包: ${lang}`, e);
      return false;
    }
  }
  return true;
};

// 初始化时更新文档标题
updateDocumentTitle();

// 监听语言变化，更新文档标题
watch(() => typedI18n.locale.value, (newLang: string) => {
  console.log(`语言已变更为: ${newLang}`);
  updateDocumentTitle();
  
  // 确保 currentLanguage 与 typedI18n.locale.value 同步
  if (newLang !== currentLanguage.value) {
    console.log(`同步 currentLanguage (${currentLanguage.value}) 到 typedI18n.locale (${newLang})`);
    currentLanguage.value = newLang as SupportedLocale;
  }
});

// 监听 currentLanguage 变化，确保与 typedI18n.locale.value 同步
watch(() => currentLanguage.value, (newLang: SupportedLocale) => {
  if (newLang !== typedI18n.locale.value) {
    console.log(`同步 typedI18n.locale (${typedI18n.locale.value}) 到 currentLanguage (${newLang})`);
    typedI18n.locale.value = newLang;
  }
});

export { i18n, typedI18n, currentLanguage, t, setLanguage, fetchLanguageSettings, loadLanguage };

// 导出 useLocalization 组合式函数
export { useLocalization } from './composables';
