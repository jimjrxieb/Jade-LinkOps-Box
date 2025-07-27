<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-6 space-y-6">
    <!-- Header -->
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-jade drop-shadow glow">💠 LinkOps Box</h1>
      <p class="text-cyan-400 mt-2">Secure Offline AI Platform with Jade Assistant</p>
      <div class="mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-jade-500/10 text-jade-400 border border-jade-500/30">
        v1.0.0
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid md:grid-cols-4 sm:grid-cols-2 gap-6">
      <div class="card-glass hover:scale-105 transition-transform duration-200">
        <div class="flex justify-between items-start">
          <h2 class="text-cyan-300 text-sm">Synced Files</h2>
          <span class="status-badge-success">Live</span>
        </div>
        <p class="text-2xl font-bold mt-1">{{ stats.syncedFiles }}</p>
        <p class="text-xs text-gray-400 mt-1">Last sync: {{ stats.lastSync }}</p>
      </div>

      <div class="card-glass hover:scale-105 transition-transform duration-200">
        <div class="flex justify-between items-start">
          <h2 class="text-cyan-300 text-sm">MCP Tools</h2>
          <span class="status-badge-success">{{ stats.activeTools }} Active</span>
        </div>
        <p class="text-2xl font-bold mt-1">{{ stats.totalTools }}</p>
        <div class="text-xs text-gray-400 mt-1">
          <div class="w-full bg-gray-700 rounded-full h-1">
            <div class="bg-jade-500 h-1 rounded-full" :style="{ width: `${(stats.activeTools / stats.totalTools) * 100}%` }"></div>
          </div>
        </div>
      </div>

      <div class="card-glass hover:scale-105 transition-transform duration-200">
        <div class="flex justify-between items-start">
          <h2 class="text-cyan-300 text-sm">ML Models</h2>
          <span class="status-badge-warning">Training</span>
        </div>
        <p class="text-2xl font-bold mt-1">{{ stats.mlModels }}</p>
        <p class="text-xs text-gray-400 mt-1">{{ stats.modelStatus }}</p>
      </div>

      <div class="card-glass hover:scale-105 transition-transform duration-200">
        <div class="flex justify-between items-start">
          <h2 class="text-cyan-300 text-sm">Vector Index</h2>
          <span class="status-badge-success">Ready</span>
        </div>
        <p class="text-2xl font-bold mt-1">{{ stats.vectorChunks }} chunks</p>
        <p class="text-xs text-gray-400 mt-1">{{ stats.indexSize }} MB used</p>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid md:grid-cols-4 gap-6 mt-8">
      <button 
        @click="$router.push('/chat')" 
        class="card-glass-hover group p-6 text-left"
      >
        <div class="flex items-center space-x-4">
          <div class="p-3 rounded-lg bg-jade-500/10 text-jade-400 group-hover:scale-110 transition-transform">
            💬
          </div>
          <div>
            <h3 class="font-bold text-white">Start Chat with Jade</h3>
            <p class="text-sm text-gray-400">Ask questions, run tools, get help</p>
          </div>
        </div>
      </button>

      <button 
        @click="$router.push('/upload')" 
        class="card-glass-hover group p-6 text-left"
      >
        <div class="flex items-center space-x-4">
          <div class="p-3 rounded-lg bg-jade-500/10 text-jade-400 group-hover:scale-110 transition-transform">
            📁
          </div>
          <div>
            <h3 class="font-bold text-white">Upload Documents</h3>
            <p class="text-sm text-gray-400">Sync files for Jade to learn from</p>
          </div>
        </div>
      </button>

      <button 
        @click="$router.push('/train')" 
        class="card-glass-hover group p-6 text-left"
      >
        <div class="flex items-center space-x-4">
          <div class="p-3 rounded-lg bg-jade-500/10 text-jade-400 group-hover:scale-110 transition-transform">
            📊
          </div>
          <div>
            <h3 class="font-bold text-white">Train ML Model</h3>
            <p class="text-sm text-gray-400">Improve vendor suggestions</p>
          </div>
        </div>
      </button>

      <button 
        @click="$router.push('/htc-trainer')" 
        class="card-glass-hover group p-6 text-left"
      >
        <div class="flex items-center space-x-4">
          <div class="p-3 rounded-lg bg-jade-500/10 text-jade-400 group-hover:scale-110 transition-transform">
            🧠
          </div>
          <div>
            <h3 class="font-bold text-white">HTC Learning</h3>
            <p class="text-sm text-gray-400">Train Jade on any new task</p>
          </div>
        </div>
      </button>
    </div>

    <!-- Jade Tip -->
    <div class="card-glass mt-8 p-8">
      <div class="flex items-start space-x-4">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 rounded-full bg-jade-500/10 flex items-center justify-center text-2xl">
            🤖
          </div>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h3 class="font-bold text-jade">Jade Assistant</h3>
            <span class="text-xs text-gray-400">Just now</span>
          </div>
          <p class="mt-1 text-gray-300">
            Hi! I'm your secure AI assistant. I can help you with:
          </p>
          <ul class="mt-2 space-y-1 text-sm text-gray-400">
            <li class="flex items-center">
              <span class="mr-2">✓</span>
              Searching through synced documents
            </li>
            <li class="flex items-center">
              <span class="mr-2">✓</span>
              Running and managing MCP tools
            </li>
            <li class="flex items-center">
              <span class="mr-2">✓</span>
              Training and evaluating ML models
            </li>
          </ul>
          <p class="mt-3 text-sm text-gray-300">
            Click "Start Chat" above to begin working together!
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Mock stats - replace with real API calls
const stats = ref({
  syncedFiles: 37,
  lastSync: '2 mins ago',
  totalTools: 12,
  activeTools: 10,
  mlModels: 3,
  modelStatus: 'Vendor model training (87%)',
  vectorChunks: 105,
  indexSize: 256
})

// Simulate real-time updates
onMounted(() => {
  // Update synced files count periodically
  setInterval(() => {
    if (Math.random() > 0.7) {
      stats.value.syncedFiles++
      stats.value.lastSync = 'Just now'
    }
  }, 5000)

  // Update model status
  setInterval(() => {
    const progress = Math.floor(Math.random() * 100)
    stats.value.modelStatus = `Vendor model training (${progress}%)`
  }, 3000)
})
</script>

<style scoped>
.glow {
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}
</style>
