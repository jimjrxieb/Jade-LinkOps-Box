<template>
  <Teleport to="body">
    <div
      class="fixed top-4 right-4 z-50 flex flex-col gap-2 min-w-[300px] max-w-[400px]"
      :class="{ 'pointer-events-none': !hasToasts }"
    >
      <TransitionGroup
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform translate-x-full opacity-0"
        enter-to-class="transform translate-x-0 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform translate-x-0 opacity-100"
        leave-to-class="transform translate-x-full opacity-0"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="card-glass pointer-events-auto flex items-start gap-3 p-4 shadow-glow"
          :class="{
            'border-jade-500/30': toast.type === 'success',
            'border-red-500/30': toast.type === 'error',
            'border-yellow-500/30': toast.type === 'warning',
            'border-cyan-500/30': toast.type === 'info'
          }"
        >
          <!-- Icon -->
          <div
            class="flex-shrink-0 w-5 h-5"
            :class="{
              'text-jade-400': toast.type === 'success',
              'text-red-400': toast.type === 'error',
              'text-yellow-400': toast.type === 'warning',
              'text-cyan-400': toast.type === 'info'
            }"
          >
            <span v-if="toast.type === 'success'">✅</span>
            <span v-else-if="toast.type === 'error'">❌</span>
            <span v-else-if="toast.type === 'warning'">⚠️</span>
            <span v-else>ℹ️</span>
          </div>

          <!-- Content -->
          <div class="flex-1 pt-1">
            <div class="text-sm">{{ toast.message }}</div>
          </div>

          <!-- Close Button -->
          <button
            class="flex-shrink-0 text-gray-400 hover:text-white transition-colors"
            @click="removeToast(toast.id)"
          >
            <span class="sr-only">Close</span>
            <svg class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
              <path
                fill-rule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useJadeStore } from '@/store/useJadeStore'

const store = useJadeStore()
const toasts = computed(() => store.toasts)
const hasToasts = computed(() => toasts.value.length > 0)

const removeToast = (id) => {
  store.removeToast(id)
}
</script> 