import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/pages/RegisterPage.vue')
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/pages/ForgotPasswordPage.vue'),
    meta: {
      requiresAuth: false,
      title: '忘记密码'
    }
  },
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/pages/ChatPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat/:conversationId',
    name: 'chat-conversation',
    component: () => import('@/pages/ChatPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/models',
    name: 'models',
    component: () => import('@/pages/ModelsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/models/custom',
    name: 'model-custom',
    component: () => import('@/pages/ModelCustomPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/models/pull',
    name: 'model-pull',
    component: () => import('@/pages/PullModelPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/models/:id',
    name: 'model-detail',
    component: () => import('@/pages/ModelDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/prompts',
    name: 'prompts',
    component: () => import('@/pages/PromptsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/prompts/create',
    name: 'createPrompt',
    component: () => import('@/pages/CreatePromptPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/prompts/:id/edit',
    name: 'editPrompt',
    component: () => import('@/pages/CreatePromptPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notes',
    name: 'notes',
    component: () => import('@/pages/NotesPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/create',
    name: 'createNote',
    component: () => import('@/pages/CreateNotePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notes/:id/edit',
    name: 'editNote',
    component: () => import('@/pages/CreateNotePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/pages/HistoryPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/account-settings',
    name: 'accountSettings',
    component: () => import('@/pages/AccountSettingsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/features-settings',
    name: 'featuresSettings',
    component: () => import('@/pages/FeaturesSettingsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/pages/AboutPage.vue'),
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果是需要认证的页面
  if (to.meta.requiresAuth) {
    // 检查是否已认证
    if (authStore.isAuthenticated) {
      next()
      return
    }
    
    // 如果未认证，检查是否有最后登录的用户
    const lastLoggedUser = localStorage.getItem('kunlab_last_user')
    // 根据最后登录用户获取对应token
    const token = lastLoggedUser 
      ? localStorage.getItem(`kunlab_user_token_${lastLoggedUser}`) 
      : null
    
    if (!token) {
      next('/login')
      return
    }
    
    // 尝试获取用户信息来验证token是否有效
    try {
      await authStore.fetchUserInfo()
      next()
    } catch (error) {
      // 如果获取用户信息失败，说明token无效
      if (lastLoggedUser) {
        localStorage.removeItem(`kunlab_user_token_${lastLoggedUser}`)
      }
      next('/login')
    }
  } else {
    // 如果已经登录，访问登录/注册页面时重定向到首页
    if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      next('/')
    } else {
      next()
    }
  }
})

export default router
