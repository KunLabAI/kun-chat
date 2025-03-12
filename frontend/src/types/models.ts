// src/types/models.ts

// 移除不再使用的ApiResponse接口，因为后端直接返回Model数组
// export interface ApiResponse {
//   models: Model[]
// }

export interface Model {
  id: number
  name: string
  display_name?: string
  family?: string
  parameter_size?: string
  quantization?: string
  format?: string
  size?: number
  digest?: string
  is_custom: boolean
  options?: any
  modified_at?: string
  created_at: string
}

export interface ModelDetails {
  parent_model: string
  format: string
  family: string
  families: string[]
  parameter_size: string
  quantization_level: string
}

export interface ModelInfo extends Model {
  pull_time: string | null
  status: string | null
  last_used_at: string | null
  is_favorited: boolean | null
  advanced_parameters: {
    license: string
    modelfile: string
    parameters: string
    template: string
    details: ModelDetails
    model_info: {
      [key: string]: any
    }
    modified_at: string
  }
}

// 量化级别映射
export const QUANTIZATION_LEVELS: Record<string, QuantizationInfo> = {
  'Q2_K': { bits: 2, description: '2-bit quantization for extreme compression' },
  'Q3_K_S': { bits: 3, description: '3-bit quantization optimized for small models' },
  'Q4_K_M': { bits: 4, description: '4-bit quantization balanced for medium models' },
  'Q5_K_M': { bits: 5, description: '5-bit quantization for higher quality' },
  'Q6_K': { bits: 6, description: '6-bit quantization for near-original quality' },
  'Q8_0': { bits: 8, description: '8-bit quantization with original quality' }
}

export interface QuantizationInfo {
  bits: number
  description: string
}

// 模型下载状态
export type ModelPullStatus = 'WAITING' | 'DOWNLOADING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'

// 模型下载进度事件
export interface ModelPullEvent {
  status: ModelPullStatus
  error?: string
  total_size?: number
  downloaded_size?: number
  details?: {
    status: string
    [key: string]: any
  }
}

// 模型参数接口
export interface ModelParameters {
  temperature: number
  numCtx: number
  topK: number
  topP: number
  repeatLastN: number
  repeatPenalty: number
  mirostat: number
  mirostatEta: number
  mirostatTau: number
}

// 模型创建表单接口
export interface ModelCreateForm {
  name: string
  baseModel: string
  systemPrompt: string
  license?: string
  modelfile?: string
  parameters: ModelParameters
}

export interface ModelCreateRequest {
  name: string
  modelfile: string
  parameters?: ModelParameters
  force?: boolean
}

// 存储状态类型
export interface ModelsState {
  models: Model[]
  selectedModel: Model | null
  loading: boolean
  error: string | null
  pullStatus: { [key: string]: any }
  createModelDialogVisible: boolean
}
