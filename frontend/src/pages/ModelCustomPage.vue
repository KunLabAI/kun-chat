<template>
  <MainLayout>
    <div class="model-create">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="main-title">{{ t('model.custom_page.title') }}</h1>
            <p class="sub-title">{{ t('model.custom_page.subtitle') }}</p>
          </div>
          <div class="header-actions">
            <Button variant="link" size="md" @click="router.push('/models')">
              {{ t('model.custom_page.back') }}
            </Button>
            <Button
              variant="secondary"
              size="md"
              @click="handleReset"
              :disabled="isSubmitting"
            >
              {{ t('model.custom_page.reset') }}
            </Button>
            <Button 
              variant="primary" 
              size="md" 
              @click="handleSubmit" 
              :loading="isSubmitting"
              :disabled="isSubmitting"
            >
              {{ t('model.custom_page.create') }}
            </Button>
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="main-content">
        <!-- 页签导航 -->
        <div class="account-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.key"
            class="account-tab-item"
            :class="{ 'account-tab-item-active': currentTab === tab.key }"
            @click="currentTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 页签内容 -->
        <div class="tab-content">
          <!-- 基础信息 -->
          <div v-show="currentTab === 'basic'" class="tab-pane">
            <div class="form-group">
              <label class="form-label" for="modelName">
                {{ t('model.custom_page.form.name.label') }}
                <span class="required">*</span>
              </label>
              <input
                id="modelName"
                v-model="form.name"
                type="text"
                class="form-input"
                :class="{ error: errors.name }"
                :placeholder="t('model.custom_page.form.name.placeholder')"
                required
              />
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label class="form-label" for="baseModel">
                {{ t('model.custom_page.form.base_model.label') }}
                <span class="required">*</span>
              </label>
              <div class="model-selector">
                <button 
                  type="button"
                  class="model-select-button"
                  @click.stop="toggleBaseModelSelect($event)"
                  :class="{ 'active': showBaseModelSelect }"
                >
                  <span>{{ getModelDisplayName(form.baseModel) || t('model.custom_page.form.base_model.placeholder') }}</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="chevron-icon">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </button>
                <Transition name="fade">
                  <div v-if="showBaseModelSelect" class="model-dropdown">
                    <div 
                      v-for="model in modelsStore.models" 
                      :key="model.name"
                      class="model-item"
                      @click.stop="selectBaseModel(model.name)"
                      :class="{ 'active': form.baseModel === model.name }"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                        <polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
                        <polyline points="7.5 19.79 7.5 14.6 3 12"/>
                        <polyline points="21 12 16.5 14.6 16.5 19.79"/>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                        <line x1="12" y1="22.08" x2="12" y2="12"/>
                      </svg>
                      <span>{{ model.display_name || model.name }}</span>
                    </div>
                  </div>
                </Transition>
              </div>
              <span v-if="errors.baseModel" class="error-text">{{ errors.baseModel }}</span>
            </div>

            <div class="form-group">
              <label class="form-label" for="promptTemplate">
                {{ t('model.custom_page.form.prompt_template.label') }}
              </label>
              <div class="model-selector">
                <button 
                  type="button"
                  class="model-select-button"
                  @click.stop="togglePromptSelect($event)"
                  :class="{ 'active': showPromptSelect }"
                >
                  <span>{{ selectedPrompt ? selectedPrompt.title : t('model.custom_page.form.prompt_template.placeholder') }}</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="chevron-icon">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </button>
                <Transition name="fade">
                  <div v-if="showPromptSelect" class="model-dropdown">
                    <div 
                      v-for="prompt in prompts" 
                      :key="prompt.id"
                      class="model-item"
                      @click.stop="selectPrompt(prompt)"
                      :class="{ 'active': selectedPrompt && selectedPrompt.id === prompt.id }"
                    >
                      <span>{{ prompt.title }}</span>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="systemPrompt">{{ t('model.custom_page.form.system_prompt.label') }}</label>
              <div class="code-block system-prompt-tab">
                <div class="code-header">
                  <span class="token-count">{{ t('model.custom_page.form.system_prompt.token_count') }}: {{ tokenCount }}</span>
                  <div class="header-right">
                    <button class="icon-button clear-button" @click="clearSystemPrompt" :title="t('model.custom_page.form.system_prompt.clear')">
                      <img src="@/assets/icons/model_delete.svg" alt="clear" />
                    </button>
                    <button class="icon-button copy-button" @click="copySystemPrompt" :title="t('model.custom_page.form.system_prompt.copy')">
                      <img src="@/assets/icons/chat_copy.svg" alt="copy" />
                    </button>
                  </div>
                </div>
                <textarea
                  id="systemPrompt"
                  v-model="form.systemPrompt"
                  class="form-textarea system-prompt"
                  :class="{ error: errors.systemPrompt }"
                  rows="4"
                  :placeholder="t('model.custom_page.form.system_prompt.placeholder')"
                ></textarea>
              </div>
              <span v-if="errors.systemPrompt" class="error-text">{{ errors.systemPrompt }}</span>
            </div>
          </div>

          <!-- 模型参数 -->
          <div v-show="currentTab === 'parameters'" class="tab-pane">
            <!-- 核心参数组 -->
            <div class="parameter-group">
              <div class="group-header">
                <h3>{{ t('model.custom_page.form.parameters.core.title') }}</h3>
                <p class="group-description">{{ t('model.custom_page.form.parameters.core.description') }}</p>
              </div>
              <div class="group-content">
                <!-- Temperature -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="temperature" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.core.temperature.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.core.temperature.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <input
                        type="number"
                        v-model.number="form.parameters.temperature"
                        class="value-input"
                        step="0.1"
                        min="0"
                        max="2"
                        @input="validateParameterInput('temperature', 0, 2)"
                      />
                    </div>
                  </div>
                  <div class="parameter-input">
                    <input
                      id="temperature"
                      v-model.number="form.parameters.temperature"
                      type="range"
                      class="parameter-slider"
                      :min="0"
                      :max="2"
                      :step="0.1"
                    />
                    <div class="parameter-range">
                      <span class="range-min">0</span>
                      <span class="range-max">2</span>
                    </div>
                  </div>
                </div>

                <!-- Context Window -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="numCtx" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.core.context_window.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.core.context_window.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <input
                        type="number"
                        v-model.number="form.parameters.numCtx"
                        class="value-input"
                        step="1024"
                        min="1024"
                        max="8192"
                        @input="validateParameterInput('numCtx', 1024, 8192)"
                      />
                    </div>
                  </div>
                  <div class="parameter-input">
                    <input
                      id="numCtx"
                      v-model.number="form.parameters.numCtx"
                      type="range"
                      class="parameter-slider"
                      :min="1024"
                      :max="8192"
                      :step="1024"
                    />
                    <div class="parameter-range">
                      <span class="range-min">1024</span>
                      <span class="range-max">8192</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 采样参数组 -->
            <div class="parameter-group">
              <div class="group-header">
                <h3>{{ t('model.custom_page.form.parameters.sampling.title') }}</h3>
                <p class="group-description">{{ t('model.custom_page.form.parameters.sampling.description') }}</p>
              </div>
              <div class="group-content">
                <!-- Top P -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="topP" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.sampling.top_p.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.sampling.top_p.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <input
                        type="number"
                        v-model.number="form.parameters.topP"
                        class="value-input"
                        step="0.05"
                        min="0"
                        max="1"
                        @input="validateParameterInput('topP', 0, 1)"
                      />
                    </div>
                  </div>
                  <div class="parameter-input">
                    <input
                      id="topP"
                      v-model.number="form.parameters.topP"
                      type="range"
                      class="parameter-slider"
                      :min="0"
                      :max="1"
                      :step="0.05"
                    />
                    <div class="parameter-range">
                      <span class="range-min">0</span>
                      <span class="range-max">1</span>
                    </div>
                  </div>
                </div>

                <!-- Top K -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="topK" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.sampling.top_k.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.sampling.top_k.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <input
                        type="number"
                        v-model.number="form.parameters.topK"
                        class="value-input"
                        step="1"
                        min="0"
                        max="100"
                        @input="validateParameterInput('topK', 0, 100)"
                      />
                    </div>
                  </div>
                  <div class="parameter-input">
                    <input
                      id="topK"
                      v-model.number="form.parameters.topK"
                      type="range"
                      class="parameter-slider"
                      :min="0"
                      :max="100"
                      :step="1"
                    />
                    <div class="parameter-range">
                      <span class="range-min">0</span>
                      <span class="range-max">100</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 高级参数组 -->
            <div class="parameter-group">
              <div class="group-header">
                <h3>{{ t('model.custom_page.form.parameters.advanced.title') }}</h3>
                <p class="group-description">{{ t('model.custom_page.form.parameters.advanced.description') }}</p>
              </div>
              <div class="group-content">
                <!-- Repeat Penalty -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="repeatPenalty" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.advanced.repeat_penalty.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.advanced.repeat_penalty.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <input
                        type="number"
                        v-model.number="form.parameters.repeatPenalty"
                        class="value-input"
                        step="0.1"
                        min="1"
                        max="2"
                        @input="validateParameterInput('repeatPenalty', 1, 2)"
                      />
                    </div>
                  </div>
                  <div class="parameter-input">
                    <input
                      id="repeatPenalty"
                      v-model.number="form.parameters.repeatPenalty"
                      type="range"
                      class="parameter-slider"
                      :min="1"
                      :max="2"
                      :step="0.1"
                    />
                    <div class="parameter-range">
                      <span class="range-min">1</span>
                      <span class="range-max">2</span>
                    </div>
                  </div>
                </div>

                <!-- Repeat Last N -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="repeatLastN" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.advanced.repeat_last_n.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.advanced.repeat_last_n.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <input
                        type="number"
                        v-model.number="form.parameters.repeatLastN"
                        class="value-input"
                        step="64"
                        min="0"
                        max="1024"
                        @input="validateParameterInput('repeatLastN', 0, 1024)"
                      />
                    </div>
                  </div>
                  <div class="parameter-input">
                    <input
                      id="repeatLastN"
                      v-model.number="form.parameters.repeatLastN"
                      type="range"
                      class="parameter-slider"
                      :min="0"
                      :max="1024"
                      :step="64"
                    />
                    <div class="parameter-range">
                      <span class="range-min">0</span>
                      <span class="range-max">1024</span>
                    </div>
                  </div>
                </div>

                <!-- Mirostat Mode -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="mirostat" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.advanced.mirostat.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.advanced.mirostat.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <select
                        id="mirostat"
                        v-model.number="form.parameters.mirostat"
                        class="form-select"
                      >
                        <option value="0">{{ t('model.custom_page.form.parameters.advanced.mirostat.modes.disabled') }}</option>
                        <option value="1">{{ t('model.custom_page.form.parameters.advanced.mirostat.modes.v1') }}</option>
                        <option value="2">{{ t('model.custom_page.form.parameters.advanced.mirostat.modes.v2') }}</option>
                      </select>
                    </div>
                  </div>
                </div>

                <!-- Mirostat Eta -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="mirostatEta" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.advanced.mirostat_eta.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.advanced.mirostat_eta.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <input
                        type="number"
                        v-model.number="form.parameters.mirostatEta"
                        class="value-input"
                        step="0.01"
                        min="0.01"
                        max="1"
                        @input="validateParameterInput('mirostatEta', 0.01, 1)"
                      />
                    </div>
                  </div>
                  <div class="parameter-input">
                    <input
                      id="mirostatEta"
                      v-model.number="form.parameters.mirostatEta"
                      type="range"
                      class="parameter-slider"
                      :min="0.01"
                      :max="1"
                      :step="0.01"
                    />
                    <div class="parameter-range">
                      <span class="range-min">0.01</span>
                      <span class="range-max">1</span>
                    </div>
                  </div>
                </div>

                <!-- Mirostat Tau -->
                <div class="parameter-item">
                  <div class="parameter-header">
                    <label for="mirostatTau" class="parameter-label">
                      {{ t('model.custom_page.form.parameters.advanced.mirostat_tau.label') }}
                      <span class="tooltip" :data-tooltip="t('model.custom_page.form.parameters.advanced.mirostat_tau.tooltip')">?</span>
                    </label>
                    <div class="parameter-value">
                      <input
                        type="number"
                        v-model.number="form.parameters.mirostatTau"
                        class="value-input"
                        step="0.1"
                        min="0.1"
                        max="10"
                        @input="validateParameterInput('mirostatTau', 0.1, 10)"
                      />
                    </div>
                  </div>
                  <div class="parameter-input">
                    <input
                      id="mirostatTau"
                      v-model.number="form.parameters.mirostatTau"
                      type="range"
                      class="parameter-slider"
                      :min="0.1"
                      :max="10"
                      :step="0.1"
                    />
                    <div class="parameter-range">
                      <span class="range-min">0.1</span>
                      <span class="range-max">10</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 许可证 -->
          <div v-show="currentTab === 'license'" class="tab-pane">
            <div class="form-group">
              <label class="form-label" for="license">{{ t('model.custom_page.form.license.label') }}</label>
              <div class="code-block license-tab">
                <div class="code-header">
                  <span class="token-count">{{ t('model.custom_page.form.license.token_count') }}: {{ licenseTokenCount }}</span>
                  <div class="header-right">
                    <button class="icon-button clear-button" @click="clearLicense" :title="t('model.custom_page.form.license.clear')">
                      <img src="@/assets/icons/model_delete.svg" alt="clear" />
                    </button>
                    <button class="icon-button copy-button" @click="copyLicense" :title="t('model.custom_page.form.license.copy')">
                      <img src="@/assets/icons/chat_copy.svg" alt="copy" />
                    </button>
                  </div>
                </div>
                <textarea
                  id="license"
                  v-model="form.license"
                  class="form-textarea license"
                  rows="8"
                  :placeholder="t('model.custom_page.form.license.placeholder')"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <Dialog
      v-model="showOverwriteDialog"
      :title="t('model.custom_page.overwrite_dialog.title')"
      :confirm-text="t('model.custom_page.overwrite_dialog.confirm')"
      :cancel-text="t('model.custom_page.overwrite_dialog.cancel')"
      @confirm="handleOverwriteConfirm"
    >
      <p>{{ t('model.custom_page.overwrite_dialog.message') }}</p>
    </Dialog>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import { useModelsStore } from '@/stores/models'
import { usePromptStore } from '@/stores/promptStore'
import { useLocalization } from '@/i18n'
import MainLayout from '@/layouts/MainLayout.vue'
import Button from '@/components/common/Button.vue'
import Dialog from '@/components/common/Dialog.vue'
import { modelApi, ModelApiError } from '@/api/models'
import { convertToModelfile, validateModelConfig } from '@/utils/modelUtils'

const router = useRouter()
const notificationStore = useNotificationStore()
const modelsStore = useModelsStore()
const promptStore = usePromptStore()
const { t } = useLocalization()

// 页签配置
const tabs = [
  { key: 'basic', label: t('model.custom_page.tabs.basic'), required: true },
  { key: 'parameters', label: t('model.custom_page.tabs.parameters'), required: false },
  { key: 'license', label: t('model.custom_page.tabs.license'), required: false }
]
const currentTab = ref('basic')

// 表单数据
const form = reactive({
  name: '',
  baseModel: '',
  systemPrompt: '',
  license: '',
  parameters: {
    temperature: 0.8,
    topP: 0.9,
    topK: 40,
    numCtx: 4096,
    repeatLastN: 64,
    repeatPenalty: 1.1,
    presencePenalty: 0,
    frequencyPenalty: 0,
    mirostat: 0,
    mirostatTau: 5,
    mirostatEta: 0.1,
    seed: -1,
    stop: []
  }
})

// 错误信息
const errors = reactive({
  name: '',
  baseModel: '',
  systemPrompt: ''
})

// 提交状态
const isSubmitting = ref(false)
const showOverwriteDialog = ref(false)

// 系统提示词的token计数
const tokenCount = computed(() => {
  // 简单估算，实际应该使用tokenizer计算
  return form.systemPrompt ? Math.round(form.systemPrompt.length / 3) : 0
})

// 计算许可证token数量
const licenseTokenCount = computed(() => {
  // 简单估算，实际应该使用tokenizer计算
  return form.license ? Math.round(form.license.length / 3) : 0
})

// 对话框相关状态
interface ModelData {
  name: string;
  baseModel: string;
  systemPrompt: string;
  parameters: {
    temperature: number;
    numCtx: number;
    topK: number;
    topP: number;
    repeatLastN: number;
    repeatPenalty: number;
    presencePenalty: number;
    frequencyPenalty: number;
    mirostat: number;
    mirostatEta: number;
    mirostatTau: number;
    seed: number;
    stop: string[];
  };
  license: string;
}

const pendingModelData = ref<ModelData | null>(null)

// 本地存储的key
const STORAGE_KEY = 'model_custom_form_data'

// 保存表单数据到localStorage
const saveFormData = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    ...form,
    parameters: { ...form.parameters }
  }))
}

// 从localStorage加载表单数据
const loadFormData = () => {
  const savedData = localStorage.getItem(STORAGE_KEY)
  if (savedData) {
    const parsedData = JSON.parse(savedData)
    Object.assign(form, parsedData)
  }
}

// 重置表单数据
const handleReset = () => {
  form.name = ''
  form.baseModel = ''
  form.systemPrompt = ''
  form.license = ''
  form.parameters = { 
    temperature: 0.8,
    topP: 0.9,
    topK: 40,
    numCtx: 4096,
    repeatLastN: 64,
    repeatPenalty: 1.1,
    presencePenalty: 0,
    frequencyPenalty: 0,
    mirostat: 0,
    mirostatTau: 5,
    mirostatEta: 0.1,
    seed: -1,
    stop: []
  }
  localStorage.removeItem(STORAGE_KEY)
  notificationStore.success(t('model.custom_page.notifications.reset_success'))
}

// 监听表单变化并自动保存
watch(
  [
    () => form.name,
    () => form.baseModel,
    () => form.systemPrompt,
    () => form.parameters,
    () => form.license
  ],
  () => {
    saveFormData()
  },
  { deep: true }
)

// 验证参数输入
const validateParameterInput = (paramName: keyof typeof form.parameters, min: number, max: number) => {
  // 确保只处理数字类型的参数
  if (paramName === 'stop') {
    return; // 跳过非数字类型参数
  }
  
  const value = form.parameters[paramName];
  if (typeof value === 'number') {
    if (value < min) {
      form.parameters[paramName] = min;
    } else if (value > max) {
      form.parameters[paramName] = max;
    }
  }
}

// 获取提示词列表
const { prompts } = storeToRefs(promptStore)
const selectedPrompt = ref<any>("")

// 监听选中的提示词变化
watch(selectedPrompt, (newPrompt) => {
  if (newPrompt) {
    form.systemPrompt = newPrompt.content
  }
})

// 创建模型的具体逻辑
const createModel = async (force: boolean = false) => {
  isSubmitting.value = true
  try {
    const modelfile = convertToModelfile({
      name: form.name,
      baseModel: form.baseModel,
      systemPrompt: form.systemPrompt,
      parameters: {
        temperature: form.parameters.temperature,
        numCtx: form.parameters.numCtx,
        topK: form.parameters.topK,
        topP: form.parameters.topP,
        repeatLastN: form.parameters.repeatLastN,
        repeatPenalty: form.parameters.repeatPenalty,
        mirostat: form.parameters.mirostat,
        mirostatEta: form.parameters.mirostatEta,
        mirostatTau: form.parameters.mirostatTau
      },
      license: form.license
    })

    await modelsStore.createModel({
      name: form.name,
      modelfile,
      parameters: {
        temperature: form.parameters.temperature,
        numCtx: form.parameters.numCtx,
        topK: form.parameters.topK,
        topP: form.parameters.topP,
        repeatLastN: form.parameters.repeatLastN,
        repeatPenalty: form.parameters.repeatPenalty,
        mirostat: form.parameters.mirostat,
        mirostatEta: form.parameters.mirostatEta,
        mirostatTau: form.parameters.mirostatTau
      },
      force
    })

    notificationStore.success(t('model.custom_page.notifications.create_success'))
    router.push('/models')
  } catch (error: unknown) {
    // 处理不同类型的错误
    if (error instanceof ModelApiError) {
      // 处理API错误
      if (error.status === 409) {
        // 模型名称冲突，显示覆盖确认对话框
        pendingModelData.value = { ...form }
        showOverwriteDialog.value = true
        return
      } else {
        // 其他API错误
        notificationStore.error(t('model.custom_page.notifications.create_error') + ': ' + error.message)
      }
    } else if (error instanceof Error) {
      // 一般JavaScript错误
      notificationStore.error(t('model.custom_page.notifications.create_error') + ': ' + error.message)
    } else {
      // 未知错误
      notificationStore.error(t('model.custom_page.notifications.create_error_retry'))
    }
  } finally {
    isSubmitting.value = false
  }
}

// 验证表单
function validateForm(): boolean {
  const validationErrors = validateModelConfig(form)
  
  Object.assign(errors, validationErrors)
  
  return Object.keys(validationErrors).length === 0
}

// 提交表单
const handleSubmit = async () => {
  if (!validateForm()) return
  await createModel(false)
}

// 确认覆盖已有模型
const handleOverwriteConfirm = async () => {
  showOverwriteDialog.value = false
  if (pendingModelData.value) {
    await createModel(true)
    pendingModelData.value = null
  }
}

// 复制系统提示词
const copySystemPrompt = async () => {
  try {
    await navigator.clipboard.writeText(form.systemPrompt)
    const button = document.querySelector('.system-prompt-tab .copy-button') as HTMLElement;
    if (button) {
      button.style.backgroundColor = 'var(--success-bg)'
      
      setTimeout(() => {
        button.style.backgroundColor = ''
      }, 2000)
    }
    notificationStore.success(t('model.custom_page.form.system_prompt.copied'))
  } catch (err) {
    console.error('Failed to copy system prompt:', err)
  }
}

// 清空系统提示词
const clearSystemPrompt = () => {
  form.systemPrompt = ''
  notificationStore.info(t('model.custom_page.form.system_prompt.cleared'))
}

// 复制许可证内容
const copyLicense = async () => {
  try {
    await navigator.clipboard.writeText(form.license)
    const button = document.querySelector('.license-tab .copy-button') as HTMLElement
    if (button) {
      button.style.backgroundColor = 'var(--success-bg)'
      
      setTimeout(() => {
        button.style.backgroundColor = ''
      }, 2000)
    }
    notificationStore.success(t('model.custom_page.form.license.copied'))
  } catch (err) {
    console.error('Failed to copy license:', err)
  }
}

// 清空许可证内容
const clearLicense = () => {
  form.license = ''
  notificationStore.info(t('model.custom_page.form.license.cleared'))
}

// 在组件挂载时获取模型列表和提示词列表
onMounted(async () => {
  try {
    await Promise.all([
      modelsStore.fetchModels(),
      promptStore.loadPrompts()
    ])
    loadFormData()
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
    
  // 添加全局点击事件监听，用于关闭下拉选择栏
  document.addEventListener('click', handleOutsideClick)
  // 添加全局键盘事件监听，用于ESC键关闭下拉选择栏
  document.addEventListener('keydown', handleKeyDown)
})

// 组件卸载前移除事件监听
onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  document.removeEventListener('keydown', handleKeyDown)
})


// 处理点击外部区域关闭下拉选择栏
// 处理点击外部区域关闭下拉选择栏
const handleOutsideClick = (event: MouseEvent) => {
  // 获取点击的元素
  const target = event.target as HTMLElement
  
  // 检查点击是否在任何选择器内部
  const isClickInsideAnySelector = !!target.closest('.model-selector')
  
  // 如果点击在所有选择器外部，则关闭所有下拉菜单
  if (!isClickInsideAnySelector) {
    showBaseModelSelect.value = false
    showPromptSelect.value = false
  }
}

// 处理ESC键关闭下拉选择栏
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    // 如果有任何下拉选择栏打开，则关闭它们
    if (showBaseModelSelect.value || showPromptSelect.value) {
      showBaseModelSelect.value = false
      showPromptSelect.value = false
    }
  }
}

// 模型选择相关状态
const showBaseModelSelect = ref(false)
const showPromptSelect = ref(false)

// 切换模型选择弹出层
const toggleBaseModelSelect = (event: Event) => {
  event.stopPropagation()
  showBaseModelSelect.value = !showBaseModelSelect.value
  // 如果打开了基础模型选择器，关闭提示词选择器
  if (showBaseModelSelect.value) {
    showPromptSelect.value = false
  }
}

// 切换提示词选择弹出层
const togglePromptSelect = (event: Event) => {
  event.stopPropagation()
  showPromptSelect.value = !showPromptSelect.value
  // 如果打开了提示词选择器，关闭基础模型选择器
  if (showPromptSelect.value) {
    showBaseModelSelect.value = false
  }
}

// 选择模型
const selectBaseModel = (modelName: string) => {
  // 先设置模型名称，再关闭下拉菜单
  form.baseModel = modelName
  // 使用 setTimeout 延迟关闭下拉菜单，确保选择操作先完成
  setTimeout(() => {
    showBaseModelSelect.value = false
  }, 10)
}

// 选择提示词
const selectPrompt = (prompt: any) => {
  selectedPrompt.value = prompt
  showPromptSelect.value = false
}

// 获取模型显示名称
const getModelDisplayName = (modelName: string) => {
  const model = modelsStore.models.find((model) => model.name === modelName)
  return model ? (model.display_name || model.name) : modelName
}
</script>

<style scoped>
@import '@/styles/ModelCustomPage.css';
</style>
