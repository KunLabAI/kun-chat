import CohereIcon from '@/assets/modelslogo/Cohere_icon.svg'
import DeepseekIcon from '@/assets/modelslogo/Deepseek_icon.svg'
import DefaultIcon from '@/assets/modelslogo/DefaultIcon.svg'
import GemmaIcon from '@/assets/modelslogo/Gemma_icon.svg'
import LLaVAIcon from '@/assets/modelslogo/LLaVA_icon.svg'
import MetaIcon from '@/assets/modelslogo/Meta_icon.svg'
import MistralIcon from '@/assets/modelslogo/Mistral_icon.svg'
import NvidiaIcon from '@/assets/modelslogo/Nvidia_icon.svg'
import PhiIcon from '@/assets/modelslogo/Phi_icon.svg'
import QwenIcon from '@/assets/modelslogo/Qwen_icon.svg'

// 模型家族到图标的映射
export const modelFamilyLogoMap: Record<string, string> = {
  'cohere': CohereIcon,
  'deepseek': DeepseekIcon,
  'gemma': GemmaIcon,
  'llava': LLaVAIcon,
  'mllama': MetaIcon,  // Meta's LLaMA models
  'mistral': MistralIcon,
  'nvidia': NvidiaIcon,
  'phi': PhiIcon,
  'qwen': QwenIcon
}

/**
 * 获取模型家族对应的logo图标
 * @param family 模型家族名称
 * @returns logo图标的URL
 */
export function getModelLogo(family: string): string {
  if (!family) return DefaultIcon
  
  // 提取基础家族名称（移除版本号等）
  const baseFamilyName = family.toLowerCase().split(/[-_\d.]/)[0]
  
  // 特殊处理 llama 系列
  if (baseFamilyName === 'llama') {
    return MetaIcon
  }
  
  return modelFamilyLogoMap[baseFamilyName] || DefaultIcon
}
