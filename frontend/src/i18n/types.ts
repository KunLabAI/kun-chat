/**
 * 多语言类型定义
 */

// 通用类型
export interface CommonMessages {
  app: {
    name: string;
    description: string;
  };
  locale: string;
  app_name: string;
  loading: string;
  empty_data: string;
  yes: string;
  no: string;
  markdown: {
    copy_code: string;
    copied: string;
    preview_code: string;
    html_preview: string;
    open_in_new_window: string;
    close: string;
    expand_code: string;
    collapse_code: string;
  };
  notification: {
    close: string;
  };
  actions: {
    save: string;
    cancel: string;
    confirm: string;
    delete: string;
    copy:string;
    edit: string;
    add: string;
    test: string;
    search: string;
    refresh: string;
    close: string;
    back: string;
    next: string;
    previous: string;
    submit: string;
    clear: string;
    show: string;
    hide: string;
    learn_more: string;
    update: string;
    create: string;
    finish: string;
    ok: string;
  };
  status: {
    success: string;
    error: string;
    warning: string;
    info: string;
    loading: string;
    enabled: string;
    disabled: string;
  };
  not_available: string;
}

// 设置类型
export interface SettingsMessages {
  title: string;
  subtitle: string;
  tabs: {
    general: string;
    tools: string;
    connection: string;
    network: string;
  };
  features?: {
    title: string;
  };
  account?: {
    title: string;
    subtitle: string;
    tabs: {
      profile: string;
      security: string;
      preferences: string;
    };
    profile: {
      title: string;
      avatar: {
        title: string;
        description: string;
        alt: string;
        success: string;
        error: string;
      };
      username: {
        label: string;
        placeholder: string;
      };
      nickname: {
        label: string;
        placeholder: string;
        success: string;
        error: string;
      };
      email: {
        label: string;
        placeholder: string;
        success: string;
        error: string;
      };
    };
    theme: {
      title: string;
      switch: {
        title: string;
        description: string;
        light: string;
        dark: string;
        system: string;
      };
    };
    security: {
      title: string;
      password: {
        current: {
          label: string;
          placeholder: string;
        };
        new: {
          label: string;
          placeholder: string;
        };
        confirm: {
          label: string;
          placeholder: string;
        };
        success: string;
        error: string;
      };
    };
    preferences: {
      title: string;
      personal_info: {
          placeholder: string;
          description: string;
      };
      use_personal_info: {
          label: string;
          description: string;
      };
      enable_button: string;
      disable_button: string;
      enabled: string;
      disabled: string;
      save_button: string;
      saving: string;
      success: string;
      error: string;
    };
  };
  general: {
    language: {
      title: string;
    };
    theme: {
      title: string;
      options: {
        light: string;
        dark: string;
        system: string;
      };
    };
  };
  tools: {
    tavily: {
      title: string;
      description: string;
      api_key: {
        label: string;
        placeholder: string;
        description: string;
      };
      apiKeyHint: string;
      test_button: string;
      test_success: string;
      test_error: string;
      connecting: string;
      hide_key: string;
      show_key: string;
      delete_key: string;
      domain_format_error: string;
      search_depth: {
        label: string;
        basic: string;
        advanced: string;
        description: string;
      };
      include_domains: {
        label: string;
        description: string;
        placeholder: string;
      };
      exclude_domains: {
        label: string;
        description: string;
        placeholder: string;
      };
      messages: {
        api_key_cleared: string;
        api_key_saved: string;
        search_depth_updated: string;
        include_domains_updated: string;
        exclude_domains_updated: string;
        connection_test_success: string;
        api_key_verified: string;
      };
      errors: {
        clear_api_key_failed: string;
        get_settings_failed: string;
        invalid_api_key: string;
        save_api_key_failed: string;
        update_search_depth_failed: string;
        update_include_domains_failed: string;
        update_exclude_domains_failed: string;
        connection_test_failed: string;
      };
      warnings: {
        domain_exists: string;
        set_api_key_first: string;
      };
    };
  };
  connection: {
    ollama: {
      title: string;
      host: {
        label: string;
        placeholder: string;
        description: string;
      };
      test_success: string;
      test_error: string;
      status: {
        label: string;
        description: string;
        connected: string;
        disconnected: string;
        version: string;
        state: string;
      };
      notification: {
        label: string;
        connected: string;
        disconnected: string;
      };
      auto_check: {
        label: string;
        description: string;
      };
      save_button: string;
      checking: string;
      save_success: string;
      save_failed: string;
      load_failed: string;
    };
  };
}

// 功能页面类型
export interface FeaturesMessages {
  title: string;
  subtitle: string;
}

// 首页消息类型
export interface HomeMessages {
  welcome: string;
  subtitle: string;
  favorite_models: {
    title: string;
    view_more: string;
  };
  onboarding: {
    install_ollama: string;
    pull_models: string;
  };
  new_chat: string;
  delete_model: {
    title: string;
    confirm_message: string;
  };
}

// 历史记录页面消息类型
export interface HistoryMessages {
  title: string;
  subtitle: string;
  loading: string;
  select_all: string;
  delete_selected: string;
  search_placeholder: string;
  retry: string;
  conversation_count: string;
  empty_state: {
    title: string;
    start_chat: string;
  };
  time_groups: {
    today: string;
    yesterday: string;
    three_days: string;
    last_week: string;
    earlier: string;
    date_range: string;
    to: string;
    and_earlier: string;
  };
  date_format: {
    month_day: string;
    year_month_day: string;
    time: string;
    date_time: string;
  };
  conversation: {
    untitled: string;
    no_ai_response: string;
    continue_chat: string;
    image_message: string;
    images_message: string;
    pdf_document: string;
    loading_message: string;
  };
  delete_dialog: {
    title: string;
    confirm_single: string;
    confirm_multiple: string;
    success_single: string;
    success_multiple: string;
    error: string;
  };
}

// 提示词页面消息类型
export interface PromptMessages {
  title: string;
  subtitle: string;
  create_prompt: string;
  edit_prompt: string;
  empty_state: {
    title: string;
    subtitle: string;
  };
  form: {
    title_label: string;
    title_placeholder: string;
    content_label: string;
    content_placeholder: string;
    tags_label: string;
    tags_placeholder: string;
    cancel: string;
    save: string;
    create: string;
  };
  card: {
    created_at: string;
    updated_at: string;
    unknown_time: string;
    copy: string;
    edit: string;
    delete: string;
    use: string;
  };
  delete_dialog: {
    title: string;
    confirm_message: string;
    success: string;
    error: string;
  };
  notifications: {
    copied: string;
    create_success: string;
    create_error: string;
    update_success: string;
    update_error: string;
    delete_success: string;
    delete_error: string;
    load_error: string;
    get_error: string;
  };
}

// 模型页面消息类型
export interface ModelMessages {
  title: string;
  subtitle: string;
  create_model: string;
  custom_model: string;
  pull_model: string;
  empty_state: {
    title: string;
  };
  loading: string;
  delete_dialog: {
    title: string;
    confirm_message: string;
  };
  actions: {
    view_details: string;
    start_chat: string;
    delete: string;
  };
  notifications: {
    delete_success: string;
    delete_error: string;
    create_success: string;
    create_error: string;
    pull_success: string;
    pull_error: string;
    reset_success: string;
  };
  card: {
    parameter_size: string;
    file_size: string;
    modified_time: string;
    unknown: string;
    tooltip: {
      details: string;
      chat: string;
      delete: string;
    };
  };
  detail: {
    back: string;
    favorite: string;
    unfavorite: string;
    favorited: string;
    tabs: {
      basic: string;
      advanced: string;
    };
    sections: {
      basic_info: string;
      modelfile_config: string;
      model_parameters: string;
      template_config: string;
      license: string;
      model_architecture: string;
      attention_params: string;
      tokenizer_params: string;
    };
    actions: {
      expand: string;
      collapse: string;
    };
    system_prompt_title: string;
    info_labels: {
      name: string;
      family: string;
      parameter_size: string;
      quantization: string;
      file_size: string;
      created_at: string;
      modified_at: string;
      format: string;
      system_prompt: string;
      system: string;
    };
    advanced_params: {
      // 架构参数
      architecture_type: string;
      base_model: string;
      organization: string;
      repo_url: string;
      model_name: string;
      parameter_count: string;
      quantization_version: string;
      size_label: string;
      finetune_type: string;
      tags: string;
      
      // 新版架构参数
      context_length: string;
      embedding_length: string;
      feed_forward: string;
      head_count: string;
      kv_head_count: string;
      layer_count: string;
      vocabulary_size: string;
      
      // 注意力参数
      attention_head_count: string;
      kv_head_count_param: string;
      layer_norm_epsilon: string;
      block_count: string;
      context_length_param: string;
      embedding_dimension: string;
      feed_forward_dimension: string;
      rope_freq_base: string;
      
      // 新版注意力参数
      rope_dimension: string;
      sliding_window: string;
      key_length: string;
      value_length: string;
      version: string;
      languages: string;
      
      // 分词器参数
      tokenizer_type: string;
      add_bos_token: string;
      add_eos_token: string;
      bos_token_id: string;
      eos_token_id: string;
      padding_token_id: string;
      prefix: string;
      
      // 新版分词器参数
      type: string;
      model: string;
      tokens: string;
    };
  };
  
  // 添加拉取模型页面相关翻译
  pull_page: {
    title: string;
    subtitle: string;
    back: string;
    start_pull: string;
    pulling: string;
    form: {
      model_name: string;
      model_name_placeholder: string;
    };
    validation: {
      model_name_required: string;
      model_name_invalid: string;
      model_not_found: string;
    };
    progress: {
      pulling: string;
      status: {
        downloading: string;
        completed: string;
        failed: string;
        cancelled: string;
        cancelling: string;
        exists: string;
        unknown: string;
      };
      download_speed: string;
      time_left: string;
      cancel_dialog: {
        title: string;
        message: string;
        confirm: string;
        cancel: string;
      };
      retry: string;
      done: string;
      error: string;
      connection_error: string;
    };
    overwrite_dialog: {
      title: string;
      message: string;
      confirm: string;
      cancel: string;
    },
    empty_state: {
      completed: {
        title: string;
        subtitle: string;
      };
      default: {
        title: string;
        subtitle: string;
      };
    };
  };
  
  // 添加自定义模型页面相关翻译
  custom_page: {
    title: string;
    subtitle: string;
    back: string;
    reset: string;
    create: string;
    tabs: {
      basic: string;
      parameters: string;
      license: string;
    };
    form: {
      name: {
        label: string;
        placeholder: string;
        required: string;
      };
      base_model: {
        label: string;
        placeholder: string;
        required: string;
      };
      prompt_template: {
        label: string;
        placeholder: string;
      };
      system_prompt: {
        label: string;
        placeholder: string;
        token_count: string;
        clear: string;
        copy: string;
        copied: string;
        cleared: string;
      };
      parameters: {
        core: {
          title: string;
          description: string;
          temperature: {
            label: string;
            tooltip: string;
          };
          context_window: {
            label: string;
            tooltip: string;
          };
        };
        sampling: {
          title: string;
          description: string;
          top_p: {
            label: string;
            tooltip: string;
          };
          top_k: {
            label: string;
            tooltip: string;
          };
          frequency_penalty: {
            label: string;
            tooltip: string;
          };
          presence_penalty: {
            label: string;
            tooltip: string;
          };
        };
        advanced: {
          title: string;
          description: string;
          repeat_penalty: {
            label: string;
            tooltip: string;
          };
          repeat_last_n: {
            label: string;
            tooltip: string;
          };
          mirostat: {
            label: string;
            tooltip: string;
            modes: {
              disabled: string;
              v1: string;
              v2: string;
            };
          };
          mirostat_tau: {
            label: string;
            tooltip: string;
          };
          mirostat_eta: {
            label: string;
            tooltip: string;
          };
          seed: {
            label: string;
            tooltip: string;
          };
          stop_sequences: {
            label: string;
            tooltip: string;
            placeholder: string;
          };
        };
      };
      license: {
        label: string;
        placeholder: string;
        token_count: string;
        clear: string;
        copy: string;
        copied: string;
        cleared: string;
      };
    };
    overwrite_dialog: {
      title: string;
      message: string;
      confirm: string;
      cancel: string;
    };
    notifications: {
      create_success: string;
      create_error: string;
      copy_success: string;
      copy_error: string;
      reset_success: string;
    };
  };
}

// 聊天页面消息类型
export interface ChatMessages {
  confirm_clear: {
    title: string;
    message: string;
  };
  confirm_refresh: {
    title: string;
    message: string;
  };
  thinking_process: {
    title: string;
    time: string;
    expand: string;
    collapse: string;
  };
  file_preview: {
    pdf_document: string;
    show_content: string;
    hide_content: string;
    file_types: {
      pdf: string;
      word: string;
      text: string;
      markdown: string;
      document: string;
      excel: string;
      csv: string;
      ppt: string;
      html: string;
    };
    file_size: string;

  };
  input: {
    placeholder: string;
    send: string;
    stop: string;
    model_select: string;
    web_search: string;
    upload_file: string;
    clear_conversation: string;
    upload_options: {
      image: string;
      document: string;
      image_tooltip: string;
      document_tooltip: string;
    };
    remove_file: string;
  };
  message_actions: {
    copy: string;
    delete: string;
    selected_copy: string;
    save_to_note: string;
    selected_save: string;
  };
  notifications: {
    copy_success: string;
    copy_error: string;
    saved_to_note: string;
    clear_success: string;
    clear_error: string;
    image_upload_success: string;
    image_upload_error: string;
    document_upload_success: string;
    document_upload_error: string;
    web_search_enabled: string;
    web_search_disabled: string;
    model_switch_success: string;
    model_switch_error: string;
    web_search_no_api_key: string;
    abort_success: string;
    abort_error: string;
  };
  errors: {
    connection_error: string;
    connection_closed: string;
    connection_timeout: string;
    retry_connecting: string;
    server_connection_failed: string;
  };
}

// 状态消息
export interface StatusMessages {
  success: string;
  error: string;
  warning: string;
  info: string;
  loading: string;
  enabled: string;
  disabled: string;
}

// 关于页面消息类型
export interface AboutMessages {
  title: string;
  subtitle: string;
  tabs: {
    app: string;
    license: string;
    changelog: string;
  };
  appInfo: {
    title: string;
    description: string;
    details: string;
    developer: string;
    developerText: string;
    website: string;
    websiteText: string;
    email: string;
    github: string;
    githubText: string;
    versionInfo: string;
    version: string;
    versionDesc: string;
    electronVersion: string;
    electronVersionDesc: string;
    lastCheck: string;
    lastCheckDesc: string;
    never: string;
    checkNow: string;
    checking: string;
    checkUpdate: string;
    updateSettings: string;
    autoCheck: string;
    autoCheckDesc: string;
    checkFrequency: string;
    checkFrequencyDesc: string;
    frequency: {
      startup: string;
      daily: string;
      weekly: string;
      monthly: string;
    };
    updateStatus: string;
    upToDate: string;
    updateAvailable: string;
    downloading: string;
    readyToInstall: string;
    updateError: string;
    downloadNow: string;
    installNow: string;
    downloadFailed: string;
    checkFailed: string;
    downloadSuccess: string;
    installSuccess: string;
    installFailed: string;
    cancelInstall: string;
    installCancelled: string;
  };
  license: {
    title: string;
    loading: string;
    error: string;
  };
  changelog: {
    title: string;
    description: string;
    viewOnGithub: string;
    loading: string;
    error: string;
  };
}

// 侧边栏消息类型
export interface SidebarMessages {
  home: string;
  chat: string;
  models: string;
  prompts: string;
  notes: string;
  history: string;
  user_menu: string;
  login: string;
  register: string;
  account_settings: string;
  features_settings: string;
  community: string;
  help_docs: string;
  about: string;
  logout: string;
  logo_tooltip: string;
  user_avatar: string;
}

// 笔记类型
export interface NotesMessages {
  title: string;
  subtitle: string;
  create_note: string;
  edit_note: string;
  create_subtitle: string;
  edit_subtitle: string;
  quick_note: string;
  preview: string;
  saved_from_chat: string;
  toggle_preview: string;
  back_to_edit: string;
  preview_empty: string;
  preview_requires_content: string;
  stats: {
    lines: string;
    chars: string;
  };
  empty_state: {
    title: string;
    subtitle: string;
  };
  search_placeholder: string;
  search_empty: {
    title: string;
    subtitle: string;
    clear_button: string;
  };
  delete_dialog: {
    title: string;
    confirm_message: string;
  };
  cancel_dialog: {
    title: string;
    message: string;
    confirm: string;
    cancel: string;
  };
  notifications: {
    create_success: string;
    create_error: string;
    update_success: string;
    update_error: string;
    delete_success: string;
    delete_error: string;
    load_error: string;
    export_success: string;
    export_error: string;
  };
  card: {
    time_format: {
      today: string;
      yesterday: string;
      this_week: string;
      date: string;
    };
    conversation_note: string;
    edit: string;
    delete: string;
  };
  form: {
    title_label: string;
    title_placeholder: string;
    title_required: string;
    content_label: string;
    content_placeholder: string;
    content_required: string;
  };
  export: {
    button: string;
    tooltip: string;
    empty_content: string;
  };
}

// 完整的消息类型
export interface Messages {
  common: CommonMessages;
  settings: SettingsMessages;
  features: FeaturesMessages;
  home: HomeMessages;
  history: HistoryMessages;
  prompt: PromptMessages;
  model: ModelMessages;
  notes: NotesMessages;
  status: StatusMessages;
  sidebar: SidebarMessages;
  chat: ChatMessages;
  about: AboutMessages;
}

// 声明模块扩展 vue-i18n
declare module 'vue-i18n' {
  export interface DefineLocaleMessage extends Messages {}
}
