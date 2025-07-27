<template>
  <div class="zrs-mcp-tools min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
    <!-- Header -->
    <div class="bg-slate-800/80 backdrop-blur-sm border-b border-purple-500/30 p-4">
      <div class="max-w-7xl mx-auto">
        <h1 class="text-2xl font-bold text-white flex items-center">
          🛠️ ZRS MCP Tools Dashboard
        </h1>
        <p class="text-purple-300 mt-1">Model Context Protocol Tools for Property Management</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto p-6">
      <!-- Tool Categories -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div v-for="tool in mcpTools" :key="tool.name" 
             class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-purple-500/20 hover:border-purple-400/40 transition-all duration-300 cursor-pointer"
             @click="selectTool(tool)">
          
          <!-- Tool Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="h-12 w-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <span class="text-white text-xl">{{ tool.icon }}</span>
            </div>
            <span class="text-xs px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full">
              {{ tool.category }}
            </span>
          </div>
          
          <!-- Tool Info -->
          <h3 class="text-lg font-semibold text-white mb-2">{{ tool.displayName }}</h3>
          <p class="text-purple-300 text-sm mb-4">{{ tool.description }}</p>
          
          <!-- Tool Stats -->
          <div class="flex items-center justify-between text-xs">
            <span class="text-purple-400">{{ tool.parameters.length }} parameters</span>
            <span class="text-green-400">✓ Active</span>
          </div>
        </div>
      </div>

      <!-- Tool Details Panel -->
      <div v-if="selectedTool" class="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-purple-500/20 overflow-hidden">
        <!-- Panel Header -->
        <div class="bg-gradient-to-r from-purple-600 to-pink-600 p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="h-12 w-12 bg-white/20 rounded-lg flex items-center justify-center">
                <span class="text-white text-xl">{{ selectedTool.icon }}</span>
              </div>
              <div>
                <h2 class="text-xl font-bold text-white">{{ selectedTool.displayName }}</h2>
                <p class="text-purple-100">{{ selectedTool.description }}</p>
              </div>
            </div>
            <button @click="selectedTool = null" class="text-white/80 hover:text-white">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <div class="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Tool Configuration -->
          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-semibold text-white mb-4">🔧 Configuration</h3>
              
              <!-- Parameters -->
              <div class="space-y-4">
                <div v-for="param in selectedTool.parameters" :key="param.name" class="space-y-2">
                  <label class="block text-purple-300 text-sm font-medium">
                    {{ param.name }}
                    <span v-if="param.required" class="text-red-400">*</span>
                  </label>
                  
                  <div v-if="param.type === 'select'" class="relative">
                    <select v-model="toolParams[param.name]" 
                            class="w-full bg-slate-700/50 border border-purple-500/30 rounded-lg px-4 py-2 text-white">
                      <option value="">Select {{ param.name }}</option>
                      <option v-for="option in param.options" :key="option" :value="option">{{ option }}</option>
                    </select>
                  </div>
                  
                  <div v-else-if="param.type === 'boolean'" class="flex items-center">
                    <input type="checkbox" v-model="toolParams[param.name]" 
                           class="h-4 w-4 text-purple-600 bg-slate-700 border-purple-500/30 rounded">
                    <span class="ml-2 text-purple-300 text-sm">{{ param.description }}</span>
                  </div>
                  
                  <div v-else>
                    <input v-model="toolParams[param.name]" 
                           :type="param.type === 'number' ? 'number' : 'text'"
                           :placeholder="param.example || `Enter ${param.name}`"
                           class="w-full bg-slate-700/50 border border-purple-500/30 rounded-lg px-4 py-2 text-white placeholder-purple-400">
                  </div>
                  
                  <p class="text-purple-400 text-xs">{{ param.description }}</p>
                </div>
              </div>
              
              <!-- Execute Button -->
              <button @click="executeTool" 
                      :disabled="isExecuting || !canExecute"
                      class="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200">
                <span v-if="isExecuting" class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Executing...
                </span>
                <span v-else>Execute Tool</span>
              </button>
            </div>
          </div>

          <!-- Tool Information -->
          <div class="space-y-6">
            <!-- Command Preview -->
            <div>
              <h3 class="text-lg font-semibold text-white mb-4">💻 Command Preview</h3>
              <div class="bg-slate-900/60 border border-purple-500/20 rounded-lg p-4">
                <code class="text-purple-300 text-sm whitespace-pre-wrap">{{ generatedCommand }}</code>
              </div>
            </div>

            <!-- Tool Specs -->
            <div>
              <h3 class="text-lg font-semibold text-white mb-4">📋 Tool Specifications</h3>
              <div class="space-y-3">
                <div class="flex justify-between items-center">
                  <span class="text-purple-300">Category</span>
                  <span class="text-white">{{ selectedTool.category }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-purple-300">Timeout</span>
                  <span class="text-white">{{ selectedTool.execution?.timeout || 30 }}s</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-purple-300">Retry Count</span>
                  <span class="text-white">{{ selectedTool.execution?.retry_count || 2 }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-purple-300">Log Level</span>
                  <span class="text-white">{{ selectedTool.execution?.log_level || 'INFO' }}</span>
                </div>
              </div>
            </div>

            <!-- Execution History -->
            <div v-if="executionHistory.length > 0">
              <h3 class="text-lg font-semibold text-white mb-4">📝 Recent Executions</h3>
              <div class="space-y-2 max-h-64 overflow-y-auto">
                <div v-for="execution in executionHistory" :key="execution.id"
                     class="bg-slate-700/30 border border-purple-500/20 rounded-lg p-3">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-white text-sm font-medium">{{ execution.tool }}</span>
                    <span :class="execution.success ? 'text-green-400' : 'text-red-400'" class="text-xs">
                      {{ execution.success ? '✓ Success' : '✗ Failed' }}
                    </span>
                  </div>
                  <p class="text-purple-300 text-xs">{{ execution.summary }}</p>
                  <p class="text-purple-400 text-xs mt-1">{{ formatTime(execution.timestamp) }}</p>
                </div>
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
  name: 'ZRSMCPTools',
  data() {
    return {
      selectedTool: null,
      isExecuting: false,
      toolParams: {},
      executionHistory: [],
      mcpTools: [
        {
          name: 'send_late_notice',
          displayName: 'Send Late Notice',
          icon: '📧',
          category: 'billing',
          description: 'Send late rent notice to tenant with ZRS branding and legal compliance',
          parameters: [
            { name: 'tenant_name', type: 'text', required: true, description: 'Full name of the tenant', example: 'John Wick' },
            { name: 'unit_number', type: 'text', required: true, description: 'Unit number', example: '204' },
            { name: 'amount_due', type: 'number', required: true, description: 'Total amount overdue', example: 1800 },
            { name: 'days_late', type: 'number', required: true, description: 'Days past due', example: 12 }
          ],
          execution: { timeout: 30, retry_count: 3, log_level: 'INFO' }
        },
        {
          name: 'notify_maintenance',
          displayName: 'Notify Maintenance',
          icon: '🔧',
          category: 'maintenance',
          description: 'Alert maintenance team with automatic priority assignment and vendor routing',
          parameters: [
            { name: 'unit_number', type: 'text', required: true, description: 'Unit reporting the issue', example: '404' },
            { name: 'issue', type: 'text', required: true, description: 'Description of the problem', example: 'leaking faucet' },
            { name: 'priority', type: 'select', required: true, options: ['low', 'medium', 'high', 'emergency'], description: 'Urgency level' },
            { name: 'tenant_contact', type: 'text', required: false, description: 'Tenant phone number', example: '555-0123' }
          ],
          execution: { timeout: 30, retry_count: 2, log_level: 'INFO' }
        },
        {
          name: 'vendor_suggest',
          displayName: 'Suggest Vendor',
          icon: '👷',
          category: 'vendor',
          description: 'Recommend best ZRS-approved vendor based on performance and cost analysis',
          parameters: [
            { name: 'work_type', type: 'select', required: true, options: ['HVAC', 'plumbing', 'electrical', 'painting', 'flooring', 'roofing', 'general'], description: 'Type of work needed' },
            { name: 'urgency', type: 'select', required: false, options: ['routine', 'urgent', 'emergency'], description: 'How quickly work is needed' },
            { name: 'budget_max', type: 'number', required: false, description: 'Maximum budget', example: 2500 }
          ],
          execution: { timeout: 45, retry_count: 2, log_level: 'INFO' }
        },
        {
          name: 'schedule_turnover',
          displayName: 'Schedule Turnover',
          icon: '🏠',
          category: 'unit_turnover',
          description: 'Schedule complete cleaning and inspection workflow for vacant units',
          parameters: [
            { name: 'unit_number', type: 'text', required: true, description: 'Unit to be turned over', example: '509' },
            { name: 'move_out_date', type: 'date', required: true, description: 'Move-out date (YYYY-MM-DD)', example: '2025-08-01' },
            { name: 'new_lease_date', type: 'date', required: false, description: 'New tenant move-in date', example: '2025-08-15' },
            { name: 'deep_clean', type: 'boolean', required: false, description: 'Whether deep cleaning is required' }
          ],
          execution: { timeout: 60, retry_count: 2, log_level: 'INFO' }
        },
        {
          name: 'query_delinquency',
          displayName: 'Query Delinquency',
          icon: '💰',
          category: 'financial',
          description: 'Analyze tenant payment data with advanced filtering and analytics',
          parameters: [
            { name: 'days_late', type: 'number', required: true, description: 'Minimum days late', example: 15 },
            { name: 'building', type: 'text', required: false, description: 'Filter by building', example: 'Building A' },
            { name: 'amount_threshold', type: 'number', required: false, description: 'Minimum amount owed', example: 500 },
            { name: 'sort_by', type: 'select', required: false, options: ['days_late', 'amount_owed', 'tenant_name', 'unit'], description: 'Sort field' }
          ],
          execution: { timeout: 30, retry_count: 2, log_level: 'INFO' }
        },
        {
          name: 'broadcast_notice',
          displayName: 'Broadcast Notice',
          icon: '📢',
          category: 'communication',
          description: 'Send mass notifications with professional formatting and delivery tracking',
          parameters: [
            { name: 'subject', type: 'text', required: true, description: 'Email subject line', example: 'Pool Closure Notice' },
            { name: 'body', type: 'text', required: true, description: 'Message body', example: 'Pool closed for maintenance' },
            { name: 'recipient_group', type: 'select', required: false, options: ['all_tenants', 'building_a', 'building_b', 'current_residents', 'delinquent_only'], description: 'Target audience' },
            { name: 'priority', type: 'select', required: false, options: ['low', 'normal', 'high', 'urgent'], description: 'Message priority' }
          ],
          execution: { timeout: 120, retry_count: 3, log_level: 'INFO' }
        }
      ]
    }
  },
  computed: {
    canExecute() {
      if (!this.selectedTool) return false;
      
      const requiredParams = this.selectedTool.parameters.filter(p => p.required);
      return requiredParams.every(param => 
        this.toolParams[param.name] && 
        this.toolParams[param.name].toString().trim() !== ''
      );
    },
    
    generatedCommand() {
      if (!this.selectedTool) return '';
      
      let command = `python tools/${this.selectedTool.name}.py`;
      
      for (const param of this.selectedTool.parameters) {
        const value = this.toolParams[param.name];
        if (value !== undefined && value !== '') {
          if (param.type === 'boolean') {
            if (value) command += ` --${param.name}`;
          } else {
            command += ` --${param.name} '${value}'`;
          }
        }
      }
      
      return command;
    }
  },
  methods: {
    selectTool(tool) {
      this.selectedTool = tool;
      this.toolParams = {};
      
      // Initialize with default values
      tool.parameters.forEach(param => {
        if (param.type === 'boolean') {
          this.toolParams[param.name] = false;
        } else {
          this.toolParams[param.name] = '';
        }
      });
    },
    
    async executeTool() {
      if (!this.canExecute) return;
      
      this.isExecuting = true;
      
      // Simulate tool execution
      setTimeout(() => {
        const success = Math.random() > 0.1; // 90% success rate
        
        const execution = {
          id: Date.now(),
          tool: this.selectedTool.displayName,
          success: success,
          timestamp: new Date(),
          summary: success 
            ? this.getSuccessMessage(this.selectedTool.name)
            : 'Tool execution failed - please check parameters'
        };
        
        this.executionHistory.unshift(execution);
        this.isExecuting = false;
        
        // Show notification
        this.$emit('tool-executed', execution);
      }, 2000 + Math.random() * 2000);
    },
    
    getSuccessMessage(toolName) {
      const messages = {
        'send_late_notice': 'Late notice sent successfully - Email delivered',
        'notify_maintenance': 'Work order created - Maintenance team notified',
        'vendor_suggest': 'Vendor recommendations generated - 3 options found',
        'schedule_turnover': 'Turnover scheduled - Timeline created',
        'query_delinquency': 'Delinquency analysis complete - Report generated',
        'broadcast_notice': 'Broadcast sent - 98% delivery rate achieved'
      };
      
      return messages[toolName] || 'Tool executed successfully';
    },
    
    formatTime(timestamp) {
      return timestamp.toLocaleString();
    }
  }
}
</script>

<style scoped>
.zrs-mcp-tools {
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

input[type="date"] {
  color-scheme: dark;
}
</style>