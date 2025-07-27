<template>
  <div class="landing-container">
    <!-- Header -->
    <div class="header-section">
      <div class="logo-area">
        <h1 class="platform-title">💠 LinkOps AI Box</h1>
        <p class="platform-subtitle">Secure Offline AI Platform with Autonomous Learning</p>
        <div class="status-badge">
          <span class="status-dot"></span>
          100% Local • Air-Gapped • v1.0.0
        </div>
      </div>
    </div>

    <!-- Jade Chat Interface -->
    <div class="jade-chat-container">
      <div class="chat-header">
        <div class="jade-avatar">🤖</div>
        <div class="jade-info">
          <h3>Jade AI Assistant</h3>
          <p class="jade-status">
            <span class="status-indicator"></span>
            {{ isJadeOnline ? 'Online & Ready' : 'Initializing...' }}
          </p>
        </div>
        <div class="llm-info">
          <span class="llm-badge">{{ llmStatus.model_type || 'Local LLM' }}</span>
        </div>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          class="message-item"
          :class="{ 'user-message': message.isUser, 'jade-message': !message.isUser }"
        >
          <div class="message-avatar">
            {{ message.isUser ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">{{ message.isUser ? 'You' : 'Jade' }}</span>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-text" v-html="formatMessage(message.text)"></div>
            <div v-if="message.executionTime" class="message-meta">
              ⚡ Response time: {{ message.executionTime.toFixed(2) }}s
            </div>
          </div>
        </div>

        <!-- Typing indicator -->
        <div v-if="isJadeTyping" class="message-item jade-message typing">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
              Jade is thinking...
            </div>
          </div>
        </div>

        <!-- Role Selector -->
        <div v-if="showRoleSelector" class="role-selector-container">
          <div class="role-selector">
            <h4>Choose your role:</h4>
            <div class="role-options">
              <button 
                v-for="role in roles" 
                :key="role.id"
                @click="selectRole(role.id)"
                class="role-option"
              >
                <div class="role-icon">{{ role.icon }}</div>
                <div class="role-info">
                  <div class="role-title">{{ role.title }}</div>
                  <div class="role-description">{{ role.description }}</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="chat-input-area">
        <div class="input-container">
          <input 
            v-model="userInput" 
            @keyup.enter="sendMessage"
            placeholder="Ask Jade about the AI Box, HTC system, or anything else..."
            class="message-input"
            :disabled="isJadeTyping"
          />
          <button 
            @click="sendMessage" 
            :disabled="!userInput.trim() || isJadeTyping"
            class="send-button"
          >
            <span v-if="isJadeTyping">⏳</span>
            <span v-else>➤</span>
          </button>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <button 
            v-for="action in quickActions" 
            :key="action.text"
            @click="sendQuickMessage(action.text)"
            :disabled="isJadeTyping"
            class="quick-action-btn"
          >
            {{ action.icon }} {{ action.text }}
          </button>
        </div>
      </div>
    </div>

    <!-- Navigation CTA -->
    <div class="navigation-section">
      <div class="nav-grid">
        <router-link to="/dashboard" class="nav-card">
          <div class="nav-icon">🏠</div>
          <h4>Enter Dashboard</h4>
          <p>Access the full AI platform</p>
        </router-link>
        
        <router-link to="/htc-trainer" class="nav-card">
          <div class="nav-icon">🧠</div>
          <h4>Try HTC Learning</h4>
          <p>Train Jade on any task</p>
        </router-link>
        
        <a href="/api/docs" target="_blank" class="nav-card">
          <div class="nav-icon">📚</div>
          <h4>API Documentation</h4>
          <p>Developer resources</p>
        </a>
      </div>
    </div>

    <!-- Footer Info -->
    <div class="footer-info">
      <p>🔒 <strong>Privacy:</strong> All processing happens locally. No data leaves your machine.</p>
      <p>🚀 <strong>Demo Credentials:</strong> linkops-demo / demo123</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'

export default {
  name: 'LandingAssistant',
  setup() {
    // Reactive state
    const messages = ref([])
    const userInput = ref('')
    const isJadeTyping = ref(false)
    const isJadeOnline = ref(false)
    const llmStatus = ref({})
    const messagesContainer = ref(null)
    const currentIntroStep = ref(0)
    const selectedRole = ref(null)
    const showRoleSelector = ref(false)

    // Role-specific quick actions
    const getRoleQuickActions = (role) => {
      const actionsByRole = {
        cloud_engineer: [
          { icon: '🐳', text: 'Show me the Docker architecture' },
          { icon: '🛡️', text: 'Explain the security model' },
          { icon: '⚙️', text: 'Deployment automation' },
          { icon: '📊', text: 'Infrastructure monitoring' }
        ],
        ai_ml_engineer: [
          { icon: '🤖', text: 'LLM integration details' },
          { icon: '📊', text: 'ML pipeline automation' },
          { icon: '🧠', text: 'HTC autonomous learning' },
          { icon: '⚡', text: 'Model training workflows' }
        ],
        property_manager: [
          { icon: '🏗️', text: 'Vendor management demo' },
          { icon: '🔧', text: 'Maintenance automation' },
          { icon: '📋', text: 'Tenant data analysis' },
          { icon: '💰', text: 'Cost prediction models' }
        ]
      }
      
      return actionsByRole[role] || [
        { icon: '🎯', text: 'Give me a walkthrough' },
        { icon: '🧠', text: 'What is the HTC system?' },
        { icon: '🔧', text: 'Building tools demo' },
        { icon: '🔒', text: 'Privacy and security features' }
      ]
    }

    const quickActions = computed(() => {
      return selectedRole.value ? getRoleQuickActions(selectedRole.value) : [
        { icon: '🎯', text: 'Give me a walkthrough' },
        { icon: '🧠', text: 'What is the HTC system?' },
        { icon: '🔧', text: 'Building tools demo' },
        { icon: '🔒', text: 'Privacy and security features' }
      ]
    })

    // Role definitions
    const roles = ref([
      {
        id: 'cloud_engineer',
        icon: '☁️',
        title: 'Cloud Engineer',
        description: 'DevOps, Infrastructure, Containerization'
      },
      {
        id: 'ai_ml_engineer', 
        icon: '🧬',
        title: 'AI/ML Engineer',
        description: 'Machine Learning, Data Science, AI Systems'
      },
      {
        id: 'property_manager',
        icon: '🏢', 
        title: 'Property Manager',
        description: 'Real Estate, Tenant Management, Operations'
      }
    ])

    // Initial introduction script
    const initialIntro = [
      {
        text: "👋 Hi, I'm **Jade** — your secure, local AI assistant.",
        delay: 1000
      },
      {
        text: "🧠 Before we begin, can I ask — are you here as a:",
        delay: 3000,
        showRoleSelector: true
      }
    ]

    // Role-specific walkthrough scripts
    const roleScripts = {
      cloud_engineer: [
        {
          text: "☁️ **Welcome, Cloud Engineer!** This platform was built using real DevOps experience — including container orchestration, GitOps-style sync, and security-first infrastructure design.",
          delay: 1000
        },
        {
          text: "🐳 **I was deployed using:** Docker Compose with multiple secure services, LLM inference hosted entirely offline (via llama.cpp), file sync + PII-safe vector updates, and GitOps-like memory sync based on mounted directories.",
          delay: 4000
        },
        {
          text: "🛡️ **This isn't just an AI demo** — it's a hardened DevSecOps system you can run anywhere, even air-gapped. Perfect for classified environments, edge deployments, or anywhere you need AI without cloud dependencies.",
          delay: 7000
        },
        {
          text: "⚙️ **Technical highlights:** Microservices architecture, automated session cleanup, container security hardening, network isolation, and zero-trust deployment model.",
          delay: 10000
        },
        {
          text: "🚀 **Want to see:** The Docker architecture, security model, deployment automation, or infrastructure monitoring? Just ask!",
          delay: 13000
        }
      ],
      ai_ml_engineer: [
        {
          text: "🧬 **Hello fellow AI/ML engineer!** 👋 This platform demonstrates how you can deliver powerful AI workflows — securely, and fully offline.",
          delay: 1000
        },
        {
          text: "🤖 **I use:** mistral-7b-instruct.Q4_K_M.gguf via llama-cpp-python, ChromaDB for local vector search (RAG), an autonomous learning system (HTC) to retrain myself using user-uploaded data, and a drag-and-drop UI to create ML models on the fly.",
          delay: 4000
        },
        {
          text: "📊 **It's a full-stack AI pipeline** — with zero dependencies on OpenAI or external APIs. Features automated model selection, hyperparameter optimization, feature engineering, and production deployment.",
          delay: 7000
        },
        {
          text: "🧠 **The HTC system** showcases advanced MLOps: automated data preprocessing, algorithm comparison, cross-validation, model persistence, and real-time inference APIs.",
          delay: 10000
        },
        {
          text: "🎯 **Technical deep-dive options:** LLM integration, ML pipeline automation, model training workflows, or the autonomous learning architecture. What interests you most?",
          delay: 13000
        }
      ],
      property_manager: [
        {
          text: "🏢 **Hi there!** I was built for property managers like you. I know many companies are cautious about AI — especially with sensitive tenant data or constantly changing vendor policies.",
          delay: 1000
        },
        {
          text: "🔒 **That's why this system runs 100% offline.** No cloud. No API calls. No risk. Your tenant information, lease agreements, and vendor data never leave your servers.",
          delay: 4000
        },
        {
          text: "🛠️ **You can:** Upload your documents (like delinquency records or rent rolls), ask me to summarize policies or suggest vendors, train models from your own maintenance data, and create automated tools to answer common questions — all without coding.",
          delay: 7000
        },
        {
          text: "💼 **Real examples:** Vendor performance ranking, maintenance cost prediction, tenant screening automation, lease renewal risk assessment, and policy Q&A systems.",
          delay: 10000
        },
        {
          text: "🎯 **I'm like your own personal AI analyst** — running securely inside your office. Want to see vendor management, maintenance automation, or tenant data analysis? Just ask!",
          delay: 13000
        }
      ]
    }

    // Methods
    const addMessage = (text, isUser = false, executionTime = null) => {
      messages.value.push({
        text,
        isUser,
        timestamp: new Date(),
        executionTime
      })
      nextTick(() => {
        scrollToBottom()
      })
    }

    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }

    const formatTime = (timestamp) => {
      return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    const formatMessage = (text) => {
      // Convert markdown-style formatting to HTML
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>')
    }

    const checkJadeStatus = async () => {
      try {
        const response = await fetch('/api/jade/status')
        if (response.ok) {
          const status = await response.json()
          isJadeOnline.value = status.status === 'available'
          llmStatus.value = status.llm_status || {}
        }
      } catch (error) {
        console.warn('Jade status check failed:', error)
        isJadeOnline.value = false
      }
    }

    const sendMessage = async () => {
      if (!userInput.value.trim() || isJadeTyping.value) return

      const message = userInput.value.trim()
      userInput.value = ''

      // Add user message
      addMessage(message, true)

      // Show typing indicator
      isJadeTyping.value = true

      try {
        const startTime = performance.now()
        
        const response = await fetch('/api/jade/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query: message,
            context: [],
            user_role: selectedRole.value
          })
        })

        if (response.ok) {
          const result = await response.json()
          const executionTime = (performance.now() - startTime) / 1000
          
          addMessage(result.response, false, executionTime)
        } else {
          addMessage("I apologize, but I'm having trouble responding right now. Please try again or check if the services are running.", false)
        }
      } catch (error) {
        console.error('Error sending message:', error)
        addMessage("I'm currently offline. Please make sure the LinkOps services are running and try again.", false)
      } finally {
        isJadeTyping.value = false
      }
    }

    const sendQuickMessage = (message) => {
      userInput.value = message
      sendMessage()
    }

    const selectRole = async (roleId) => {
      selectedRole.value = roleId
      showRoleSelector.value = false
      
      // Add role selection message
      const roleInfo = roles.value.find(r => r.id === roleId)
      addMessage(`${roleInfo.icon} ${roleInfo.title}`, true)
      
      // Start role-specific walkthrough
      await startRoleWalkthrough(roleId)
    }

    const startRoleWalkthrough = async (roleId) => {
      const script = roleScripts[roleId]
      if (!script) return

      for (const step of script) {
        await new Promise(resolve => setTimeout(resolve, step.delay))
        
        isJadeTyping.value = true
        await new Promise(resolve => setTimeout(resolve, 1500)) // Simulate thinking time
        
        addMessage(step.text, false)
        isJadeTyping.value = false
        
        // Pause between messages
        await new Promise(resolve => setTimeout(resolve, 2000))
      }
    }

    const startIntroSequence = async () => {
      // Wait a bit for everything to load
      await new Promise(resolve => setTimeout(resolve, 2000))

      for (const step of initialIntro) {
        await new Promise(resolve => setTimeout(resolve, step.delay))
        
        isJadeTyping.value = true
        await new Promise(resolve => setTimeout(resolve, 1500)) // Simulate thinking time
        
        addMessage(step.text, false)
        isJadeTyping.value = false
        
        // Show role selector if needed
        if (step.showRoleSelector) {
          showRoleSelector.value = true
        }
        
        // Pause between messages
        await new Promise(resolve => setTimeout(resolve, 2000))
      }
    }

    // Lifecycle
    onMounted(async () => {
      await checkJadeStatus()
      
      // Add welcome message immediately
      addMessage("🚀 LinkOps AI Box is initializing...", false)
      
      // Start the introduction sequence
      startIntroSequence()
    })

    return {
      // State
      messages,
      userInput,
      isJadeTyping,
      isJadeOnline,
      llmStatus,
      messagesContainer,
      selectedRole,
      showRoleSelector,
      roles,
      quickActions,
      
      // Methods
      sendMessage,
      sendQuickMessage,
      selectRole,
      formatTime,
      formatMessage
    }
  }
}
</script>

<style scoped>
.landing-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  color: white;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 2rem;
}

.platform-title {
  font-size: 3rem;
  font-weight: bold;
  background: linear-gradient(135deg, #00f5ff, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
  text-shadow: 0 0 30px rgba(0, 245, 255, 0.3);
}

.platform-subtitle {
  font-size: 1.2rem;
  color: #94a3b8;
  margin-bottom: 1rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(0, 245, 255, 0.1);
  border: 1px solid rgba(0, 245, 255, 0.3);
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  color: #00f5ff;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #00ff00;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.jade-chat-container {
  flex: 1;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  height: 600px;
  margin-bottom: 2rem;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.jade-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #00f5ff, #00d4ff);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.jade-info h3 {
  margin: 0;
  color: #00f5ff;
  font-size: 1.1rem;
}

.jade-status {
  margin: 0;
  font-size: 0.9rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  width: 6px;
  height: 6px;
  background: #00ff00;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.llm-info {
  margin-left: auto;
}

.llm-badge {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.jade-message .message-avatar {
  background: linear-gradient(135deg, #00f5ff, #00d4ff);
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
}

.message-content {
  max-width: 70%;
  background: rgba(51, 65, 85, 0.6);
  border-radius: 12px;
  padding: 0.75rem;
  backdrop-filter: blur(5px);
}

.user-message .message-content {
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.message-sender {
  font-weight: 600;
  color: #00f5ff;
}

.user-message .message-sender {
  color: #a855f7;
}

.message-time {
  color: #94a3b8;
}

.message-text {
  line-height: 1.5;
  color: #e2e8f0;
}

.message-text strong {
  color: #00f5ff;
}

.message-text code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9rem;
}

.message-meta {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #94a3b8;
  font-style: italic;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #00f5ff;
  border-radius: 50%;
  animation: typing 1.5s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.3s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; }
  30% { opacity: 1; }
}

.role-selector-container {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
  animation: fadeIn 0.5s ease-in;
}

.role-selector {
  background: rgba(51, 65, 85, 0.8);
  border: 2px solid rgba(0, 245, 255, 0.3);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 25px rgba(0, 245, 255, 0.2);
}

.role-selector h4 {
  margin: 0 0 1rem 0;
  text-align: center;
  color: #00f5ff;
  font-size: 1.1rem;
}

.role-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 300px;
}

.role-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(30, 41, 59, 0.6);
  border: 2px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.role-option:hover {
  border-color: #00f5ff;
  background: rgba(0, 245, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 245, 255, 0.2);
}

.role-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.role-info {
  flex: 1;
}

.role-title {
  font-weight: 600;
  color: #e2e8f0;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.role-description {
  color: #94a3b8;
  font-size: 0.9rem;
  line-height: 1.3;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-input-area {
  padding: 1rem;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.input-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.message-input {
  flex: 1;
  background: rgba(51, 65, 85, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  padding: 0.75rem;
  color: white;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.message-input:focus {
  outline: none;
  border-color: #00f5ff;
  box-shadow: 0 0 0 2px rgba(0, 245, 255, 0.2);
}

.message-input::placeholder {
  color: #94a3b8;
}

.send-button {
  background: linear-gradient(135deg, #00f5ff, #00d4ff);
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: #0f172a;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.quick-action-btn {
  background: rgba(51, 65, 85, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 16px;
  padding: 0.5rem 0.75rem;
  color: #e2e8f0;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action-btn:hover:not(:disabled) {
  background: rgba(0, 245, 255, 0.1);
  border-color: #00f5ff;
  color: #00f5ff;
}

.quick-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.navigation-section {
  margin-bottom: 2rem;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.nav-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  text-decoration: none;
  color: white;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.nav-card:hover {
  transform: translateY(-4px);
  border-color: #00f5ff;
  box-shadow: 0 8px 25px rgba(0, 245, 255, 0.2);
}

.nav-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.nav-card h4 {
  margin: 0 0 0.5rem 0;
  color: #00f5ff;
  font-size: 1.1rem;
}

.nav-card p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

.footer-info {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.footer-info p {
  margin: 0.5rem 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .platform-title {
    font-size: 2rem;
  }
  
  .jade-chat-container {
    height: 500px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .nav-grid {
    grid-template-columns: 1fr;
  }
}
</style>