import type { ModelCreateForm, ModelParameters } from '@/types/models'

// 参数描述
export const PARAMETER_DESCRIPTIONS = {
  temperature: '控制输出的随机性，值越高输出越随机',
  numCtx: '模型能记住的最大token数量',
  topK: '从概率最高的K个token中采样',
  topP: '控制采样时的累积概率阈值',
  repeatPenalty: '控制模型避免重复输出的程度',
  mirostat: 'Mirostat采样控制（0=禁用，1=Mirostat，2=Mirostat 2.0）',
  mirostatEta: 'Mirostat学习率',
  mirostatTau: 'Mirostat目标熵',
} as const;

// 参数默认值
export const DEFAULT_PARAMETERS: ModelParameters = {
  temperature: 0.7,
  numCtx: 4096,
  topK: 40,
  topP: 0.9,
  repeatLastN: 64,
  repeatPenalty: 1.1,
  mirostat: 0,
  mirostatEta: 0.1,
  mirostatTau: 5.0,
};

// 参数验证规则
export const PARAMETER_RULES = {
  temperature: { min: 0, max: 2 },
  numCtx: { min: 1024, max: 8192 },
  topK: { min: 0, max: 100 },
  topP: { min: 0, max: 1 },
  repeatLastN: { min: 0, max: 1024 },
  repeatPenalty: { min: 1, max: 2 },
  mirostat: { min: 0, max: 2 },
  mirostatEta: { min: 0.01, max: 1 },
  mirostatTau: { min: 0.1, max: 10 },
};

// 转换参数名称为modelfile格式
const convertParamName = (name: string): string => {
  // 先转换为下划线格式，再转为小写
  return name.replace(/([A-Z])/g, '_$1').toLowerCase();
};

// 验证单个参数
const validateParameter = (name: string, value: number): string | null => {
  const rule = PARAMETER_RULES[name as keyof typeof PARAMETER_RULES];
  if (!rule) return null;
  
  if (value < rule.min || value > rule.max) {
    return `${name} 必须在 ${rule.min} 和 ${rule.max} 之间`;
  }
  return null;
};

// 验证表单
export const validateModelConfig = (form: ModelCreateForm): Record<string, string> => {
  const errors: Record<string, string> = {};
  
  // 基础信息验证
  if (!form.name?.trim()) {
    errors.name = '请输入模型名称';
  } else if (form.name.length > 50) {
    errors.name = '模型名称不能超过50个字符';
  }
  
  if (!form.baseModel) {
    errors.baseModel = '请选择基础模型';
  }
  
  // 系统提示词是可选的
  if (form.systemPrompt?.trim() && form.systemPrompt.length > 10000) {
    errors.systemPrompt = '系统提示词不能超过10000个字符';
  }
  
  // 参数验证
  Object.entries(form.parameters).forEach(([key, value]) => {
    const error = validateParameter(key, value);
    if (error) {
      errors[key] = error;
    }
  });
  
  return errors;
};

// 转换为modelfile格式
export function convertToModelfile(form: ModelCreateForm | (Omit<ModelCreateForm, 'baseModel'> & { file: File })): string {
  const lines: string[] = [];
  
  // 处理 FROM 指令
  if ('file' in form) {
    lines.push(`FROM ${form.file.name}`);
  } else if (form.baseModel) {
    lines.push(`FROM ${form.baseModel}`);
  }
  
  // 系统提示词（放在参数前面）
  if (form.systemPrompt?.trim()) {
    let processedPrompt = form.systemPrompt.trim()
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .join('\n');
    
    lines.push('SYSTEM """');
    lines.push(processedPrompt);
    lines.push('"""');
  }
  
  // 处理参数
  if (form.parameters) {
    Object.entries(form.parameters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        // 转换参数名称为小写
        const paramName = convertParamName(key);
        lines.push(`parameter ${paramName} ${value}`);
      }
    });
  }
  
  // 许可证（放在最后）
  if (form.license?.trim()) {
    let processedLicense = form.license.trim()
      .split('\n')
      .map(line => line.trim())
      .join('\n');
    
    lines.push('LICENSE """');
    lines.push(processedLicense);
    lines.push('"""');
  }
  
  return lines.join('\n');
};

// 获取模型的Logo图标
export function getModelLogo(modelName: string): string {
  // 根据模型名称返回对应的logo
  if (modelName.toLowerCase().includes('llama')) {
    return '/images/llama-logo.png'
  } else if (modelName.toLowerCase().includes('mistral')) {
    return '/images/mistral-logo.png'
  } else if (modelName.toLowerCase().includes('codellama')) {
    return '/images/codellama-logo.png'
  } else if (modelName.toLowerCase().includes('gemma')) {
    return '/images/gemma-logo.png'
  } else {
    return '/images/default-model-logo.png'
  }
}
