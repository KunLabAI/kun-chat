import type { Messages } from '../types';

const messages: Messages = {
  status: {
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
    info: 'Info',
    loading: 'Loading...',
    enabled: 'Enabled',
    disabled: 'Disabled'
  },
  common: {
    app: {
      name: 'kun-lab',
      description: 'Lightweight AI chat application for local deployment'
    },
    locale: 'en-US',
    app_name: 'kun-lab',
    loading: 'Loading...',
    empty_data: 'No data available',
    yes: 'Yes',
    no: 'No',
    markdown: {
      copy_code: 'Copy Code',
      copied: 'Copied',
      preview_code: 'Preview Code',
      html_preview: 'HTML Code Preview',
      open_in_new_window: 'Open in New Window',
      close: 'Close',
      expand_code: 'Expand Code',
      collapse_code: 'Collapse Code'
    },
    notification: {
      close: 'Close Notification'
    },
    actions: {
      save: 'Save',
      cancel: 'Cancel',
      confirm: 'Confirm',
      delete: 'Delete',
      copy:'copy',
      edit: 'Edit',
      add: 'Add',
      test: 'Test',
      search: 'Search',
      refresh: 'Refresh',
      close: 'Close',
      back: 'Back',
      next: 'Next',
      previous: 'Previous',
      submit: 'Submit',
      clear: 'Clear',
      show: 'Show',
      hide: 'Hide',
      learn_more: 'Learn More',
      update: 'Update',
      create: 'Create',
      finish: 'Finish',
      ok: 'OK'
    },
    status: {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info',
      loading: 'Loading...',
      enabled: 'Enabled',
      disabled: 'Disabled'
    },
    not_available: 'Not available',
    tools: {
      gpu_calculator: {
        title: 'GPU Memory Calculator',
        tooltips: 'Calculate GPU memory requirements'
      }
    }
  },
  settings: {
    title: 'Settings',
    subtitle: 'Customize your kun-lab experience',
    tabs: {
      general: 'General',
      tools: 'Tool',
      connection: 'Engine',
      network: 'Network'
    },
    features: {
      title: 'Language & Theme'
    },
    account: {
      title: 'Account Settings',
      subtitle: 'Manage your personal information and account preferences',
      tabs: {
        profile: 'Profile',
        security: 'Security',
        preferences: 'Immersion'
      },
      profile: {
        title: 'Personal Information',
        avatar: {
          title: 'Change Avatar',
          description: 'Supports JPG, PNG formats',
          alt: 'Avatar',
          success: 'Avatar updated successfully',
          error: 'Failed to update avatar, please try again'
        },
        username: {
          label: 'Username',
          placeholder: 'Username cannot be modified'
        },
        nickname: {
          label: 'Nickname',
          placeholder: 'Enter your nickname',
          success: 'Nickname updated successfully',
          error: 'Failed to update nickname'
        },
        email: {
          label: 'Email Address',
          placeholder: 'Enter your email address',
          success: 'Email address updated successfully',
          error: 'Failed to update email address'
        }
      },
      theme: {
        title: 'Theme Settings',
        switch: {
          title: 'Dark Mode',
          description: 'Toggle between dark and light themes',
          light: 'Light',
          dark: 'Dark',
          system: 'System'
        }
      },
      security: {
        title: 'Change Password',
        password: {
          current: {
            label: 'Current Password',
            placeholder: 'Enter your current password'
          },
          new: {
            label: 'New Password',
            placeholder: 'Enter new password (at least 6 characters)'
          },
          confirm: {
            label: 'Confirm New Password',
            placeholder: 'Re-enter your new password'
          },
          success: 'Password updated successfully',
          error: 'Failed to update password'
        }
      },
      preferences: {
        title: 'Immersive Settings',
        personal_info: {
          placeholder: 'Enter your personal preferences that you want the AI to remember...',
          description: 'Add personal preferences that you want the AI to remember, such as language style, answer format, etc., and when enabled, it will also remember your nickname by default.'
        },
        use_personal_info: {
          label: 'Immersive Conversation Feature',
          description: 'When enabled, your personal preference information will be sent to the model in each conversation'
        },
        enable_button: 'Enable & Save',
        disable_button: 'Disable',
        enabled: 'Immersive conversation feature enabled',
        disabled: 'Immersive conversation feature disabled',
        save_button: 'Save Preferences',
        saving: 'Saving...',
        success: 'Personal preferences updated successfully',
        error: 'Failed to update preferences'
      }
    },
    general: {
      language: {
        title: 'Language Settings',
      },
      theme: {
        title: 'Theme',
        options: {
          light: 'Light',
          dark: 'Dark',
          system: 'System'
        }
      }
    },
    tools: {
      tavily: {
        title: 'Tavily Search Settings',
        description: 'Tavily search requires users to register an account and obtain an API key.',
        api_key: {
          label: 'API Key',
          placeholder: 'Enter your Tavily API key',
          description: 'Your API key'
        },
        apiKeyHint: 'Enter your API key and click save, then use the "Test Connection" button below to verify the key validity',
        test_button: 'Test Connection',
        test_success: 'Connection successful',
        test_error: 'Connection failed',
        connecting: 'Connecting...',
        hide_key: 'Hide Key',
        show_key: 'Show Key',
        delete_key: 'Delete Key',
        domain_format_error: 'Please enter a valid domain format',
        search_depth: {
          label: 'Search Depth',
          basic: 'Basic',
          advanced: 'Advanced',
          description: 'Basic search is faster with fewer results, Advanced search is more comprehensive but slower'
        },
        include_domains: {
          label: 'Include Domains',
          description: 'Search results will prioritize content from these domains',
          placeholder: 'Enter domain and press Enter to add (e.g. example.com)'
        },
        exclude_domains: {
          label: 'Exclude Domains',
          description: 'Search results will exclude content from these domains',
          placeholder: 'Enter domain and press Enter to add (e.g. example.com)'
        },
        messages: {
          api_key_cleared: 'API key cleared',
          api_key_saved: 'API key saved, please click the "Test Connection" button to verify its validity',
          search_depth_updated: 'Search depth updated successfully',
          include_domains_updated: 'Include domains updated successfully',
          exclude_domains_updated: 'Exclude domains updated successfully',
          connection_test_success: 'Connection test successful, API key is valid',
          api_key_verified: 'API key verification successful'
        },
        errors: {
          clear_api_key_failed: 'Failed to clear API key',
          get_settings_failed: 'Failed to get Tavily settings, please try again later',
          invalid_api_key: 'Please enter a valid API key',
          save_api_key_failed: 'Failed to save API key, please try again later',
          update_search_depth_failed: 'Failed to update search depth',
          update_include_domains_failed: 'Failed to update include domains',
          update_exclude_domains_failed: 'Failed to update exclude domains',
          connection_test_failed: 'Connection test failed'
        },
        warnings: {
          domain_exists: 'This domain already exists',
          set_api_key_first: 'Please set an API key first'
        }
      }
    },
    connection: {
      ollama: {
        title: 'Ollama inference engine Settings',
        host: {
          label: 'Connection Settings',
          placeholder: 'Enter Ollama host address (e.g. http://localhost:11434)',
          description: 'Configure the connection address of the Ollama service'
        },
        test_success: 'Connection successful',
        test_error: 'Connection failed',
        status: {
          label: 'Connection Status',
          description: 'Shows the current connection status and version information of the Ollama service',
          connected: 'Connected',
          disconnected: 'Disconnected',
          version: 'Version',
          state: 'Status'
        },
        auto_check: {
          label: 'Automatic Connection Check',
          description: 'Automatically check connection every 30 minutes (default)'
        },
        notification: {
          label: 'Show Connection Status Change Notifications',
          connected: 'Successfully connected to Ollama service ({version})',
          disconnected: 'Unable to connect to Ollama service ({host}), please check if the service is running'
        },
        save_button: 'Save',
        checking: 'Checking...',
        save_success: 'Ollama connection settings saved',
        save_failed: 'Failed to save settings',
        load_failed: 'Failed to load settings'
      }
    }
  },
  features: {
    title: 'System Settings',
    subtitle: 'Configure kun-lab features'
  },
  home: {
    welcome: 'HI, {0}!',
    subtitle: 'I am kun-lab. This is a private space, talk about anything you like!',
    favorite_models: {
      title: 'Favorite Models',
      view_more: 'More Models',
    },
    onboarding: {
      install_ollama: 'Install Ollama',
      pull_models: 'Pull Models',
    },
    new_chat: 'Start New Chat',
    delete_model: {
      title: 'Confirm Deletion',
      confirm_message: 'Are you sure you want to delete model ? This action cannot be undone.'
    }
  },
  history: {
    title: 'Conversation History',
    subtitle: 'Browse and manage your conversation history',
    loading: 'Loading conversation history...',
    select_all: 'Select All',
    delete_selected: 'Delete Selected',
    search_placeholder: 'Search conversations...',
    retry: 'Retry',
    conversation_count: 'You have {0} conversations in total',
    empty_state: {
      title: 'No Conversations Yet',
      start_chat: 'Start Conversation'
    },
    time_groups: {
      today: 'Today',
      yesterday: 'Yesterday',
      three_days: 'Last 3 Days',
      last_week: 'Last Week',
      earlier: 'Earlier',
      date_range: '{0}',
      to: 'to',
      and_earlier: 'and earlier'
    },
    date_format: {
      month_day: 'MMM d',
      year_month_day: 'MMM d, yyyy',
      time: 'h:mm a',
      date_time: 'MMM d, yyyy h:mm a'
    },
    conversation: {
      untitled: 'Untitled Conversation',
      no_ai_response: 'No Message',
      continue_chat: 'Continue Chat',
      image_message: '[Image Message]',
      images_message: '[{0} Images]',
      pdf_document: '[PDF Document]',
      loading_message: 'Loading conversation content...'
    },
    delete_dialog: {
      title: 'Confirm Deletion',
      confirm_single: 'Are you sure you want to delete conversation {0}?',
      confirm_multiple: 'Are you sure you want to delete {0} selected conversations?',
      success_single: 'Conversation deleted',
      success_multiple: 'Deleted {0} conversations',
      error: 'Failed to delete'
    }
  },
  prompt: {
    title: 'Prompt Library',
    subtitle: 'Manage and use prompt templates to customize your model.',
    create_prompt: 'Create Prompt',
    edit_prompt: 'Edit Prompt',
    empty_state: {
      title: 'No prompts yet',
      subtitle: 'Create your first prompt template'
    },
    form: {
      title_label: 'Title',
      title_placeholder: 'Enter prompt title',
      content_label: 'Content',
      content_placeholder: 'Enter prompt content',
      tags_label: 'Tags (Optional, comma separated)',
      tags_placeholder: 'E.g.: translation,writing,programming',
      cancel: 'Cancel',
      save: 'Save',
      create: 'Create'
    },
    card: {
      created_at: 'Created at',
      updated_at: 'Updated at',
      unknown_time: 'Unknown time',
      copy: 'Copy',
      edit: 'Edit',
      delete: 'Delete',
      use: 'Use'
    },
    delete_dialog: {
      title: 'Delete Prompt',
      confirm_message: 'Are you sure you want to delete this prompt? This action cannot be undone.',
      success: 'Prompt deleted',
      error: 'Failed to delete prompt'
    },
    notifications: {
      copied: 'Prompt copied to clipboard',
      create_success: 'Prompt created successfully',
      create_error: 'Failed to create prompt',
      update_success: 'Prompt updated successfully',
      update_error: 'Failed to update prompt',
      delete_success: 'Prompt deleted',
      delete_error: 'Failed to delete prompt',
      load_error: 'Failed to load prompts',
      get_error: 'Failed to get prompt'
    }
  },
  model: {
    title: 'Model Library',
    subtitle: 'Explore and manage your AI model library',
    create_model: 'Create Model',
    custom_model: 'Customize',
    pull_model: 'Pull Model',
    empty_state: {
      title: 'No models available. Please pull a new model.',
    },
    loading: "Loading models..." ,
    delete_dialog: {
      title: 'Confirm Deletion',
      confirm_message: 'Are you sure you want to delete model "{0}"? This action cannot be undone.'
    },
    actions: {
      view_details: 'View Details',
      start_chat: 'Start Chat',
      delete: 'Delete'
    },
    notifications: {
      delete_success: 'Model deleted successfully',
      delete_error: 'Failed to delete model',
      create_success: 'Model created successfully',
      create_error: 'Failed to create chat',
      pull_success: 'Model pulled successfully',
      pull_error: 'Failed to pull model',
      reset_success: 'Form has been reset'
    },
    card: {
      parameter_size: 'Parameter Size',
      file_size: 'File Size',
      modified_time: 'Modified Time',
      unknown: 'Unknown',
      tooltip: {
        details: 'Model Details',
        chat: 'Start New Chat',
        delete: 'Delete Model'
      }
    },
    gpu_calculator: {
      title: 'GPU Memory Calculator',
      close_button: 'Close',
      parameter_count: 'Parameter Count (billions)',
      parameter_unit: 'B',
      quantization_bits: 'Quantization Bits',
      memory_required: 'Memory Required',
      placeholder: 'Enter parameter count'
    },
    detail: {
      back: 'Back',
      favorite: 'Favorite',
      unfavorite: 'Favorited',
      favorited: 'Favorited',
      tabs: {
        basic: 'Basic Info',
        advanced: 'Advanced Parameters'
      },
      sections: {
        basic_info: 'Basic Information',
        modelfile_config: 'ModelFile Configuration',
        model_parameters: 'Model Parameters',
        template_config: 'Template Configuration',
        license: 'License',
        model_architecture: 'Model Architecture',
        attention_params: 'Attention Parameters',
        tokenizer_params: 'Tokenizer Parameters'
      },
      actions: {
        expand: 'Expand',
        collapse: 'Collapse'
      },
      system_prompt_title: 'System Prompt',
      info_labels: {
        name: 'Name',
        family: 'Family',
        parameter_size: 'Parameter Size',
        quantization: 'Quantization',
        file_size: 'File Size',
        created_at: 'Created At',
        modified_at: 'Modified At',
        format: 'Format',
        system_prompt: 'System Prompt',
        system: 'System Prompt'
      },
      advanced_params: {
        architecture_type: 'Architecture Type',
        base_model: 'Base Model',
        organization: 'Organization',
        repo_url: 'Repository URL',
        model_name: 'Model Name',
        parameter_count: 'Parameter Count',
        quantization_version: 'Quantization Version',
        size_label: 'Size Label',
        finetune_type: 'Finetune Type',
        tags: 'Tags',
        context_length: 'Context Length',
        embedding_length: 'Embedding Length',
        feed_forward: 'Feed Forward',
        head_count: 'Head Count',
        kv_head_count: 'KV Head Count',
        layer_count: 'Layer Count',
        vocabulary_size: 'Vocabulary Size',
        attention_head_count: 'Attention Head Count',
        kv_head_count_param: 'KV Head Count',
        layer_norm_epsilon: 'Layer Norm Epsilon',
        block_count: 'Block Count',
        context_length_param: 'Context Length',
        embedding_dimension: 'Embedding Dimension',
        feed_forward_dimension: 'Feed Forward Dimension',
        rope_freq_base: 'RoPE Frequency Base',
        rope_dimension: 'RoPE Dimension',
        tokenizer_type: 'Tokenizer Type',
        add_bos_token: 'Add BOS Token',
        add_eos_token: 'Add EOS Token',
        bos_token_id: 'BOS Token ID',
        eos_token_id: 'EOS Token ID',
        padding_token_id: 'Padding Token ID',
        prefix: 'Prefix',
        type: 'Type',
        model: 'Model',
        tokens: 'Tokens',
        sliding_window: 'Sliding Window',
        key_length: 'Key Length',
        value_length: 'Value Length',
        version: 'Version',
        languages: 'Supported Languages'
      }
    },
    pull_page: {
      title: 'Pull Model',
      subtitle: 'Pull your model on this page',
      back: 'Back',
      start_pull: 'Start Pull',
      pulling: 'Pulling...',
      form: {
        model_name: 'Model Name',
        model_name_placeholder: 'e.g.: ollama run qwen2.5:0.5b or ollama run hf.co/username/model:Q4_K_M'
      },
      validation: {
        model_name_required: 'Model name is required',
        model_name_invalid: 'Invalid model name format',
        model_not_found: 'Model not found, please check if the model name is correct'
      },
      progress: {
        pulling: 'Pulling',
        status: {
          downloading: 'Downloading',
          completed: 'Completed',
          failed: 'Failed',
          cancelled: 'Cancelled',
          cancelling: 'Cancelling',
          exists: 'Exists',
          unknown: 'Unknown Status'
        },
        download_speed: 'Download Speed',
        time_left: 'Time Left',
        cancel_dialog: {
          title: 'Confirm Cancel',
          message: 'Are you sure you want to cancel pulling this model? This action cannot be undone.',
          confirm: 'Cancel Pull',
          cancel: 'Continue Pulling'
        },
        retry: 'Retry',
        done: 'Done',
        error: 'Error pulling model',
        connection_error: 'Failed to connect to server, please check your network connection'
      },
      overwrite_dialog: {
        title: 'Model Already Exists',
        message: 'Model "{modelName}" already exists. Do you want to pull it again (overwrite)?',
        confirm: 'Pull Again',
        cancel: 'Cancel'
      },
      empty_state: {
        completed: {
          title: 'Congratulations! Pull completed',
          subtitle: 'Return to model library to use it'
        },
        default: {
          title: 'No pull tasks',
          subtitle: 'Click the icons to browse models on respective platforms'
        }
      }
    },
    custom_page: {
      title: 'Custom Model',
      subtitle: 'Configure and create your custom AI model',
      back: 'Back',
      reset: 'Reset',
      create: 'Create Model',
      tabs: {
        basic: 'Basic Info',
        parameters: 'Model Parameters',
        license: 'License'
      },
      form: {
        name: {
          label: 'Model Name',
          placeholder: 'Enter model name',
          required: 'Model name is required'
        },
        base_model: {
          label: 'Base Model',
          placeholder: '--Please select--',
          required: 'Base model is required'
        },
        prompt_template: {
          label: 'Prompt Template',
          placeholder: '--Please select--'
        },
        system_prompt: {
          label: 'System Prompt',
          placeholder: 'Enter system prompt (optional)',
          token_count: 'Tokens',
          clear: 'Clear',
          copy: 'Copy Code',
          copied: 'Copied to clipboard',
          cleared: 'All content cleared'
        },
        parameters: {
          core: {
            title: 'Core Parameters',
            description: 'These parameters directly affect the basic behavior of the model',
            temperature: {
              label: 'Temperature',
              tooltip: 'Controls randomness of generated text, higher values produce more random outputs'
            },
            context_window: {
              label: 'Context Window',
              tooltip: 'Maximum content length the model can remember, larger values improve memory but consume more resources'
            }
          },
          sampling: {
            title: 'Sampling Parameters',
            description: 'Controls how the model selects the next word when generating text',
            top_p: {
              label: 'Top P (Nucleus Sampling)',
              tooltip: 'Controls output diversity, lower values make output more deterministic'
            },
            top_k: {
              label: 'Top K (Candidate Words)',
              tooltip: 'Number of candidate words considered at each step, higher values increase diversity'
            },
            frequency_penalty: {
              label: 'Frequency Penalty',
              tooltip: 'Reduces model\'s tendency to repeat the same words, higher values reduce repetition'
            },
            presence_penalty: {
              label: 'Presence Penalty',
              tooltip: 'Reduces model\'s tendency to repeat the same topics, higher values produce more diverse topics'
            }
          },
          advanced: {
            title: 'Advanced Parameters',
            description: 'Advanced control parameters for fine-tuning the model',
            repeat_penalty: {
              label: 'Repeat Penalty',
              tooltip: 'Penalizes the model for repeating previously generated content, higher values reduce repetition'
            },
            repeat_last_n: {
              label: 'Repeat Last N',
              tooltip: 'Number of tokens to look back for repetitions, larger values check more context'
            },
            mirostat: {
              label: 'Mirostat Mode',
              tooltip: 'Adaptive control algorithm to maintain output complexity at a stable level',
              modes: {
                disabled: 'Disabled',
                v1: 'Mirostat v1',
                v2: 'Mirostat v2'
              }
            },
            mirostat_tau: {
              label: 'Mirostat Target Entropy',
              tooltip: 'Target complexity, lower values produce simpler output, higher values produce more complex output'
            },
            mirostat_eta: {
              label: 'Mirostat Learning Rate',
              tooltip: 'Learning rate for Mirostat algorithm, higher values adjust faster'
            },
            seed: {
              label: 'Seed',
              tooltip: 'Seed value for controlling randomness, same seed with same input produces same output'
            },
            stop_sequences: {
              label: 'Stop Sequences',
              tooltip: 'Model stops generating when these sequences are produced, separate multiple sequences with commas',
              placeholder: 'Enter stop sequences, separate with commas'
            }
          }
        },
        license: {
          label: 'License',
          placeholder: 'Enter license content (optional)',
          token_count: 'Tokens',
          clear: 'Clear',
          copy: 'Copy Code',
          copied: 'Copied to clipboard',
          cleared: 'All content cleared'
        }
      },
      overwrite_dialog: {
        title: 'Confirm Model Overwrite',
        message: 'A model with this name already exists. Do you want to overwrite it?',
        confirm: 'Confirm Overwrite',
        cancel: 'Cancel'
      },
      notifications: {
        create_success: 'Model created successfully',
        create_error: 'Failed to create model',
        copy_success: 'Copied successfully',
        copy_error: 'Failed to copy',
        reset_success: 'Form has been reset'
      },
      errors: {
        name_conflict: 'Model name conflict for \'{name}\'. Please delete the existing model first or use a different name.',
        delete_failed: 'Failed to delete existing model, please try again later'
      }
    }
  },
  sidebar: {
    home: 'Home',
    chat: 'Chat',
    models: 'Models',
    prompts: 'Prompts',
    notes: 'Notes',
    history: 'History',
    user_menu: 'User Menu',
    login: 'Login',
    register: 'Register',
    account_settings: 'Account',
    features_settings: 'System',
    community: 'Community',
    help_docs: 'Help',
    about: 'About',
    logout: 'Logout',
    logo_tooltip: 'kun-lab',
    user_avatar: 'User Avatar'
  },
  notes: {
    title: 'Notes',
    subtitle: 'Manage and browse your notes',
    create_note: 'Create Note',
    edit_note: 'Edit Note',
    create_subtitle: 'Record your thoughts, insights and inspirations',
    edit_subtitle: 'Update your note content',
    quick_note: 'Quick Note',
    preview: 'Preview',
    saved_from_chat: 'Successfully saved to notes',
    toggle_preview: 'Toggle Preview',
    back_to_edit: 'Back to Edit',
    preview_empty: 'Nothing to preview',
    preview_requires_content: 'Please enter some content to preview',
    stats: {
      lines: 'lines',
      chars: 'chars'
    },
    empty_state: {
      title: 'No Notes',
      subtitle: 'Create your first note'
    },
    search_placeholder: 'Search notes...',
    search_empty: {
      title: 'No matching notes',
      subtitle: 'Try a different search term',
      clear_button: 'Clear Search'
    },
    delete_dialog: {
      title: 'Delete Note',
      confirm_message: 'Are you sure you want to delete this note? This action cannot be undone.'
    },
    cancel_dialog: {
      title: 'Discard Changes',
      message: 'You have unsaved changes. Are you sure you want to discard them?',
      confirm: 'Discard',
      cancel: 'Continue Editing'
    },
    notifications: {
      create_success: 'Note created successfully',
      create_error: 'Failed to create note',
      update_success: 'Note updated successfully',
      update_error: 'Failed to update note',
      delete_success: 'Note deleted',
      delete_error: 'Failed to delete note',
      load_error: 'Failed to load notes',
      export_success: 'Note exported successfully',
      export_error: 'Failed to export note'
    },
    card: {
      time_format: {
        today: 'Today',
        yesterday: 'Yesterday',
        this_week: 'This Week',
        date: 'Date'
      },
      conversation_note: 'Conversation Note',
      edit: 'Edit',
      delete: 'Delete'
    },
    form: {
      title_label: 'Title',
      title_placeholder: 'Enter note title',
      title_required: 'Title is required',
      content_label: 'Content',
      content_placeholder: 'Enter note content...',
      content_required: 'Content is required'
    },
    export: {
      button: 'Export',
      tooltip: 'Export as Markdown file',
      empty_content: 'Note content is empty, cannot export'
    }
  },
  chat: {
    confirm_clear: {
      title: 'Confirm Clear Conversation',
      message: 'Are you sure you want to clear the current conversation? This action will permanently delete all conversation content and cannot be undone.'
    },
    confirm_refresh: {
      title: 'Confirm Page Refresh',
      message: 'The AI model is currently generating content. Refreshing the page will interrupt this process. Are you sure you want to refresh?'
    },
    thinking_process: {
      title: 'Thinking Process',
      time: '({0})',
      expand: 'Expand',
      collapse: 'Collapse'
    },
    model_status: {
      loading: 'Loading model...',
      ready: 'Model ready',
      error: 'Model loading failed'
    },
    file_preview: {
      pdf_document: 'PDF Document',
      show_content: 'Show Content',
      hide_content: 'Hide Content',
      file_types: {
        pdf: 'PDF Document',
        word: 'Word Document',
        text: 'Text Document',
        markdown: 'Markdown Document',
        document: 'Document',
        excel: 'Excel Spreadsheet',
        csv: 'CSV Spreadsheet',
        ppt: 'PowerPoint Presentation',
        html: 'HTML Document'
      },
      file_size: 'File Size'
    },
    input: {
      placeholder: 'Type your message...',
      send: 'Send Message',
      stop: 'Stop Generating',
      connecting: 'Connecting...',
      thinking: 'Thinking...',
      tool_calling: 'Using tools...',
      model_select: 'Select Model',
      web_search: 'Toggle Web Search',
      upload_file: 'Upload File',
      clear_conversation: 'Clear Conversation',
      upload_options: {
        image: 'Upload Image',
        document: 'Upload Document',
        image_tooltip: 'Supports PNG, JPEG, JPG formats (for vision models)',
        document_tooltip: 'Please select PDF, DOC, PPT, XLS, HTML, CSV, or TXT format documents'
      },
      remove_file: 'Remove File'
    },
    message_actions: {
      copy: 'Copy',
      delete: 'Delete',
      selected_copy: 'Copy Selected Text',
      save_to_note: 'Save to Notes',
      selected_save: 'Save Selection to Notes'
    },
    notifications: {
      copy_success: 'Copied successfully',
      copy_error: 'Copy failed: ',
      saved_to_note: 'Content saved to notes',
      clear_success: 'Chat cleared successfully',
      clear_error: 'Failed to clear chat: ',
      image_upload_success: 'Image uploaded successfully',
      image_upload_error: 'Failed to upload image',
      document_upload_success: 'Document uploaded successfully',
      document_upload_error: 'Failed to upload document',
      web_search_enabled: 'Web Search Enabled',
      web_search_disabled: 'Web Search Disabled',
      web_search_no_api_key: 'Tavily API key not configured. Please go to Tools Settings to configure it before using web search feature',
      model_switch_success: 'Model switched successfully: {model}',
      model_switch_error: 'Failed to switch model: {error}',
      abort_success: 'Generation stopped',
      abort_error: 'Failed to stop generation: {error}'
    },
    errors: {
      connection_error: 'WebSocket connection error, please check your network or server status',
      connection_closed: 'WebSocket connection closed, please try refreshing the page',
      connection_timeout: 'WebSocket connection timeout, please try again later',
      retry_connecting: 'WebSocket connection timeout, retrying ({count}/{max})...',
      server_connection_failed: 'Failed to connect to server, please check your network or server status'
    }
  },
  about: {
    title: 'About',
    subtitle: 'Learn about Kun-Lab application',
    tabs: {
      app: 'Application',
      license: 'License',
      changelog: 'Changelog'
    },
    appInfo: {
      title: 'Application Introduction',
      description: 'Kun-Lab is a lightweight AI chat application based on Ollama',
      details: 'Application Details',
      developer: 'Development Team',
      developerText: 'Zack、Benny',
      website: 'Official Website',
      websiteText: 'lab.kunpuai.com',
      email: 'Support Email',
      github: 'GitHub Community',
      githubText: 'github.com/bahamutww/kun-lab.git',
      versionInfo: 'Version Information',
      version: 'Current Version',
      versionDesc: 'Current application version',
      electronVersion: 'Electron Version',
      electronVersionDesc: 'The version of Electron framework used by the application',
      lastCheck: 'Last Update Check',
      lastCheckDesc: 'Time of the last update check',
      never: 'Never',
      checkNow: 'Check for Updates',
      checking: 'Checking for updates...',
      checkUpdate: 'Check for Updates',
      updateSettings: 'Update Settings',
      autoCheck: 'Auto-check for Updates',
      autoCheckDesc: 'Automatically check for updates at the specified time',
      checkFrequency: 'Check Frequency',
      checkFrequencyDesc: 'Set the frequency for automatic update checks',
      frequency: {
        startup: 'At Startup',
        daily: 'Daily',
        weekly: 'Weekly',
        monthly: 'Monthly'
      },
      updateStatus: 'Update Status',
      upToDate: 'Up to date',
      updateAvailable: 'New version available: v{version}',
      downloading: 'Downloading update: {progress}%',
      readyToInstall: 'Update ready to install',
      updateError: 'Update error: {error}',
      downloadNow: 'Download Now',
      installNow: 'Install Now',
      downloadFailed: 'Failed to download update',
      checkFailed: 'Failed to check for updates',
      downloadSuccess: 'Update downloaded successfully',
      installSuccess: 'Update installed successfully',
      installFailed: 'Failed to install update',
      cancelInstall: 'Cancel Install',
      installCancelled: 'Install cancelled',
      retryDownload: 'Retry Download',
      noUpdates: 'No updates available',
      noRelease: 'No published versions',
      checkingFailed: 'Failed to check for updates, please try again later'
    },
    license: {
      title: 'License Information',
      loading: 'Loading license information...',
      error: 'Failed to load license information'
    },
    changelog: {
      title: 'Changelog',
      description: 'View the latest updates and improvements to Kun-Lab',
      viewOnGithub: 'View full changelog on GitHub',
      loading: 'Loading changelog...',
      error: 'Failed to load changelog'
    }
  }
};

export default messages;
