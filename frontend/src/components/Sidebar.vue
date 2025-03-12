<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="logo-section">
      <span class="logo-icon" :data-tooltip="t('sidebar.logo_tooltip')" @mouseenter="updateTooltipPosition">K</span>
    </div>

    <!-- Navigation -->
    <nav class="nav-section">
      <div class="nav-group">
        <template v-if="!authStore.isAuthenticated">
          <RouterLink to="/login" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.login')" @mouseenter="updateTooltipPosition">
            <UserIcon class="icon" :class="{ 'active': isActive }" />
          </RouterLink>
          <RouterLink to="/register" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.register')" @mouseenter="updateTooltipPosition">
            <UserPlusIcon class="icon" :class="{ 'active': isActive }" />
          </RouterLink>
        </template>
        
        <template v-else>
          <RouterLink to="/" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.home')" @mouseenter="updateTooltipPosition">
            <img src="@/assets/icons/sys_home.svg" class="icon" :class="{ 'active': isActive }" />
          </RouterLink>
          <RouterLink to="/chat" class="nav-item" v-slot="{ isActive }" @click="handleChatNavigation" :data-tooltip="t('sidebar.chat')" @mouseenter="updateTooltipPosition">
            <img src="@/assets/icons/sys_chat.svg" class="icon" :class="{ 'active': isActive }" />
          </RouterLink>
          <RouterLink to="/models" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.models')" @mouseenter="updateTooltipPosition">
            <img src="@/assets/icons/sys_model.svg" class="icon" :class="{ 'active': isActive }" />
          </RouterLink>
          <RouterLink to="/prompts" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.prompts')" @mouseenter="updateTooltipPosition">
            <img src="@/assets/icons/sys_prompts.svg" class="icon" :class="{ 'active': isActive }" />
          </RouterLink>
        </template>
      </div>

      <div class="nav-group bottom" v-if="authStore.isAuthenticated">
        <RouterLink to="/history" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.history')" @mouseenter="updateTooltipPosition">
          <img src="@/assets/icons/sys_history.svg" class="icon" :class="{ 'active': isActive }" />
        </RouterLink>
        <div class="nav-item user-avatar" @click="toggleUserMenu" :data-tooltip="t('sidebar.user_menu')" @mouseenter="updateTooltipPosition">
          <img :src="userAvatarUrl" class="avatar-img" :alt="t('sidebar.user_avatar')" />
        </div>
      </div>
    </nav>

    <!-- 用户菜单弹窗 -->
    <Teleport to="body">
      <!-- 遮罩层 -->
      <div v-if="showUserMenu" class="menu-overlay" @click="closeUserMenu"></div>
      <!-- 菜单内容 -->
      <div v-if="showUserMenu" 
           class="user-menu" 
           :style="userMenuStyle"
           @click.stop>
        <div class="user-menu-header">
          <img :src="userAvatarUrl" class="menu-avatar" :alt="t('sidebar.user_avatar')" />
          <span class="username">{{ authStore.user?.username || '用户' }}</span>
        </div>
        <div class="menu-items">
          <RouterLink to="/account-settings" class="menu-item" @click="closeUserMenu">
            <Cog6ToothIcon class="menu-icon" />
            <span>{{ t('sidebar.account_settings') }}</span>
          </RouterLink>
          <RouterLink to="/features-settings" class="menu-item" @click="closeUserMenu">
            <WrenchScrewdriverIcon class="menu-icon" />
            <span>{{ t('sidebar.features_settings') }}</span>
          </RouterLink>
          <a href="https://kunpuai.com" target="_blank" class="menu-item" @click="closeUserMenu">
            <UsersIcon class="menu-icon" />
            <span>{{ t('sidebar.community') }}</span>
          </a>
          <a href="https://github.com/kunpuai/kunyuchat" target="_blank" class="menu-item" @click="closeUserMenu">
            <QuestionMarkCircleIcon class="menu-icon" />
            <span>{{ t('sidebar.help_docs') }}</span>
          </a>
          <button @click="handleLogout" class="menu-item logout">
            <ArrowLeftOnRectangleIcon class="menu-icon" />
            <span>{{ t('sidebar.logout') }}</span>
          </button>
        </div>
      </div>
    </Teleport>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { chatApi } from '@/api/chat'
import { API_BASE_URL } from '@/api/config'
import { useConversation } from '@/hooks/chat/useConversation'
import { useModelsStore } from '@/stores/models'
import { useNotificationStore } from '@/stores/notification'
import { useLocalization } from '@/i18n/composables'
import { 
  Cog6ToothIcon, 
  ArrowLeftOnRectangleIcon,
  UserIcon,
  UserPlusIcon,
  UsersIcon,
  QuestionMarkCircleIcon,
  WrenchScrewdriverIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()
const modelsStore = useModelsStore()
const notificationStore = useNotificationStore()
const { createConversation, loadConversations, conversations } = useConversation()
const { t } = useLocalization()

const showUserMenu = ref(false)
const userMenuStyle = ref({})

const userAvatarUrl = computed(() => {
  if (authStore.user?.avatar) {
    // 检查是否是完整URL或相对路径
    if (authStore.user.avatar.startsWith('http')) {
      return authStore.user.avatar
    } else if (authStore.user.avatar.startsWith('/static/')) {
      // 直接使用API_BASE_URL，不需要再添加/api
      return `${API_BASE_URL}${authStore.user.avatar}`
    } else {
      // 添加API基础URL
      return `${API_BASE_URL}${authStore.user.avatar}`
    }
  }
  return `${API_BASE_URL}/static/default-avatar.jpg`
})

// 处理ESC键关闭菜单
function handleEscKey(event) {
  if (event.key === 'Escape' && showUserMenu.value) {
    closeUserMenu()
  }
}

// 在组件挂载时添加ESC键监听
onMounted(() => {
  document.addEventListener('keydown', handleEscKey)
})

// 在组件卸载时移除ESC键监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleEscKey)
})

function toggleUserMenu(event) {
  event.stopPropagation() // 阻止事件冒泡
  showUserMenu.value = !showUserMenu.value
  if (showUserMenu.value) {
    // 获取点击元素的位置信息
    const rect = event.target.closest('.user-avatar').getBoundingClientRect()
    // 获取窗口高度
    const windowHeight = window.innerHeight
    // 计算菜单位置，向上弹出
    userMenuStyle.value = {
      bottom: `${windowHeight - rect.top}px`,
      left: `${rect.right + 8}px`
    }
  }
}

function closeUserMenu() {
  showUserMenu.value = false
}

// 处理退出登录
async function handleLogout() {
  try {
    closeUserMenu()
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}

// 处理聊天导航
async function handleChatNavigation() {
  try {
    // 先获取对话列表
    await loadConversations()
    
    // 检查是否有现有对话
    if (conversations.value.length > 0) {
      // 获取最近的对话（列表已按更新时间排序）
      const latestConversation = conversations.value[0]
      
      // 设置当前对话并导航到对话页面
      chatStore.setCurrentConversation(latestConversation.conversation_id)
      await chatStore.loadConversation(latestConversation.conversation_id)
      router.push(`/chat/${latestConversation.conversation_id}`)
      return
    }
    
    // 如果没有现有对话，则创建新对话
    let defaultModel = null
    
    // 尝试获取模型，但不阻止导航
    try {
      if (!modelsStore.isLoading && modelsStore.models.length === 0) {
        await modelsStore.fetchChatModels()
      }
      defaultModel = modelsStore.models[0]?.name
    } catch (modelError) {
      console.error('获取模型失败:', modelError)
      notificationStore.warning('获取模型列表失败，将使用默认模型')
    }
    
    // 如果没有获取到模型，使用默认值
    if (!defaultModel) {
      defaultModel = 'llama3'  // 使用一个常见的默认模型名称
      notificationStore.info('使用默认模型创建对话')
    }

    // 创建新对话
    const conversation = await createConversation({
      title: '新对话',
      model: defaultModel
    })
    
    if (conversation && conversation.conversation_id) {
      // 设置当前模型并同步到后端
      try {
        await chatStore.setCurrentModel(defaultModel, conversation.conversation_id, true)
      } catch (modelSetError) {
        console.error('设置模型失败:', modelSetError)
        // 继续导航，不阻止用户体验
      }
      
      chatStore.setCurrentConversation(conversation.conversation_id)
      router.push(`/chat/${conversation.conversation_id}`)
    } else {
      throw new Error('创建对话失败：未获取到对话ID')
    }
  } catch (error) {
    console.error('处理聊天导航失败:', error)
    notificationStore.showError(error instanceof Error ? error.message : '处理聊天导航失败')
  }
}

// 处理提示框位置
const updateTooltipPosition = (event) => {
  const target = event.currentTarget;
  const rect = target.getBoundingClientRect();
  target.style.setProperty('--tooltip-y', `${rect.top + rect.height/2}px`);
}
</script>

<style scoped>
@import '@/components/Sidebar.css'
</style>