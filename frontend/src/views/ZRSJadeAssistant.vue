<template>
  <div class="zrs-jade-container min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
    <!-- Header -->
    <div class="bg-slate-800/80 backdrop-blur-sm border-b border-blue-500/30 p-4">
      <div class="flex items-center justify-between max-w-7xl mx-auto">
        <div class="flex items-center space-x-4">
          <div class="h-10 w-10 bg-gradient-to-r from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">🏢</span>
          </div>
          <div>
            <h1 class="text-xl font-bold text-white">ZRS Property Management</h1>
            <p class="text-blue-300 text-sm">Jade AI Assistant - Elite Mode</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-4">
          <div class="text-right">
            <p class="text-white text-sm font-medium">{{ currentUser }}</p>
            <p class="text-blue-300 text-xs">Property Manager</p>
          </div>
          <div class="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span class="text-white text-sm font-bold">{{ currentUser.charAt(0) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto p-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Jade Chat Interface -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Quick Actions -->
          <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-blue-500/20">
            <h2 class="text-lg font-semibold text-white mb-4 flex items-center">
              ⚡ Quick Actions
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <button 
                v-for="action in quickActions" 
                :key="action.id"
                @click="executeQuickAction(action)"
                class="bg-slate-700/50 hover:bg-blue-600/20 border border-blue-500/30 rounded-lg p-3 text-left transition-colors duration-200"
              >
                <div class="text-blue-400 text-lg mb-1">{{ action.icon }}</div>
                <div class="text-white text-sm font-medium">{{ action.title }}</div>
                <div class="text-blue-300 text-xs">{{ action.description }}</div>
              </button>
            </div>
          </div>

          <!-- Chat Interface -->
          <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-blue-500/20 overflow-hidden">
            <!-- Chat Header -->
            <div class="bg-gradient-to-r from-blue-600 to-cyan-500 p-4">
              <div class="flex items-center space-x-3">
                <div class="h-8 w-8 bg-white/20 rounded-full flex items-center justify-center">
                  <span class="text-white font-bold">🤖</span>
                </div>
                <div>
                  <h3 class="text-white font-semibold">Jade Property Assistant</h3>
                  <p class="text-blue-100 text-sm">{{ isOnline ? 'Online' : 'Offline' }} • ZRS Trained</p>
                </div>
              </div>
            </div>

            <!-- Chat Messages -->
            <div class="h-96 overflow-y-auto p-4 space-y-4" ref="chatContainer">
              <div v-for="message in chatMessages" :key="message.id" class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                  <div v-if="message.sender === 'user'" class="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span class="text-white text-sm font-bold">{{ currentUser.charAt(0) }}</span>
                  </div>
                  <div v-else class="h-8 w-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
                    <span class="text-white font-bold text-sm">🤖</span>
                  </div>
                </div>
                
                <div class="flex-1">
                  <div class="flex items-center space-x-2 mb-1">
                    <span class="text-white font-medium text-sm">{{ message.sender === 'user' ? currentUser : 'Jade' }}</span>
                    <span class="text-blue-300 text-xs">{{ formatTime(message.timestamp) }}</span>
                  </div>
                  
                  <div v-if="message.sender === 'user'" class="bg-blue-600 text-white rounded-lg p-3 max-w-md">
                    {{ message.content }}
                  </div>
                  
                  <div v-else class="bg-slate-700/60 text-white rounded-lg p-3 border border-blue-500/20">
                    <div class="whitespace-pre-wrap">{{ message.content }}</div>
                    
                    <!-- Tool Execution Result -->
                    <div v-if="message.toolResult" class="mt-3 bg-slate-600/40 rounded-lg p-3 border border-green-500/30">
                      <div class="flex items-center space-x-2 mb-2">
                        <span class="text-green-400 text-sm">✅ Tool Executed</span>
                        <span class="text-green-300 text-xs">{{ message.toolResult.tool }}</span>
                      </div>
                      <div class="text-green-100 text-sm">{{ message.toolResult.summary }}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Typing Indicator -->
              <div v-if="isTyping" class="flex items-center space-x-3">
                <div class="h-8 w-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
                  <span class="text-white font-bold text-sm">🤖</span>
                </div>
                <div class="bg-slate-700/60 rounded-lg p-3 border border-blue-500/20">
                  <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Chat Input -->
            <div class="border-t border-blue-500/20 p-4">
              <div class="flex space-x-3">
                <input
                  v-model="currentMessage"
                  @keypress.enter="sendMessage"
                  type="text"
                  placeholder="Ask Jade about property management..."
                  class="flex-1 bg-slate-700/50 border border-blue-500/30 rounded-lg px-4 py-2 text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  @click="sendMessage"
                  :disabled="!currentMessage.trim() || isTyping"
                  class="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:opacity-50 text-white rounded-lg px-4 py-2 transition-colors duration-200"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Property Stats -->
          <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-blue-500/20">
            <h3 class="text-lg font-semibold text-white mb-4">📊 Property Stats</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-blue-300">Total Units</span>
                <span class="text-white font-semibold">{{ propertyStats.totalUnits }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-blue-300">Occupied</span>
                <span class="text-green-400 font-semibold">{{ propertyStats.occupied }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-blue-300">Delinquent</span>
                <span class="text-red-400 font-semibold">{{ propertyStats.delinquent }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-blue-300">Maintenance</span>
                <span class="text-yellow-400 font-semibold">{{ propertyStats.maintenance }}</span>
              </div>
            </div>
          </div>

          <!-- Recent Tools -->
          <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-blue-500/20">
            <h3 class="text-lg font-semibold text-white mb-4">🔧 Recent Tools</h3>
            <div class="space-y-2">
              <div v-for="tool in recentTools" :key="tool.id" class="flex items-center space-x-3 p-2 bg-slate-700/30 rounded-lg">
                <span class="text-lg">{{ tool.icon }}</span>
                <div class="flex-1">
                  <div class="text-white text-sm font-medium">{{ tool.name }}</div>
                  <div class="text-blue-300 text-xs">{{ tool.lastUsed }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- System Status -->
          <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-blue-500/20">
            <h3 class="text-lg font-semibold text-white mb-4">🟢 System Status</h3>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-blue-300 text-sm">Jade AI</span>
                <span class="text-green-400 text-sm">● Online</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-blue-300 text-sm">MCP Tools</span>
                <span class="text-green-400 text-sm">● Ready</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-blue-300 text-sm">Email System</span>
                <span class="text-green-400 text-sm">● Connected</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-blue-300 text-sm">Database</span>
                <span class="text-green-400 text-sm">● Synced</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ZRSJadeAssistant',
  data() {
    return {
      currentUser: 'Sarah Connor',
      isOnline: true,
      isTyping: false,
      currentMessage: '',
      chatMessages: [
        {
          id: 1,
          sender: 'jade',
          content: 'Hello! I\'m Jade, your ZRS Property Management AI assistant. I can help with rent collection, maintenance requests, vendor coordination, and more. How can I assist you today?',
          timestamp: new Date(Date.now() - 60000),
        }
      ],
      quickActions: [
        {
          id: 'late_notice',
          icon: '📧',
          title: 'Send Late Notice',
          description: 'Email late rent notice',
          prompt: 'Send late notice to Tony Stark in unit 401 for $2500, 12 days late'
        },
        {
          id: 'maintenance',
          icon: '🔧',
          title: 'Report Maintenance',
          description: 'Create work order',
          prompt: 'Water leak emergency in unit 303 - dispatch immediately'
        },
        {
          id: 'delinquency',
          icon: '💰',
          title: 'Check Delinquency',
          description: 'View late payments',
          prompt: 'Show me all tenants more than 15 days late'
        },
        {
          id: 'turnover',
          icon: '🏠',
          title: 'Schedule Turnover',
          description: 'Prepare vacant unit',
          prompt: 'Schedule turnover for unit 205 after move-out tomorrow'
        },
        {
          id: 'vendor',
          icon: '👷',
          title: 'Find Vendor',
          description: 'Get contractor quotes',
          prompt: 'Which HVAC vendor should I use for urgent repair?'
        },
        {
          id: 'broadcast',
          icon: '📢',
          title: 'Broadcast Notice',
          description: 'Send tenant notice',
          prompt: 'Send notice to all tenants about pool closure'
        }
      ],
      propertyStats: {
        totalUnits: 156,
        occupied: 142,
        delinquent: 8,
        maintenance: 12
      },
      recentTools: [
        { id: 1, name: 'Send Late Notice', icon: '📧', lastUsed: '2 min ago' },
        { id: 2, name: 'Query Delinquency', icon: '💰', lastUsed: '15 min ago' },
        { id: 3, name: 'Vendor Suggest', icon: '👷', lastUsed: '1 hour ago' },
        { id: 4, name: 'Broadcast Notice', icon: '📢', lastUsed: '2 hours ago' }
      ]
    }
  },
  methods: {
    executeQuickAction(action) {
      this.currentMessage = action.prompt;
      this.sendMessage();
    },
    
    async sendMessage() {
      if (!this.currentMessage.trim() || this.isTyping) return;
      
      const userMessage = {
        id: Date.now(),
        sender: 'user',
        content: this.currentMessage,
        timestamp: new Date()
      };
      
      this.chatMessages.push(userMessage);
      const prompt = this.currentMessage;
      this.currentMessage = '';
      this.isTyping = true;
      
      // Scroll to bottom
      this.$nextTick(() => {
        this.scrollToBottom();
      });
      
      // Simulate Jade response
      setTimeout(() => {
        const response = this.generateJadeResponse(prompt);
        this.chatMessages.push(response);
        this.isTyping = false;
        
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }, 1500 + Math.random() * 1000);
    },
    
    generateJadeResponse(prompt) {
      const responses = {
        'late': {
          content: 'I\'ll send a late rent notice right away. Executing the send_late_notice tool...',
          toolResult: {
            tool: 'send_late_notice',
            summary: 'Late notice sent to Tony Stark (Unit 401) - Email delivered successfully'
          }
        },
        'maintenance': {
          content: 'Emergency maintenance request created. Dispatching to on-call technician immediately.',
          toolResult: {
            tool: 'notify_maintenance',
            summary: 'Work Order #WO-2025012701 created - Emergency response team notified'
          }
        },
        'delinquency': {
          content: 'Analyzing current delinquency data...',
          toolResult: {
            tool: 'query_delinquency',
            summary: 'Found 8 tenants over 15 days late - Total owed: $14,200'
          }
        },
        'turnover': {
          content: 'Scheduling complete turnover process for the unit...',
          toolResult: {
            tool: 'schedule_turnover',
            summary: 'Turnover scheduled - Ready date: Feb 3rd, Estimated cost: $450'
          }
        },
        'vendor': {
          content: 'Analyzing vendor performance and availability for HVAC work...',
          toolResult: {
            tool: 'vendor_suggest',
            summary: 'Top recommendation: CoolAir Systems - 4.8 rating, 2hr response time'
          }
        },
        'broadcast': {
          content: 'Preparing broadcast notice for all tenants...',
          toolResult: {
            tool: 'broadcast_notice',
            summary: 'Notice sent to 142 tenants - 98.5% delivery rate'
          }
        }
      };
      
      // Find matching response
      const lowerPrompt = prompt.toLowerCase();
      let response = {
        content: 'I understand you\'re asking about property management. Let me help you with that using the appropriate ZRS tools.',
        toolResult: null
      };
      
      for (const [key, value] of Object.entries(responses)) {
        if (lowerPrompt.includes(key)) {
          response = value;
          break;
        }
      }
      
      return {
        id: Date.now() + 1,
        sender: 'jade',
        content: response.content,
        timestamp: new Date(),
        toolResult: response.toolResult
      };
    },
    
    formatTime(timestamp) {
      return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    scrollToBottom() {
      const container = this.$refs.chatContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }
}
</script>

<style scoped>
.zrs-jade-container {
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

.animate-bounce {
  animation: bounce 1.4s infinite;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px);
  }
}
</style>