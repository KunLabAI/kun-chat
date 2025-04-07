<template>
  <div>
    <!-- 小屏幕下的侧边栏触发区域 -->
    <div class="sidebar-trigger-area" 
         v-if="isMobileView" 
         @mouseenter="showSidebar = true"></div>

    <!-- 侧边栏 -->
    <aside class="sidebar" 
           :class="{ 'sidebar-mobile-hidden': isMobileView && !showSidebar }"
           @mouseleave="isMobileView && (showSidebar = false)">
      <!-- Logo -->
      <div class="logo-section">
        <img src="@/assets/kun-lab_logo.svg" class="logo-icon" :data-tooltip="t('sidebar.logo_tooltip')" @mouseenter="updateTooltipPosition" alt="kun-lab logo" />
      </div>

      <!-- Navigation -->
      <nav class="nav-section">
        <div class="nav-group">
          <template v-if="!authStore.isAuthenticated">
            <RouterLink to="/login" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.login')" @mouseenter="updateTooltipPosition">
              <img src="@/assets/icons/sys_user.svg" class="icon" :class="{ 'active': isActive }" />
            </RouterLink>
            <RouterLink to="/register" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.register')" @mouseenter="updateTooltipPosition">
              <img src="@/assets/icons/sys_safe.svg" class="icon" :class="{ 'active': isActive }" />
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
            <RouterLink to="/notes" class="nav-item" v-slot="{ isActive }" :data-tooltip="t('sidebar.notes')" @mouseenter="updateTooltipPosition">
              <img src="@/assets/icons/sys_note.svg" class="icon" :class="{ 'active': isActive }" />
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
              <img src="@/assets/icons/sys_accountsettings.svg" class="menu-icon" />
              <span>{{ t('sidebar.account_settings') }}</span>
            </RouterLink>
            <RouterLink to="/features-settings" class="menu-item" @click="closeUserMenu">
              <img src="@/assets/icons/sys_systemsettings.svg" class="menu-icon" />
              <span>{{ t('sidebar.features_settings') }}</span>
            </RouterLink>
            <a href="https://lab.kunpuai.com" target="_blank" class="menu-item" @click="closeUserMenu">
              <img src="@/assets/icons/sys_community.svg" class="menu-icon" />
              <span>{{ t('sidebar.community') }}</span>
            </a>
            <a href="https://github.com/bahamutww/kun-lab.git" target="_blank" class="menu-item" @click="closeUserMenu">
              <img src="@/assets/icons/sys_help.svg" class="menu-icon" />
              <span>{{ t('sidebar.help_docs') }}</span>
            </a>
            <RouterLink to="/about" class="menu-item" @click="closeUserMenu">
              <img src="@/assets/icons/sys_info.svg" class="menu-icon" />
              <span>{{ t('sidebar.about') }}</span>
            </RouterLink>
            <button @click="handleLogout" class="menu-item logout">
              <img src="@/assets/icons/sys_logout.svg" class="menu-icon" />
              <span>{{ t('sidebar.logout') }}</span>
            </button>
          </div>
        </div>
      </Teleport>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
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

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()
const modelsStore = useModelsStore()
const notificationStore = useNotificationStore()
const { createConversation, loadConversations, conversations } = useConversation()
const { t } = useLocalization()

const showUserMenu = ref(false)
const userMenuStyle = ref({})
const isMobileView = ref(false)
const showSidebar = ref(false)

// 检测屏幕尺寸
function checkScreenSize() {
  isMobileView.value = window.innerWidth < 768
  // 如果不是移动视图，确保侧边栏显示
  if (!isMobileView.value) {
    showSidebar.value = true
  } else {
    // 移动视图默认隐藏侧边栏
    showSidebar.value = false
  }
}

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
  // 使用本地静态资源
  return new URL('../assets/default-avatar.jpg', import.meta.url).href
})

// 处理ESC键关闭菜单
function handleEscKey(event) {
  if (event.key === 'Escape' && showUserMenu.value) {
    closeUserMenu()
  }
}

// 在组件挂载时添加ESC键监听和窗口大小变化监听
onMounted(() => {
  document.addEventListener('keydown', handleEscKey)
  window.addEventListener('resize', checkScreenSize)
  // 初始检查屏幕尺寸
  checkScreenSize()
})

// 在组件卸载时移除ESC键监听和窗口大小变化监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleEscKey)
  window.removeEventListener('resize', checkScreenSize)
})

// 当路由变化时关闭侧边栏（在移动视图下）
watch(() => router.currentRoute.value.path, () => {
  if (isMobileView.value) {
    showSidebar.value = false
  }
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
        await modelsStore.fetchModels()
      }
      
      // 尝试获取默认模型
      if (modelsStore.models.length > 0) {
        // 查找默认模型或使用第一个可用模型
        defaultModel = modelsStore.models.find(model => model.is_default) || modelsStore.models[0]
      }
    } catch (error) {
      console.error('获取模型失败:', error)
      notificationStore.showNotification({
        type: 'error',
        title: t('notifications.error'),
        message: t('notifications.fetch_models_failed')
      })
    }
    
    // 创建新对话
    try {
      const modelId = defaultModel ? defaultModel.id : null
      const newConversation = await createConversation(modelId)
      
      // 设置当前对话并导航到对话页面
      chatStore.setCurrentConversation(newConversation.conversation_id)
      router.push(`/chat/${newConversation.conversation_id}`)
    } catch (error) {
      console.error('创建对话失败:', error)
      notificationStore.showNotification({
        type: 'error',
        title: t('notifications.error'),
        message: t('notifications.create_conversation_failed')
      })
    }
  } catch (error) {
    console.error('导航到聊天页面失败:', error)
    notificationStore.showNotification({
      type: 'error',
      title: t('notifications.error'),
      message: t('notifications.navigation_failed')
    })
  }
}

// 处理提示框位置
function updateTooltipPosition(event) {
  const target = event.currentTarget
  if (!target) return
  
  // 获取元素相对于视口的位置
  const rect = target.getBoundingClientRect()
  // 设置提示框的垂直位置
  target.style.setProperty('--tooltip-y', rect.top + rect.height / 2 + 'px')
}
</script>

<style scoped>
@import '@/components/Sidebar.css'
</style>