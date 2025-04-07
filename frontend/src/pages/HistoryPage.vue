<template>
  <MainLayout>
    <div class="history-page">
      <div class="page-header">
        <div class="header-content">
          <div class="title-group">
            <h1 class="main-title">{{ t('history.title') }}</h1>
            <p class="sub-title">{{ t('history.subtitle') }}</p>
          </div>
          <div class="batch-actions" v-if="displayedConversations.length > 0">
            <label class="select-all">
              <input
                type="checkbox"
                :checked="isAllSelected"
                @change="toggleSelectAll"
                :disabled="displayedConversations.length === 0"
              />
              {{ t('history.select_all') }}
            </label>
            <Button
              @click="batchDelete"
              variant="danger"
              size="sm"
              :disabled="selectedChats.length === 0"
            >
              {{ t('history.delete_selected') }} ({{ selectedChats.length }})
            </Button>
          </div>
        </div>
      </div>

      <div class="page-content">
        <!-- 搜索条和批量操作 -->
        <div class="header-actions">
          <div class="search-wrapper">
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              :placeholder="t('history.search_placeholder')"
              @input="handleSearch"
            />
            <MagnifyingGlassIcon class="search-icon" />
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-indicator">
          <DotLoader />
          <p>{{ t('history.loading') }}</p>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class="error-message">
          <p>{{ error }}</p>
          <Button @click="loadConversations" variant="primary">
            {{ t('history.retry') }}
          </Button>
        </div>

        <!-- 对话列表 -->
        <template v-else>
          <p class="conversation-count">{{ t('history.conversation_count', [totalConversations]) }}</p>
          <template v-if="displayedConversations.length > 0">
            <div v-for="(group, category) in groupedConversations" :key="category" class="conversation-group">
              <h2 class="group-title">
                {{ getLocalizedTimeGroup(category) }}
                <span class="group-date">{{ getGroupDateRange(category) }}</span>
              </h2>
              <div class="conversation-list">
                <TransitionGroup name="conversation">
                  <div
                    v-for="chat in group"
                    :key="chat.conversation_id"
                    class="conversation-item"
                  >
                    <div class="conversation-checkbox">
                      <input
                        type="checkbox"
                        :checked="selectedChats.includes(chat.conversation_id)"
                        @change="toggleSelect(chat.conversation_id)"
                      />
                    </div>
                    <div class="conversation-content">
                      <h3 class="conversation-title">{{ chat.title || t('history.conversation.untitled') }}</h3>
                      <p class="conversation-message">{{ getLastMessage(chat) }}</p>
                      <div class="conversation-footer">
                        <span class="conversation-time">{{ getConversationTime(chat) }}</span>
                        <div class="conversation-actions">
                          <Button
                            @click="openChat(chat.conversation_id)"
                            variant="primary"
                            size="sm"
                          >
                            {{ t('history.conversation.continue_chat') }}
                          </Button>
                          <Button
                            @click="deleteChat(chat.conversation_id)"
                            variant="ghost"
                            size="sm"
                            class="delete-button"
                          >
                            <TrashIcon class="h-5 w-5" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </TransitionGroup>
              </div>
            </div>
          </template>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <img 
              src="@/assets/illustration/chathistoryempty.png" 
              alt="No chat history"
              class="empty-state-image"
            />
            <h3 class="empty-title">{{ t('history.empty_state.title') }}</h3>
            <Button
              variant="secondary"
              size="lg"
              @click="$router.push('/chat')"
            >
              {{ t('history.empty_state.start_chat') }}
            </Button>
          </div>
        </template>
      </div>
    </div>
  </MainLayout>
  
  <!-- 删除确认对话框 -->
  <Dialog
    v-model="showDeleteDialog"
    :title="t('history.delete_dialog.title')"
    :confirmText="t('common.actions.delete')"
    :cancelText="t('common.actions.cancel')"
    @confirm="confirmDelete"
  >
    <p class="text-gray-600 dark:text-gray-300">{{ deleteDialogMessage }}</p>
  </Dialog>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { chatApi } from '@/api/chat'
import { useConversation } from '@/hooks/chat/useConversation'
import { MagnifyingGlassIcon, TrashIcon, ChatBubbleLeftRightIcon } from '@heroicons/vue/24/outline'
import MainLayout from '@/layouts/MainLayout.vue'
import Button from '@/components/common/Button.vue'
import Dialog from '@/components/common/Dialog.vue'
import DotLoader from '@/components/common/DotLoader.vue'
import { useNotificationStore } from '@/stores/notification'
import { useLocalization } from '@/i18n/composables'

const router = useRouter()
const { conversations, loading, error, loadConversations, deleteConversation } = useConversation()
const notificationStore = useNotificationStore()
const { t, language } = useLocalization()
const showDeleteDialog = ref(false)
const deleteDialogMessage = ref('')
const pendingDeleteIds = ref([])
const conversationLastMessages = ref({});
const loadingMessages = ref({});


const searchQuery = ref('')
const selectedChats = ref([])

// 是否全选
const isAllSelected = computed(() => {
  return displayedConversations.value.length > 0 && 
         selectedChats.value.length === displayedConversations.value.length
})

// 计算要显示的对话记录
const displayedConversations = computed(() => {
  if (!searchQuery.value.trim()) {
    return conversations.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return conversations.value.filter(chat => {
    // 检查标题
    const titleMatch = chat.title?.toLowerCase().includes(query) || false
    
    // 检查最后一条AI消息
    const lastMessage = conversationLastMessages.value[chat.conversation_id] || ''
    const messageMatch = lastMessage.toLowerCase().includes(query)
    
    // 返回标题或消息内容匹配的对话
    return titleMatch || messageMatch
  })
})

// 计算对话总数
const totalConversations = computed(() => conversations.value.length)

// 对话按时间分组
const groupedConversations = computed(() => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const threeDaysAgo = new Date(today)
  threeDaysAgo.setDate(threeDaysAgo.getDate() - 3)
  const oneWeekAgo = new Date(today)
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)

  const groups = {
    '今天': [],
    '昨天': [],
    '三天内': [],
    '上周': [],
    '更早': []
  }

  displayedConversations.value.forEach(chat => {
    // 添加时区调整
    const originalDate = new Date(chat.created_at);
    const chatDate = new Date(originalDate.getTime() + 8 * 60 * 60 * 1000);
    
    if (chatDate >= today) {
      groups['今天'].push(chat)
    } else if (chatDate >= yesterday) {
      groups['昨天'].push(chat)
    } else if (chatDate >= threeDaysAgo) {
      groups['三天内'].push(chat)
    } else if (chatDate >= oneWeekAgo) {
      groups['上周'].push(chat)
    } else {
      groups['更早'].push(chat)
    }
  })

  // 只返回有内容的分组
  return Object.fromEntries(
    Object.entries(groups).filter(([_, chats]) => chats.length > 0)
  )
})

// 获取本地化的时间分组名称
function getLocalizedTimeGroup(category) {
  const timeGroupMap = {
    '今天': 'history.time_groups.today',
    '昨天': 'history.time_groups.yesterday',
    '三天内': 'history.time_groups.three_days',
    '上周': 'history.time_groups.last_week',
    '更早': 'history.time_groups.earlier'
  }
  return t(timeGroupMap[category] || category)
}

// 获取分组的日期范围
function getGroupDateRange(category) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  switch(category) {
    case '今天':
      return formatGroupDate(today);
    case '昨天': {
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      return formatGroupDate(yesterday);
    }
    case '三天内': {
      const threeDaysAgo = new Date(today);
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
      return `${formatGroupDate(threeDaysAgo)} ${t('history.time_groups.to')} ${formatGroupDate(today)}`;
    }
    case '上周': {
      const oneWeekAgo = new Date(today);
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      return `${formatGroupDate(oneWeekAgo)} ${t('history.time_groups.to')} ${formatGroupDate(yesterday)}`;
    }
    case '更早': {
      const oneMonthAgo = new Date(today);
      oneMonthAgo.setDate(oneMonthAgo.getDate() - 30);
      return `${formatGroupDate(oneMonthAgo)} ${t('history.time_groups.and_earlier')}`;
    }
    default:
      return '';
  }
}

// 获取对话的创建时间
function getConversationTime(conversation) {
  return formatTime(conversation.created_at)
}

// 获取对话的创建日期
function getConversationDate(conversation) {
  return formatDate(conversation.created_at)
}

// 在组件挂载时加载对话列表
onMounted(async () => {
  await loadConversations();
  // 加载完对话列表后，获取每个对话的最后消息
  loadLastMessages();
});

// 监听对话列表变化，重新加载最后消息
watch(conversations, () => {
  loadLastMessages();
}, { deep: true });


// 监听对话列表变化，重新加载最后消息
watch(conversations, () => {
  loadLastMessages();
}, { deep: true });

// 加载每个对话的最后消息
async function loadLastMessages() {
  for (const chat of conversations.value) {
    if (loadingMessages.value[chat.conversation_id]) continue;
    
    loadingMessages.value[chat.conversation_id] = true;
    try {
      const conversation = await chatApi.getConversation(chat.conversation_id);
      
      if (conversation && conversation.messages && conversation.messages.length > 0) {
        // 查找最后一条AI消息
        const aiMessages = conversation.messages.filter(msg => msg.role === 'assistant');
        if (aiMessages.length > 0) {
          const lastAiMessage = aiMessages[aiMessages.length - 1];
          conversationLastMessages.value[chat.conversation_id] = lastAiMessage.content;
        }
      }
    } catch (error) {
      console.error(`获取对话 ${chat.conversation_id} 的消息失败:`, error);
    } finally {
      loadingMessages.value[chat.conversation_id] = false;
    }
  }
}

// 获取最后一条消息
function getLastMessage(chat) {
  const lastMessage = conversationLastMessages.value[chat.conversation_id];
  
  if (loadingMessages.value[chat.conversation_id]) {
    return t('history.conversation.loading_message') || '加载中...';
  }
  
  if (!lastMessage) {
    return t('history.conversation.no_ai_response') || '暂无AI回复';
  }
  
  // 截取内容（最多显示50个字符，多余的用...表示）
  if (lastMessage.length <= 50) {
    return lastMessage;
  } else {
    return lastMessage.substring(0, 50) + '...';
  }
}

// 切换选择单个对话
function toggleSelect(chatId) {
  const index = selectedChats.value.indexOf(chatId)
  if (index === -1) {
    selectedChats.value.push(chatId)
  } else {
    selectedChats.value.splice(index, 1)
  }
}

// 切换全选
function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedChats.value = []
  } else {
    selectedChats.value = displayedConversations.value.map(chat => chat.conversation_id)
  }
}

// 批量删除对话
async function batchDelete() {
  if (selectedChats.value.length === 0) return
  
  showDeleteDialog.value = true
  deleteDialogMessage.value = t('history.delete_dialog.confirm_multiple', [selectedChats.value.length])
  pendingDeleteIds.value = [...selectedChats.value]
}

// 打开聊天
async function openChat(chatId) {
  const chat = conversations.value.find(c => c.conversation_id === chatId)
  if (chat) {
    router.push(`/chat/${chatId}`)
  }
}

// 删除聊天
async function deleteChat(chatId) {
  showDeleteDialog.value = true
  deleteDialogMessage.value = t('history.delete_dialog.confirm_single', [chatId])
  pendingDeleteIds.value = [chatId]
}

// 确认删除
async function confirmDelete() {
  try {
    for (const chatId of pendingDeleteIds.value) {
      await deleteConversation(chatId)
    }
    
    if (pendingDeleteIds.value.length === 1) {
      notificationStore.addNotification(t('history.delete_dialog.success_single'), 'SUCCESS')
    } else {
      notificationStore.addNotification(t('history.delete_dialog.success_multiple', [pendingDeleteIds.value.length]), 'SUCCESS')
    }
    
    // 清空选中的对话
    selectedChats.value = selectedChats.value.filter(id => !pendingDeleteIds.value.includes(id))
  } catch (e) {
    notificationStore.addNotification(t('history.delete_dialog.error'), 'ERROR')
  } finally {
    showDeleteDialog.value = false
    pendingDeleteIds.value = []
  }
}

// 格式化时间
function formatTime(dateStr) {
  // 记录原始输入以便调试
  console.debug('原始日期字符串:', dateStr);
  
  // 尝试更可靠的日期解析方式
  let date;
  try {
    // 如果是ISO格式字符串，直接解析
    date = new Date(dateStr);
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      console.error('无效日期:', dateStr);
      return '--:--';
    }
    
    // 添加时区调整（如果数据库时间与本地时间有固定偏差）
    // 假设数据库时间比本地时间慢8小时（根据实际情况调整）
    const adjustedDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
    
    console.debug('调整前的日期对象:', date.toLocaleString());
    console.debug('调整后的日期对象:', adjustedDate.toLocaleString());
    
    // 使用调整后的日期
    date = adjustedDate;
  } catch (error) {
    console.error('日期解析错误:', error);
    return '--:--';
  }
  
  // 使用本地时区的小时和分钟
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  
  // 根据语言环境决定是否使用12小时制
  if (language.value.startsWith('zh')) {
    // 中文环境使用24小时制
    return `${hours}:${minutes}`;
  } else {
    // 英文环境使用12小时制
    const hour12 = hours % 12 || 12;
    const ampm = hours >= 12 ? 'PM' : 'AM';
    return `${hour12}:${minutes} ${ampm}`;
  }
}

// 格式化分组日期
function formatGroupDate(date) {
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    console.error('Invalid date object')
    return '--/--'
  }
  
  // 添加时区调整（保持与formatTime一致）
  const adjustedDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
  
  const month = adjustedDate.getMonth() + 1
  const day = adjustedDate.getDate()
  
  // 根据语言环境返回不同格式
  if (language.value.startsWith('zh')) {
    return `${month}月${day}日`
  } else {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return `${monthNames[month-1]} ${day}`
  }
}
</script>

<style scoped>
@import '@/styles/HistoryPage.css';
</style>