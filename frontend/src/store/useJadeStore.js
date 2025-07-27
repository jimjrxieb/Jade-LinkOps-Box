import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

// Configure marked for security
marked.setOptions({
  headerIds: false,
  mangle: false
})

// Create a custom renderer that uses our Tailwind classes
const renderer = new marked.Renderer()

// Style code blocks
renderer.code = (code, language) => {
  return `<pre class="bg-backdrop-light p-4 rounded-lg overflow-x-auto my-4"><code class="text-jade-300 font-mono text-sm">${code}</code></pre>`
}

// Style blockquotes
renderer.blockquote = (quote) => {
  return `<blockquote class="border-l-4 border-jade-500/30 pl-4 my-4 text-jade-300 italic">${quote}</blockquote>`
}

// Style links
renderer.link = (href, title, text) => {
  return `<a href="${href}" title="${title || ''}" target="_blank" rel="noopener noreferrer" class="text-jade-400 hover:text-jade-300 underline transition-colors">${text}</a>`
}

marked.use({ renderer })

export const useJadeStore = defineStore('jade', () => {
  // Existing state
  const messages = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const selectedSource = ref(null)
  const recentQuestions = ref([])
  const sessionStartTime = ref(Date.now())

  // Toast state
  const toasts = ref([])
  let toastTimeout = null

  // Chat settings
  const chatSettings = ref({
    top_k: 5,
    similarity_threshold: 0.7,
    include_metadata: true
  })

  // Computed
  const chatStats = computed(() => {
    const questions = messages.value.filter(m => m.type === 'user').length
    const aiResponses = messages.value.filter(m => m.type === 'ai' && !m.loading)
    const totalTime = aiResponses.reduce((sum, m) => sum + (m.queryInfo?.execution_time || 0), 0)
    const avgTime = questions > 0 ? (totalTime / questions).toFixed(3) : '0.000'
    const totalSources = aiResponses.reduce((sum, m) => sum + (m.sources?.length || 0), 0)

    return {
      totalQuestions: questions,
      avgResponseTime: avgTime,
      totalSources: totalSources
    }
  })

  const sessionTime = computed(() => {
    const elapsed = Math.floor((Date.now() - sessionStartTime.value) / 1000)
    const minutes = Math.floor(elapsed / 60)
    const seconds = elapsed % 60
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  })

  // Toast actions
  const addToast = (message, type = 'info', duration = 5000) => {
    const id = Date.now()
    toasts.value.push({ id, message, type })

    // Auto-remove after duration
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  const removeToast = (id) => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  // Message actions
  const sendMessage = async (text) => {
    if (!text || isLoading.value) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: text,
      timestamp: new Date().toISOString()
    }

    const aiMessage = {
      id: Date.now() + 1,
      type: 'ai',
      content: '',
      loading: true,
      timestamp: new Date().toISOString(),
      sources: [],
      queryInfo: null
    }

    messages.value.push(userMessage, aiMessage)
    isLoading.value = true
    error.value = null

    // Add to recent questions
    recentQuestions.value.unshift({
      id: Date.now(),
      query: text,
      timestamp: new Date().toISOString()
    })

    // Keep only last 10 recent questions
    if (recentQuestions.value.length > 10) {
      recentQuestions.value = recentQuestions.value.slice(0, 10)
    }

    try {
      // First try RAG search
      const ragResponse = await axios.post('/rag/query', {
        query: text,
        top_k: chatSettings.value.top_k,
        similarity_threshold: chatSettings.value.similarity_threshold,
        include_metadata: chatSettings.value.include_metadata
      })

      // Then query Jade assistant with context
      const jadeResponse = await axios.post('/jade/query', {
        query: text,
        context: ragResponse.data.results
      })

      // Parse markdown in response
      const parsedContent = marked(jadeResponse.data.response)

      // Update AI message with combined response
      const aiIndex = messages.value.findIndex(m => m.id === aiMessage.id)
      if (aiIndex !== -1) {
        messages.value[aiIndex] = {
          ...aiMessage,
          loading: false,
          content: parsedContent,
          rawContent: jadeResponse.data.response,
          sources: ragResponse.data.results,
          queryInfo: {
            execution_time: jadeResponse.data.execution_time || 0,
            llm_used: 'Jade Assistant',
            total_sources: ragResponse.data.total_results || 0
          },
          toolResult: jadeResponse.data.result,
          toolError: jadeResponse.data.error
        }
      }

      // Show success toast if tool was executed
      if (jadeResponse.data.result) {
        addToast('Tool executed successfully', 'success')
      }
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      
      // Update AI message with error
      const aiIndex = messages.value.findIndex(m => m.id === aiMessage.id)
      if (aiIndex !== -1) {
        messages.value[aiIndex] = {
          ...aiMessage,
          loading: false,
          content: 'I apologize, but I encountered an error while processing your question. Please try again.',
          sources: [],
          queryInfo: null
        }
      }

      // Show error toast
      addToast(error.value, 'error')
    } finally {
      isLoading.value = false
    }
  }

  const clearChat = () => {
    messages.value = []
    recentQuestions.value = []
    sessionStartTime.value = Date.now()
    error.value = null
    addToast('Chat history cleared', 'info')
  }

  const setSelectedSource = (source) => {
    selectedSource.value = source
  }

  const updateChatSettings = (settings) => {
    chatSettings.value = {
      ...chatSettings.value,
      ...settings
    }
    addToast('Chat settings updated', 'success')
  }

  return {
    // State
    messages,
    isLoading,
    error,
    selectedSource,
    recentQuestions,
    chatSettings,
    toasts,
    
    // Computed
    chatStats,
    sessionTime,
    
    // Actions
    sendMessage,
    clearChat,
    setSelectedSource,
    updateChatSettings,
    addToast,
    removeToast
  }
}) 