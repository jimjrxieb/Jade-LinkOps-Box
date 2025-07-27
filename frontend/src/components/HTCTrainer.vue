<template>
  <div class="htc-trainer-container">
    <!-- Header -->
    <div class="header-section">
      <h1 class="page-title">🧠 HTC Autonomous Learning</h1>
      <p class="page-subtitle">Train Jade to learn any new task, generate tools, models, and knowledge automatically</p>
    </div>

    <!-- Training Interface -->
    <div class="training-interface">
      <!-- Task Description -->
      <div class="form-section">
        <label class="form-label">📝 What should Jade learn?</label>
        <textarea 
          v-model="taskDescription" 
          placeholder="Describe the task you want Jade to learn (e.g., 'Analyze customer data and generate risk scores', 'Create automation tools for data processing')"
          class="task-input"
          rows="3"
        ></textarea>
      </div>

      <!-- File Upload -->
      <div class="form-section">
        <label class="form-label">📁 Upload Training Content</label>
        <div class="upload-area" @drop="onDrop" @dragover.prevent @dragenter.prevent>
          <input 
            ref="fileInput" 
            type="file" 
            multiple 
            @change="onFileSelect" 
            class="file-input"
            accept=".csv,.json,.txt,.md,.py,.js,.sql"
          >
          <div class="upload-content">
            <div class="upload-icon">📂</div>
            <p>Drop files here or click to browse</p>
            <p class="upload-hint">Supports: CSV, JSON, Text, Code, Documentation</p>
          </div>
        </div>

        <!-- Selected Files -->
        <div v-if="selectedFiles.length > 0" class="selected-files">
          <h4>Selected Files:</h4>
          <div class="file-list">
            <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size">({{ formatFileSize(file.size) }})</span>
              <button @click="removeFile(index)" class="remove-btn">✕</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Output Selection -->
      <div class="form-section">
        <label class="form-label">🎯 What should Jade generate?</label>
        <div class="output-options">
          <label class="checkbox-option">
            <input type="checkbox" v-model="outputs.tool" value="tool">
            <span class="checkbox-text">🔧 Tools & Scripts</span>
            <p class="option-desc">Generate Python tools and automation scripts</p>
          </label>
          <label class="checkbox-option">
            <input type="checkbox" v-model="outputs.model" value="model">
            <span class="checkbox-text">🤖 ML Models</span>
            <p class="option-desc">Train classification/regression models from CSV data</p>
          </label>
          <label class="checkbox-option">
            <input type="checkbox" v-model="outputs.rag" value="rag">
            <span class="checkbox-text">📚 Knowledge Base</span>
            <p class="option-desc">Create searchable knowledge entries for RAG</p>
          </label>
          <label class="checkbox-option">
            <input type="checkbox" v-model="outputs.action" value="action">
            <span class="checkbox-text">⚡ Executable Actions</span>
            <p class="option-desc">Generate MCP actions for AutoRunner</p>
          </label>
        </div>
      </div>

      <!-- Tags -->
      <div class="form-section">
        <label class="form-label">🏷️ Tags (optional)</label>
        <input 
          v-model="tagsInput" 
          placeholder="e.g., data-analysis, automation, customer-risk"
          class="tags-input"
          @keyup.enter="addTag"
        >
        <div v-if="tags.length > 0" class="tags-list">
          <span v-for="(tag, index) in tags" :key="index" class="tag">
            {{ tag }}
            <button @click="removeTag(index)" class="tag-remove">✕</button>
          </span>
        </div>
      </div>

      <!-- Train Button -->
      <div class="form-section">
        <button 
          @click="startTraining" 
          :disabled="!canTrain || isTraining" 
          class="train-btn"
        >
          <span v-if="isTraining">🔄 Training Jade...</span>
          <span v-else>🚀 Start HTC Training</span>
        </button>
      </div>
    </div>

    <!-- Training Progress -->
    <div v-if="isTraining" class="training-progress">
      <div class="progress-header">
        <h3>🧠 Jade is Learning...</h3>
        <p>Session ID: {{ currentSession?.session_id }}</p>
      </div>
      <div class="progress-steps">
        <div class="step" :class="{ active: trainingStep >= 1 }">
          <span class="step-icon">📁</span>
          <span>Processing Files</span>
        </div>
        <div class="step" :class="{ active: trainingStep >= 2 }">
          <span class="step-icon">📚</span>
          <span>Creating Knowledge</span>
        </div>
        <div class="step" :class="{ active: trainingStep >= 3 }">
          <span class="step-icon">🤖</span>
          <span>Training Models</span>
        </div>
        <div class="step" :class="{ active: trainingStep >= 4 }">
          <span class="step-icon">🔧</span>
          <span>Generating Tools</span>
        </div>
        <div class="step" :class="{ active: trainingStep >= 5 }">
          <span class="step-icon">✅</span>
          <span>Complete</span>
        </div>
      </div>
    </div>

    <!-- Training Results -->
    <div v-if="trainingResults" class="training-results">
      <div class="results-header">
        <h3>🎉 Training Complete!</h3>
        <p>Session: {{ trainingResults.session_id }} | Duration: {{ trainingResults.execution_time?.toFixed(2) }}s</p>
      </div>

      <div class="generated-assets">
        <div v-for="(result, type) in trainingResults.generated" :key="type" class="asset-card">
          <div class="asset-header">
            <span class="asset-icon">{{ getAssetIcon(type) }}</span>
            <h4>{{ getAssetTitle(type) }}</h4>
            <span class="asset-status" :class="result.status">{{ result.status }}</span>
          </div>
          <div v-if="result.status === 'success'" class="asset-details">
            <p><strong>File:</strong> {{ result.file_path || result.tool_name || result.entry_id }}</p>
            <p v-if="result.description"><strong>Description:</strong> {{ result.description }}</p>
            <p v-if="result.model_type"><strong>Type:</strong> {{ result.model_type }}</p>
            <p v-if="result.accuracy"><strong>Accuracy:</strong> {{ (result.accuracy * 100).toFixed(1) }}%</p>
          </div>
          <div v-else class="asset-error">
            <p>{{ result.error || result.reason }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Training History -->
    <div class="training-history">
      <div class="history-header">
        <h3>📜 Training History</h3>
        <button @click="refreshHistory" class="refresh-btn">🔄 Refresh</button>
      </div>
      
      <div v-if="trainingHistory.length === 0" class="no-history">
        <p>No training sessions yet. Start your first HTC training above!</p>
      </div>
      
      <div v-else class="history-list">
        <div v-for="session in trainingHistory" :key="session.session_id" class="history-item">
          <div class="session-header">
            <span class="session-id">{{ session.session_id }}</span>
            <span class="session-date">{{ formatDate(session.timestamp) }}</span>
            <button @click="deleteSession(session.session_id)" class="delete-btn">🗑️</button>
          </div>
          <p class="session-task">{{ session.task }}</p>
          <div class="session-outputs">
            <span v-for="output in session.outputs_requested" :key="output" class="output-tag">
              {{ getAssetIcon(output) }} {{ output }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'HTCTrainer',
  setup() {
    // Reactive state
    const taskDescription = ref('')
    const selectedFiles = ref([])
    const outputs = ref({
      tool: true,
      model: false,
      rag: true,
      action: false
    })
    const tagsInput = ref('')
    const tags = ref([])
    const isTraining = ref(false)
    const trainingStep = ref(0)
    const currentSession = ref(null)
    const trainingResults = ref(null)
    const trainingHistory = ref([])

    // File input ref
    const fileInput = ref(null)

    // Computed properties
    const canTrain = computed(() => {
      return taskDescription.value.trim() && 
             selectedFiles.value.length > 0 && 
             Object.values(outputs.value).some(v => v)
    })

    const selectedOutputs = computed(() => {
      return Object.entries(outputs.value)
        .filter(([_, selected]) => selected)
        .map(([output, _]) => output)
    })

    // Methods
    const onFileSelect = (event) => {
      const files = Array.from(event.target.files)
      selectedFiles.value = [...selectedFiles.value, ...files]
    }

    const onDrop = (event) => {
      event.preventDefault()
      const files = Array.from(event.dataTransfer.files)
      selectedFiles.value = [...selectedFiles.value, ...files]
    }

    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1)
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const addTag = () => {
      const tag = tagsInput.value.trim()
      if (tag && !tags.value.includes(tag)) {
        tags.value.push(tag)
        tagsInput.value = ''
      }
    }

    const removeTag = (index) => {
      tags.value.splice(index, 1)
    }

    const startTraining = async () => {
      if (!canTrain.value) return

      isTraining.value = true
      trainingStep.value = 1
      trainingResults.value = null

      try {
        // Step 1: Upload files
        const formData = new FormData()
        selectedFiles.value.forEach(file => {
          formData.append('files', file)
        })
        formData.append('task_description', taskDescription.value)

        const uploadResponse = await fetch('/api/htc-trainer/upload', {
          method: 'POST',
          body: formData
        })

        if (!uploadResponse.ok) {
          throw new Error('File upload failed')
        }

        const uploadResult = await uploadResponse.json()
        const fileNames = uploadResult.uploaded_files.map(f => f.filename)

        trainingStep.value = 2

        // Step 2: Start training
        const trainingResponse = await fetch('/api/htc-trainer/train', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            task_description: taskDescription.value,
            files: fileNames,
            desired_outputs: selectedOutputs.value,
            tags: tags.value
          })
        })

        if (!trainingResponse.ok) {
          throw new Error('Training failed')
        }

        const result = await trainingResponse.json()
        currentSession.value = result

        // Simulate progress steps
        for (let step = 3; step <= 5; step++) {
          await new Promise(resolve => setTimeout(resolve, 1000))
          trainingStep.value = step
        }

        trainingResults.value = result
        await refreshHistory()

      } catch (error) {
        console.error('Training error:', error)
        alert('Training failed: ' + error.message)
      } finally {
        isTraining.value = false
        trainingStep.value = 0
      }
    }

    const refreshHistory = async () => {
      try {
        const response = await fetch('/api/htc-trainer/history')
        if (response.ok) {
          const data = await response.json()
          trainingHistory.value = data.sessions || []
        }
      } catch (error) {
        console.error('Failed to fetch history:', error)
      }
    }

    const deleteSession = async (sessionId) => {
      if (!confirm('Delete this training session and all generated assets?')) return

      try {
        const response = await fetch(`/api/htc-trainer/session/${sessionId}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          await refreshHistory()
        }
      } catch (error) {
        console.error('Failed to delete session:', error)
      }
    }

    const getAssetIcon = (type) => {
      const icons = {
        tool: '🔧',
        model: '🤖',
        rag: '📚',
        action: '⚡'
      }
      return icons[type] || '📄'
    }

    const getAssetTitle = (type) => {
      const titles = {
        tool: 'Generated Tool',
        model: 'ML Model',
        rag: 'Knowledge Entry',
        action: 'MCP Action'
      }
      return titles[type] || 'Asset'
    }

    const formatDate = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
      refreshHistory()
    })

    return {
      // State
      taskDescription,
      selectedFiles,
      outputs,
      tagsInput,
      tags,
      isTraining,
      trainingStep,
      currentSession,
      trainingResults,
      trainingHistory,
      fileInput,
      
      // Computed
      canTrain,
      selectedOutputs,
      
      // Methods
      onFileSelect,
      onDrop,
      removeFile,
      formatFileSize,
      addTag,
      removeTag,
      startTraining,
      refreshHistory,
      deleteSession,
      getAssetIcon,
      getAssetTitle,
      formatDate
    }
  }
}
</script>

<style scoped>
.htc-trainer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header-section {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #6b7280;
  max-width: 600px;
  margin: 0 auto;
}

.training-interface {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.form-section {
  margin-bottom: 2rem;
}

.form-label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.task-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
  resize: vertical;
}

.task-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-area:hover {
  border-color: #3b82f6;
}

.file-input {
  display: none;
}

.upload-content {
  pointer-events: none;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-hint {
  color: #6b7280;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.selected-files {
  margin-top: 1rem;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 6px;
  gap: 0.5rem;
}

.file-name {
  flex: 1;
  font-weight: 500;
}

.file-size {
  color: #6b7280;
  font-size: 0.9rem;
}

.remove-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
}

.remove-btn:hover {
  background: #fee2e2;
}

.output-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.checkbox-option {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.checkbox-option:hover {
  border-color: #3b82f6;
}

.checkbox-option input[type="checkbox"] {
  margin-right: 0.5rem;
}

.checkbox-text {
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.option-desc {
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0;
}

.tags-input {
  width: 100%;
  padding: 0.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 1rem;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background: #e0e7ff;
  color: #3730a3;
  border-radius: 20px;
  font-size: 0.9rem;
  gap: 0.25rem;
}

.tag-remove {
  background: none;
  border: none;
  color: #3730a3;
  cursor: pointer;
  font-size: 0.8rem;
}

.train-btn {
  width: 100%;
  padding: 1rem 2rem;
  background: linear-gradient(to right, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.train-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.training-progress {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.progress-header {
  text-align: center;
  margin-bottom: 2rem;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0.4;
  transition: opacity 0.3s;
}

.step.active {
  opacity: 1;
}

.step-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.training-results {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.results-header {
  text-align: center;
  margin-bottom: 2rem;
}

.generated-assets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.asset-card {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
}

.asset-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.asset-icon {
  font-size: 1.5rem;
}

.asset-status {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-left: auto;
}

.asset-status.success {
  background: #dcfce7;
  color: #166534;
}

.asset-status.error {
  background: #fee2e2;
  color: #dc2626;
}

.asset-details p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.asset-error {
  color: #dc2626;
}

.training-history {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.refresh-btn {
  background: none;
  border: 1px solid #e5e7eb;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.no-history {
  text-align: center;
  color: #6b7280;
  padding: 2rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.session-id {
  font-family: monospace;
  font-weight: 600;
  color: #3b82f6;
}

.session-date {
  color: #6b7280;
  font-size: 0.9rem;
}

.delete-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0.25rem;
}

.session-task {
  margin: 0.5rem 0;
  color: #374151;
}

.session-outputs {
  display: flex;
  gap: 0.5rem;
}

.output-tag {
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}
</style>