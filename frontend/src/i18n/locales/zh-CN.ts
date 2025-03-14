import type { Messages } from '../types';

const messages: Messages = {
  status: {
    success: '成功',
    error: '错误',
    warning: '警告',
    info: '信息',
    loading: '加载中...',
    enabled: '已启用',
    disabled: '已关闭'
  },
  common: {
    app: {
      name: 'kun-lab',
      description: '轻量级本地部署 AI 对话应用'
    },
    locale: 'zh-CN',
    app_name: 'kun-lab',
    loading: '加载中...',
    empty_data: '暂无数据',
    yes: '是',
    no: '否',
    markdown: {
      copy_code: '复制代码',
      copied: '已复制'
    },
    notification: {
      close: '关闭通知'
    },
    actions: {
      save: '保存',
      cancel: '取消',
      confirm: '确认',
      delete: '删除',
      edit: '编辑',
      add: '添加',
      test: '测试',
      search: '搜索',
      refresh: '刷新',
      close: '关闭',
      back: '返回',
      next: '下一步',
      previous: '上一步',
      submit: '提交',
      clear: '清除',
      show: '显示',
      hide: '隐藏',
      learn_more: '了解更多',
      update: '更新',
      create: '创建',
      finish: '完成'
    },
    status: {
      success: '成功',
      error: '错误',
      warning: '警告',
      info: '信息',
      loading: '加载中...',
      enabled: '已启用',
      disabled: '已关闭'
    }
  },
  settings: {
    title: '设置',
    subtitle: '自定义您的 kun-lab 体验',
    tabs: {
      general: '常规设置',
      tools: '工具设置',
      appearance: '外观设置',
      advanced: '高级设置',
      account: '账户设置',
    },
    features: {
      title: '语言和主题'
    },
    account: {
      title: '账户设置',
      subtitle: '管理您的个人信息和账户偏好设置',
      tabs: {
        profile: '个人资料',
        security: '安全设置',
        preferences: '沉浸设置'
      },
      profile: {
        title: '个人信息',
        avatar: {
          title: '更换头像',
          description: '支持 JPG、PNG 格式',
          alt: '头像',
          success: '头像更新成功',
          error: '头像更新失败，请重试'
        },
        username: {
          label: '用户名',
          placeholder: '用户名不可修改'
        },
        nickname: {
          label: '昵称',
          placeholder: '请输入您的昵称',
          success: '昵称更新成功',
          error: '昵称更新失败'
        },
        email: {
          label: '邮箱地址',
          placeholder: '请输入邮箱地址',
          success: '邮箱地址更新成功',
          error: '邮箱地址更新失败'
        }
      },
      theme: {
        title: '主题设置',
        switch: {
          title: '深色模式',
          description: '切换深色和浅色主题',
          light: '浅色',
          dark: '深色',
          system: '跟随系统'
        }
      },
      security: {
        title: '修改密码',
        password: {
          current: {
            label: '当前密码',
            placeholder: '请输入当前密码'
          },
          new: {
            label: '新密码',
            placeholder: '请输入新密码（至少6位）'
          },
          confirm: {
            label: '确认新密码',
            placeholder: '请再次输入新密码'
          },
          success: '密码更新成功',
          error: '密码更新失败'
        }
      },
      preferences: {
        title: '沉浸设置',
        personal_info: {
          label: '个人偏好信息',
          placeholder: '请输入您希望AI记住的个人偏好信息...',
          description: '说明：添加您希望AI记住的个人偏好，如语言风格、回答格式等，启用后还会默认记住您的昵称。'
        },
        use_personal_info: {
          label: '沉浸式对话功能',
          description: '启用后，您的个人偏好信息将在每次对话中发送给模型'
        },
        enable_button: '启用并保存',
        disable_button: '关闭',
        enabled: '沉浸式对话功能已启用',
        disabled: '沉浸式对话功能已关闭',
        save_button: '保存偏好设置',
        saving: '保存中...',
        success: '个人偏好设置已更新',
        error: '更新偏好设置失败'
      }
    },
    general: {
      language: {
        title: '语言设置',
        description: '选择应用界面语言'
      },
      theme: {
        title: '主题',
        description: '选择应用主题',
        options: {
          light: '浅色',
          dark: '深色',
          system: '跟随系统'
        }
      }
    },
    tools: {
      tavily: {
        title: 'Tavily 搜索设置',
        description: 'Tavily 是一个强大的网络搜索 API，允许 AI 助手访问最新的互联网信息。',
        api_key: {
          label: 'API 密钥',
          placeholder: '请输入您的 Tavily API 密钥',
          description: '您的 API 密钥'
        },
        test_button: '测试连接',
        test_success: '连接成功',
        test_error: '连接失败',
        search_depth: {
          label: '搜索深度',
          basic: '基础',
          advanced: '高级',
          description: '基础搜索更快但结果较少，高级搜索更全面但较慢'
        },
        include_domains: {
          label: '包含域名',
          description: '搜索结果将优先显示这些域名的内容',
          placeholder: '输入域名并按回车添加（例如：example.com）'
        },
        exclude_domains: {
          label: '排除域名',
          description: '搜索结果将排除这些域名的内容',
          placeholder: '输入域名并按回车添加（例如：example.com）'
        }
      }
    }
  },
  features: {
    title: '系统设置',
    subtitle: '配置 kun-lab 功能'
  },
  home: {
    welcome: 'HI，{0}!',
    subtitle: '我是 kun-lab，这是一个私密空间，想聊啥都可以！',
    favorite_models: {
      title: '已收藏模型',
      view_more: '更多模型',
      empty_state: {
        title: '暂无收藏模型'
      }
    },
    new_chat: '开始新对话',
    delete_model: {
      title: '确认删除',
      confirm_message: '确定要删除模型 "{0}" 吗？此操作不可撤销。'
    }
  },
  history: {
    title: '对话记录',
    subtitle: '查看和管理您的所有对话历史',
    select_all: '全选',
    delete_selected: '删除选中',
    search_placeholder: '搜索对话内容...',

    retry: '重试',
    conversation_count: '您总共有 {0} 条对话记录',
    empty_state: {
      title: '暂无对话记录',
      subtitle: '开始新的对话，探索AI的无限可能',
      start_chat: '开始对话'
    },
    time_groups: {
      today: '今天',
      yesterday: '昨天',
      three_days: '三天内',
      last_week: '上周',
      earlier: '更早',
      date_range: '{0}',
      to: '至',
      and_earlier: '及更早'
    },
    date_format: {
      month_day: 'M月d日',
      year_month_day: 'yyyy年M月d日',
      time: 'HH:mm',
      date_time: 'yyyy年M月d日 HH:mm'
    },
    conversation: {
      untitled: '未命名对话',
      no_ai_response: '暂无消息',
      continue_chat: '继续对话',
      image_message: '[图片消息]',
      images_message: '[{0}张图片]',
      pdf_document: '[PDF文档]'
    },
    delete_dialog: {
      title: '删除确认',
      confirm_single: '确定要删除对话 {0} 吗？',
      confirm_multiple: '确定要删除选中的 {0} 条对话吗？',
      success_single: '对话已删除',
      success_multiple: '已删除 {0} 条对话',
      error: '删除失败'
    }
  },
  prompt: {
    title: '提示词库',
    subtitle: '管理和使用您的提示词模板, 让您的模型更有特色',
    create_prompt: '创建提示词',
    edit_prompt: '编辑提示词',
    empty_state: {
      title: '暂无提示词',
      subtitle: '创建您的第一个提示词模板'
    },
    form: {
      title_label: '标题',
      title_placeholder: '输入提示词标题',
      content_label: '内容',
      content_placeholder: '输入提示词内容',
      tags_label: '标签（可选，用逗号分隔）',
      tags_placeholder: '例如：翻译,写作,编程',
      cancel: '取消',
      save: '保存',
      create: '创建'
    },
    card: {
      created_at: '创建于',
      updated_at: '更新于',
      unknown_time: '未知时间',
      copy: '复制',
      edit: '编辑',
      delete: '删除',
      use: '使用'
    },
    delete_dialog: {
      title: '删除提示词',
      confirm_message: '确定要删除此提示词吗？此操作不可撤销。',
      success: '提示词已删除',
      error: '删除提示词失败'
    },
    notifications: {
      copied: '提示词已复制到剪贴板',
      create_success: '提示词创建成功',
      create_error: '创建提示词失败',
      update_success: '提示词更新成功',
      update_error: '更新提示词失败',
      delete_success: '提示词已删除',
      delete_error: '删除提示词失败',
      load_error: '加载提示词失败',
      get_error: '获取提示词失败'
    }
  },
  model: {
    title: '模型库',
    subtitle: '探索和管理您的AI模型库',
    create_model: '创建模型',
    custom_model: '自定义',
    pull_model: '拉取模型',
    empty_state: '暂无模型，请拉取新模型。',
    loading: "加载中..." ,
    delete_dialog: {
      title: '确认删除',
      confirm_message: '确定要删除模型 "{0}" 吗？此操作不可撤销。'
    },
    actions: {
      view_details: '查看详情',
      start_chat: '开始对话',
      delete: '删除'
    },
    notifications: {
      delete_success: '模型删除成功',
      delete_error: '删除模型失败',
      create_success: '模型创建成功',
      create_error: '创建对话失败',
      pull_success: '模型拉取成功',
      pull_error: '拉取模型失败',
      reset_success: '表单已重置'
    },
    card: {
      parameter_size: '参数规模',
      file_size: '文件大小',
      modified_time: '修改时间',
      unknown: '未知',
      tooltip: {
        details: '模型详情',
        chat: '开始新对话',
        delete: '删除模型'
      }
    },
    detail: {
      back: '返回',
      favorite: '收藏',
      unfavorite: '已收藏',
      favorited: '已收藏',
      tabs: {
        basic: '基础信息',
        advanced: '高级参数'
      },
      sections: {
        basic_info: '基本信息',
        modelfile_config: 'ModelFile 配置',
        model_parameters: '模型参数',
        template_config: '模板配置',
        license: '许可证',
        model_architecture: '模型架构',
        attention_params: 'Attention参数',
        tokenizer_params: 'Tokenizer参数'
      },
      actions: {
        expand: '展开',
        collapse: '收起'
      },
      info_labels: {
        name: '名称',
        family: '系列',
        parameter_size: '参数规模',
        quantization: '量化方式',
        file_size: '文件大小',
        created_at: '创建时间',
        modified_at: '修改时间',
        format: '格式',
        system_prompt: '系统提示词'
      },
      advanced_params: {
        architecture_type: '架构类型',
        base_model: '基础模型',
        organization: '开发组织',
        repo_url: '模型仓库',
        model_name: '模型名称',
        parameter_count: '参数数量',
        quantization_version: '量化版本',
        size_label: '规格大小',
        finetune_type: '微调类型',
        tags: '标签',
        context_length: '上下文长度',
        embedding_length: '嵌入长度',
        feed_forward: '前馈网络',
        head_count: '注意力头数',
        kv_head_count: 'KV头数',
        layer_count: '层数',
        vocabulary_size: '词汇表大小',
        attention_head_count: 'Attention头数',
        kv_head_count_param: 'KV头数',
        layer_norm_epsilon: '层归一化Epsilon',
        block_count: '块数量',
        context_length_param: '上下文长度',
        embedding_dimension: '嵌入维度',
        feed_forward_dimension: '前馈网络维度',
        rope_freq_base: 'RoPE基频',
        rope_dimension: 'RoPE维度',
        tokenizer_type: '分词器类型',
        add_bos_token: '添加BOS Token',
        add_eos_token: '添加EOS Token',
        bos_token_id: 'BOS Token ID',
        eos_token_id: 'EOS Token ID',
        padding_token_id: 'Padding Token ID',
        prefix: '前缀',
        type: '类型',
        model: '模型',
        tokens: '词元数量'
      }
    },
    
    // 拉取模型页面翻译
    pull_page: {
      title: '拉取模型',
      subtitle: '在此页面拉取您的模型',
      back: '返回',
      start_pull: '开始拉取',
      pulling: '拉取中...',
      form: {
        model_name: '模型名称',
        model_name_placeholder: '请输入模型名称，例如：ollama run qwen2.5:0.5b 或 ollama run hf.co/username/model:Q4_K_M'
      },
      validation: {
        model_name_required: '模型名称不能为空',
        model_name_invalid: '模型名称格式无效',
        model_not_found: '模型不存在，请检查模型名称是否正确'
      },
      progress: {
        pulling: '正在拉取',
        status: {
          downloading: '下载中',
          completed: '已完成',
          failed: '失败',
          cancelled: '已取消',
          cancelling: '取消中',
          exists: '已存在',
          unknown: '未知状态'
        },
        download_speed: '下载速度',
        time_left: '剩余时间',
        cancel_dialog: {
          title: '确认取消',
          message: '确定要取消拉取模型吗？此操作不可撤销。',
          confirm: '取消拉取',
          cancel: '继续拉取'
        },
        retry: '重试',
        done: '完成',
        error: '拉取模型时出错',
        connection_error: '连接服务器失败，请检查网络连接'
      },
      overwrite_dialog: {
        title: '模型已存在',
        message: '模型 "{modelName}" 已存在，是否要重新拉取（覆盖）？',
        confirm: '重新拉取',
        cancel: '取消'
      },
      empty_state: {
        completed: {
          title: '恭喜您！已完成拉取',
          subtitle: '返回模型库即可使用'
        },
        default: {
          title: '暂无拉取任务',
          subtitle: '点击图标浏览相应平台的模型'
        }
      }
    },
    
    // 自定义模型页面翻译
    custom_page: {
      title: '自定义模型',
      subtitle: '配置和创建您的自定义AI模型',
      back: '返回',
      reset: '重置',
      create: '创建模型',
      tabs: {
        basic: '基础信息',
        parameters: '模型参数',
        license: '许可证'
      },
      form: {
        name: {
          label: '模型名称',
          placeholder: '请输入模型名称',
          required: '模型名称不能为空'
        },
        base_model: {
          label: '基础模型',
          placeholder: '--请选择--',
          required: '基础模型不能为空'
        },
        prompt_template: {
          label: '提示词模板',
          placeholder: '--请选择--'
        },
        system_prompt: {
          label: '系统提示词',
          placeholder: '请输入系统提示词（可选）',
          token_count: 'Tokens',
          clear: '清空',
          copy: '复制代码',
          copied: '已复制到剪贴板',
          cleared: '已清空所有内容'
        },
        parameters: {
          core: {
            title: '核心参数',
            description: '这些参数会直接影响模型的基础行为',
            temperature: {
              label: '温度（Temperature）',
              tooltip: '控制生成文本的随机性，值越高输出越随机'
            },
            context_window: {
              label: '上下文窗口（Context Window）',
              tooltip: '模型能记住的最大内容长度，越大记忆力越好但消耗更多资源'
            }
          },
          sampling: {
            title: '采样参数',
            description: '控制模型在生成文本时如何选择下一个词',
            top_p: {
              label: 'Top P（核心采样）',
              tooltip: '控制输出多样性，值越低输出越确定'
            },
            top_k: {
              label: 'Top K（候选词数）',
              tooltip: '每一步考虑的候选词数量，值越大多样性越高'
            },
            frequency_penalty: {
              label: '频率惩罚（Frequency Penalty）',
              tooltip: '减少模型重复使用相同词汇的倾向，值越高重复越少'
            },
            presence_penalty: {
              label: '存在惩罚（Presence Penalty）',
              tooltip: '减少模型重复讨论相同主题的倾向，值越高话题越多样'
            }
          },
          advanced: {
            title: '高级参数',
            description: '用于微调模型的高级控制参数',
            repeat_penalty: {
              label: '重复惩罚（Repeat Penalty）',
              tooltip: '惩罚模型重复之前生成的内容，值越高重复越少'
            },
            repeat_last_n: {
              label: '重复最后N个',
              tooltip: '查找重复的令牌数量，较大的值会检查更多上下文'
            },
            mirostat: {
              label: 'Mirostat模式',
              tooltip: '自适应控制算法，保持输出复杂度在稳定水平',
              modes: {
                disabled: '禁用',
                v1: 'Mirostat v1',
                v2: 'Mirostat v2'
              }
            },
            mirostat_tau: {
              label: 'Mirostat目标熵',
              tooltip: '目标复杂度，值越低输出越简单，值越高输出越复杂'
            },
            mirostat_eta: {
              label: 'Mirostat学习率',
              tooltip: 'Mirostat算法的学习率，值越大调整越快'
            },
            seed: {
              label: '随机种子（Seed）',
              tooltip: '控制随机性的种子值，相同种子在相同输入下会产生相同输出'
            },
            stop_sequences: {
              label: '停止序列（Stop Sequences）',
              tooltip: '当模型生成这些序列时停止生成，多个序列用逗号分隔',
              placeholder: '输入停止序列，多个用逗号分隔'
            }
          }
        },
        license: {
          label: '许可证',
          placeholder: '请输入许可证内容（可选）',
          token_count: 'Tokens',
          clear: '清空',
          copy: '复制代码',
          copied: '已复制到剪贴板',
          cleared: '已清空所有内容'
        }
      },
      overwrite_dialog: {
        title: '确认覆盖模型',
        message: '已存在同名模型，是否覆盖？',
        confirm: '确认覆盖',
        cancel: '取消'
      },
      notifications: {
        create_success: '模型创建成功',
        create_error: '模型创建失败',
        copy_success: '复制成功',
        copy_error: '复制失败',
        reset_success: '表单已重置'
      }
    }
  },
  sidebar: {
    home: '首页',
    chat: '聊天对话',
    models: '模型库',
    prompts: '提示词',
    history: '对话记录',
    user_menu: '用户菜单',
    login: '登录',
    register: '注册',
    account_settings: '账户设置',
    features_settings: '系统设置',
    community: '社区空间',
    help_docs: '帮助文档',
    logout: '退出登录',
    logo_tooltip: 'kun-lab',
    user_avatar: '用户头像'
  },
  chat: {
    confirm_clear: {
      title: '确认清空对话',
      message: '确定要清空当前对话吗？此操作将永久删除所有对话内容，且不可恢复。'
    },
    confirm_refresh: {
      title: '确认刷新页面',
      message: 'AI 模型正在生成内容，刷新页面将会中断生成过程。确定要刷新吗？'
    },
    thinking_process: {
      title: '思考过程',
      time: '({0})',
      expand: '展开',
      collapse: '收起'
    },
    message_actions: {
      copy: '复制',
      delete: '删除'
    },
    file_preview: {
      pdf_document: 'PDF文档',
      show_content: '查看内容',
      hide_content: '收起内容',
      file_types: {
        pdf: 'PDF 文档',
        word: 'Word 文档',
        text: '文本文档',
        html: 'HTML 文档',
        markdown: 'Markdown 文档',
        document: '文档'
      }
    },
    input: {
      placeholder: '请输入对话内容...',
      send: '发送消息',
      stop: '停止生成',
      model_select: '选择对话模型',
      web_search: '开启/关闭网页搜索',
      upload_file: '上传文件',
      clear_conversation: '清空当前对话',
      upload_options: {
        image: '上传图片',
        document: '上传文档',
        image_tooltip: '支持PNG、JPEG、JPG格式（视觉模型专用）',
        document_tooltip: '请选择PDF、DOC、PPT、XLS、HTML、CSV、TXT格式文档上传'
      },
      remove_file: '移除文件'
    },
    notifications: {
      copy_success: '复制成功',
      copy_error: '复制失败：',
      clear_success: '对话清空成功',
      clear_error: '对话清空失败：',
      image_upload_success: '图片上传成功',
      image_upload_error: '图片上传失败',
      document_upload_success: '文档上传成功',
      document_upload_error: '文档上传失败',
      web_search_enabled: '网页搜索功能已开启',
      web_search_disabled: '网页搜索功能已关闭',
      web_search_no_api_key: 'Tavily API key not configured. Please go to Tools Settings to configure it before using web search feature',
      model_switch_success: '模型切换成功：{model}',
      model_switch_error: '模型切换失败：{error}',
      abort_success: '已停止生成',
      abort_error: '停止生成失败：{error}'
    },
    errors: {
      connection_error: 'WebSocket连接错误，请检查网络或服务器状态',
      connection_closed: 'WebSocket连接已关闭，请尝试刷新页面',
      connection_timeout: 'WebSocket连接超时，请稍后重试',
      retry_connecting: 'WebSocket连接超时，正在重试 ({count}/{max})...',
      server_connection_failed: '连接服务器失败，请检查网络或服务器状态'
    }
  }
};

export default messages;
