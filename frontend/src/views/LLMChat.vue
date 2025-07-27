<!-- LLMChat.vue -->
<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-6 space-y-6">
    <!-- Header -->
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-jade drop-shadow glow">💬 Chat with Jade</h1>
      <p class="text-cyan-400 mt-2">Your offline AI assistant with memory & tool execution</p>
      <div class="mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-jade-500/10 text-jade-400 border border-jade-500/30">
        RAG + Tool Execution
      </div>
      <!-- Keyboard Shortcuts Help -->
      <div class="mt-4 flex items-center justify-center gap-4 text-sm text-jade-600">
        <span><kbd class="px-2 py-1 bg-backdrop-light rounded border border-jade-500/30">/</kbd> Focus input</span>
        <span><kbd class="px-2 py-1 bg-backdrop-light rounded border border-jade-500/30">↑</kbd> Edit last</span>
        <span><kbd class="px-2 py-1 bg-backdrop-light rounded border border-jade-500/30">Shift + ↵</kbd> New line</span>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid lg:grid-cols-4 gap-6">
      <!-- Chat Area (3/4) -->
      <div class="lg:col-span-3">
        <div class="card-glass flex flex-col h-[65vh]">
          <!-- Messages Area -->
          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Welcome Message -->
            <div v-if="store.messages.length === 0" class="text-center py-12">
              <div class="text-6xl mb-6 animate-pulse">🧠</div>
              <h3 class="text-2xl font-bold text-jade mb-4">Welcome to Jade Assistant!</h3>
              <p class="text-cyan-400 mb-8">Ask me anything about your synced files, tools, or tenant data.</p>
              <div class="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
                <button
                  v-for="suggestion in chatSuggestions"
                  :key="suggestion"
                  class="btn-secondary text-sm"
                  @click="sendMessage(suggestion)"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>

            <!-- Chat Messages -->
            <template v-for="message in store.messages" :key="message.id">
              <!-- User Message -->
              <div v-if="message.type === 'user'" class="flex justify-end">
                <div class="max-w-[80%]">
                  <div class="bg-jade-500/20 text-white px-6 py-3 rounded-2xl rounded-br-sm">
                    <p class="whitespace-pre-wrap">{{ message.content }}</p>
                  </div>
                  <div class="text-xs text-jade-400 mt-2 text-right">
                    {{ formatTime(message.timestamp) }}
                  </div>
                </div>
              </div>

              <!-- AI Message -->
              <div v-else class="flex justify-start">
                <div class="max-w-[85%]">
                  <div class="flex items-start gap-4">
                    <!-- Avatar -->
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-jade-500 to-jade-700 flex items-center justify-center shadow-glow">
                      <span class="text-lg">🤖</span>
                    </div>

                    <!-- Message Content -->
                    <div class="flex-1">
                      <div class="bg-backdrop-light backdrop-blur-sm px-6 py-4 rounded-2xl rounded-tl-sm border border-jade-500/30">
                        <!-- Loading State -->
                        <div v-if="message.loading" class="flex items-center gap-3">
                          <div class="w-2 h-2 rounded-full bg-jade-500 animate-pulse"></div>
                          <div class="w-2 h-2 rounded-full bg-jade-500 animate-pulse" style="animation-delay: 0.2s"></div>
                          <div class="w-2 h-2 rounded-full bg-jade-500 animate-pulse" style="animation-delay: 0.4s"></div>
                          <span class="text-jade-400 ml-2">Jade is thinking...</span>
                        </div>

                        <!-- Message Content -->
                        <div v-else>
                          <div class="prose prose-invert max-w-none">
                            <div v-html="message.content"></div>
                          </div>

                          <!-- Sources -->
                          <div v-if="message.sources?.length" class="mt-4 pt-4 border-t border-jade-500/30">
                            <h4 class="text-sm font-medium text-jade-300 mb-3 flex items-center gap-2">
                              <span>📚</span> Sources ({{ message.sources.length }})
                            </h4>
                            <div class="space-y-3">
                              <div
                                v-for="(source, index) in message.sources"
                                :key="index"
                                class="bg-backdrop rounded-lg border border-jade-500/20 p-4"
                              >
                                <div class="flex items-start justify-between mb-2">
                                  <div class="flex items-center gap-2">
                                    <span class="text-sm font-medium text-jade-400">
                                      {{ getFileIcon(source.metadata?.source_file || source.document_id) }}
                                      Source {{ index + 1 }}
                                    </span>
                                    <span class="text-xs bg-jade-500/20 text-jade-300 px-2 py-0.5 rounded-full">
                                      {{ (source.similarity_score * 100).toFixed(1) }}% match
                                    </span>
                                  </div>
                                  <button
                                    class="text-jade-400 hover:text-jade-300 transition-colors"
                                    @click="showSourceDetails(source)"
                                    :title="getFileTypeDescription(source.metadata?.source_file || source.document_id)"
                                  >
                                    <span class="text-sm">👁️ View</span>
                                  </button>
                                </div>
                                <p class="text-sm text-gray-300 line-clamp-2">
                                  {{ source.content.substring(0, 200) }}...
                                </p>
                                <div v-if="source.metadata" class="mt-2 text-xs text-jade-600">
                                  {{ getFileIcon(source.metadata.source_file || source.document_id) }}
                                  {{ source.metadata.source_file || source.document_id }}
                                </div>
                              </div>
                            </div>
                          </div>

                          <!-- Query Info -->
                          <div v-if="message.queryInfo" class="mt-3 pt-3 border-t border-jade-500/30">
                            <div class="flex items-center gap-4 text-xs text-jade-600">
                              <span>⏱️ {{ message.queryInfo.execution_time?.toFixed(3) }}s</span>
                              <span>🧠 {{ message.queryInfo.llm_used || 'AI Model' }}</span>
                              <span>📊 {{ message.queryInfo.total_sources }} sources</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="text-xs text-jade-600 mt-2">
                        {{ formatTime(message.timestamp) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <!-- Input Area -->
          <div class="border-t border-jade-500/30 p-6 bg-backdrop-light backdrop-blur-sm">
            <div class="flex gap-4">
              <div class="flex-1">
                <textarea
                  ref="chatInput"
                  v-model="currentMessage"
                  :placeholder="isEditing ? 'Editing previous message...' : 'Ask Jade anything... (/ to focus)'"
                  class="w-full bg-backdrop border border-jade-500/30 rounded-xl px-4 py-3 resize-none focus:ring-2 focus:ring-jade-500 focus:border-transparent text-white placeholder-jade-600"
                  :class="{ 'border-yellow-500/30 focus:ring-yellow-500': isEditing }"
                  rows="2"
                  :disabled="store.isLoading"
                  @keydown.enter.prevent="handleEnter"
                />
              </div>
              <div class="flex flex-col gap-2">
                <button
                  :disabled="!currentMessage.trim() || store.isLoading"
                  class="btn-primary h-full"
                  @click="sendMessage()"
                >
                  <span v-if="store.isLoading" class="animate-spin">⏳</span>
                  <span v-else-if="isEditing">✏️</span>
                  <span v-else>🚀</span>
                  {{ store.isLoading ? 'Thinking...' : (isEditing ? 'Update' : 'Send') }}
                </button>
                <button
                  v-if="isEditing"
                  class="btn-secondary"
                  @click="cancelEdit"
                >
                  Cancel Edit
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar (1/4) -->
      <div class="lg:col-span-1 space-y-6">
        <!-- Recent Questions -->
        <div class="card-glass">
          <h3 class="text-lg font-bold text-jade-300 mb-4 flex items-center gap-2">
            <span>📝</span> Recent Questions
          </h3>
          <div v-if="store.recentQuestions.length === 0" class="text-jade-600 text-sm">
            No recent questions yet
          </div>
          <div v-else class="space-y-2">
            <button
              v-for="question in store.recentQuestions.slice(0, 5)"
              :key="question.id"
              class="w-full text-left p-3 bg-backdrop-light hover:bg-jade-500/10 rounded-lg text-sm transition-colors border border-jade-500/20"
              @click="sendMessage(question.query)"
            >
              <div class="font-medium text-jade-300 truncate">
                {{ question.query }}
              </div>
              <div class="text-xs text-jade-600 mt-1">
                {{ formatTime(question.timestamp) }}
              </div>
            </button>
          </div>
        </div>

        <!-- Chat Statistics -->
        <div class="card-glass">
          <h3 class="text-lg font-bold text-jade-300 mb-4 flex items-center gap-2">
            <span>📊</span> Chat Statistics
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-jade-400">Questions Asked:</span>
              <span class="font-semibold text-jade">{{ store.chatStats.totalQuestions }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-jade-400">Avg Response Time:</span>
              <span class="font-semibold text-jade">{{ store.chatStats.avgResponseTime }}s</span>
            </div>
            <div class="flex justify-between">
              <span class="text-jade-400">Sources Found:</span>
              <span class="font-semibold text-jade">{{ store.chatStats.totalSources }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-jade-400">Session Time:</span>
              <span class="font-semibold text-jade">{{ store.sessionTime }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card-glass">
          <h3 class="text-lg font-bold text-jade-300 mb-4 flex items-center gap-2">
            <span>⚡</span> Quick Actions
          </h3>
          <div class="space-y-2">
            <button
              v-for="action in quickActions"
              :key="action.text"
              class="w-full btn-secondary text-sm justify-start"
              @click="sendMessage(action.text)"
            >
              <span>{{ action.icon }}</span>
              <span>{{ action.text }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Source Details Modal -->
    <div v-if="store.selectedSource" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="card-glass max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Modal Header -->
        <div class="p-6 border-b border-jade-500/30">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-jade">
              📄 Source Details - {{ store.selectedSource.document_id }}
            </h3>
            <button
              class="text-jade-400 hover:text-jade-300 transition-colors text-2xl"
              @click="store.setSelectedSource(null)"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Modal Content -->
        <div class="p-6 overflow-y-auto flex-1">
          <!-- Source Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div class="bg-backdrop-light rounded-lg p-4 border border-jade-500/20">
              <h4 class="font-bold text-jade-300 mb-2">📊 Source Info</h4>
              <div class="space-y-2 text-sm">
                <div><span class="text-jade-400">Document ID:</span> {{ store.selectedSource.document_id }}</div>
                <div><span class="text-jade-400">Similarity Score:</span> {{ (store.selectedSource.similarity_score * 100).toFixed(2) }}%</div>
                <div><span class="text-jade-400">Chunk Index:</span> {{ store.selectedSource.chunk_index }}</div>
                <div v-if="store.selectedSource.metadata">
                  <span class="text-jade-400">Source File:</span> {{ store.selectedSource.metadata.source_file || 'Unknown' }}
                </div>
              </div>
            </div>

            <div v-if="store.selectedSource.metadata" class="bg-backdrop-light rounded-lg p-4 border border-jade-500/20">
              <h4 class="font-bold text-jade-300 mb-2">📋 Metadata</h4>
              <div class="space-y-2 text-sm">
                <div v-for="(value, key) in store.selectedSource.metadata" :key="key">
                  <span class="text-jade-400">{{ key }}:</span> {{ value }}
                </div>
              </div>
            </div>
          </div>

          <!-- Full Content -->
          <div class="mb-6">
            <h4 class="font-bold text-jade-300 mb-2">📄 Full Content</h4>
            <div class="bg-backdrop-light rounded-lg p-4 border border-jade-500/20 max-h-96 overflow-y-auto">
              <pre class="whitespace-pre-wrap text-sm text-gray-300">{{ store.selectedSource.content }}</pre>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="p-6 border-t border-jade-500/30">
          <div class="flex justify-end gap-4">
            <button class="btn-secondary" @click="copySourceContent(store.selectedSource)">
              📋 Copy Content
            </button>
            <button class="btn-primary" @click="store.setSelectedSource(null)">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useJadeStore } from '@/store/useJadeStore'
import { getFileIcon, getFileTypeDescription } from '@/utils/fileIcons'

// Store
const store = useJadeStore()
const currentMessage = ref('')
const chatInput = ref(null)
const isEditing = ref(false)
const editingMessageId = ref(null)

// Chat suggestions
const chatSuggestions = [
  'What are our security policies?',
  'Show me tenant information',
  'What compliance requirements do we have?',
  'Explain our data processing procedures'
]

// Quick actions
const quickActions = [
  { icon: '🔒', text: 'What are our security policies?' },
  { icon: '👥', text: 'Show me tenant information' },
  { icon: '📋', text: 'What compliance requirements do we have?' },
  { icon: '📊', text: 'Explain our data processing procedures' }
]

// Keyboard shortcuts
function handleKeyDown(e) {
  // Focus input on '/' (unless already in an input/textarea)
  if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
    e.preventDefault()
    focusInput()
  }

  // Edit last message on ↑ (when input is empty)
  if (e.key === 'ArrowUp' && currentMessage.value === '' && !isEditing.value) {
    e.preventDefault()
    editLastMessage()
  }

  // Cancel editing on Escape
  if (e.key === 'Escape' && isEditing.value) {
    e.preventDefault()
    cancelEdit()
  }
}

// Input focus
function focusInput() {
  chatInput.value?.focus()
}

// Message editing
function editLastMessage() {
  const userMessages = store.messages.filter(m => m.type === 'user')
  if (userMessages.length > 0) {
    const lastMessage = userMessages[userMessages.length - 1]
    currentMessage.value = lastMessage.content
    editingMessageId.value = lastMessage.id
    isEditing.value = true
    focusInput()
    store.addToast('Editing previous message', 'info')
  }
}

function cancelEdit() {
  currentMessage.value = ''
  editingMessageId.value = null
  isEditing.value = false
}

// Methods
const handleEnter = (event) => {
  if (event.shiftKey) return // Allow new line with Shift+Enter
  event.preventDefault() // Prevent default to avoid newline
  sendMessage()
}

const sendMessage = async (messageText = null) => {
  const text = messageText || currentMessage.value.trim()
  if (!text) return

  if (isEditing.value) {
    // Update existing message
    const messageIndex = store.messages.findIndex(m => m.id === editingMessageId.value)
    if (messageIndex !== -1) {
      // Remove the old message and its response
      store.messages.splice(messageIndex, 2)
      store.addToast('Message updated', 'success')
    }
    isEditing.value = false
    editingMessageId.value = null
  }
  
  await store.sendMessage(text)
  currentMessage.value = ''
}

const showSourceDetails = (source) => {
  store.setSelectedSource(source)
}

const copySourceContent = async (source) => {
  try {
    await navigator.clipboard.writeText(source.content)
    store.addToast('Source content copied!', 'success')
  } catch (err) {
    console.error('Failed to copy:', err)
    store.addToast('Failed to copy content', 'error')
  }
}

const formatTime = (timestamp) => {
  try {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Unknown'
  }
}

// Lifecycle
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  @apply w-2;
}

.overflow-y-auto::-webkit-scrollbar-track {
  @apply bg-gray-800;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  @apply bg-jade-600 rounded-full hover:bg-jade-500 transition-colors;
}

/* Line clamp */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Smooth scrolling */
.overflow-y-auto {
  scroll-behavior: smooth;
}

/* Chat bubble corners */
.rounded-br-sm {
  border-bottom-right-radius: 0.125rem;
}

.rounded-tl-sm {
  border-top-left-radius: 0.125rem;
}
</style>
