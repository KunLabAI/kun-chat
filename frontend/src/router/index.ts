import { createRouter, createWebHistory } from 'vue-router'
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
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/pages/NotFoundPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
