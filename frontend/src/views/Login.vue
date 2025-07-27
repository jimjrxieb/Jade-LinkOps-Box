<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 to-black flex items-center justify-center">
    <div class="w-full max-w-md p-8 card-glass">
      <!-- Logo and Title -->
      <div class="text-center mb-8">
        <div class="text-6xl mb-4 animate-glow">🔒</div>
        <h2 class="text-3xl font-bold text-jade drop-shadow glow">LinkOps Box</h2>
        <p class="text-cyan-400 mt-2">Secure Infrastructure Management</p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- Username Field -->
        <div>
          <label for="username" class="input-label">Username</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="input-field"
            :class="{ 'border-red-500': errors.username }"
            placeholder="Enter your username"
            required
            @keydown.enter="handleLogin"
          />
          <p v-if="errors.username" class="mt-1 text-sm text-red-400">
            {{ errors.username }}
          </p>
        </div>

        <!-- Password Field -->
        <div>
          <label for="password" class="input-label">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="input-field"
            :class="{ 'border-red-500': errors.password }"
            placeholder="Enter your password"
            required
            @keydown.enter="handleLogin"
          />
          <p v-if="errors.password" class="mt-1 text-sm text-red-400">
            {{ errors.password }}
          </p>
        </div>

        <!-- Remember Me -->
        <div class="flex items-center">
          <input
            id="remember"
            v-model="form.remember"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-600 bg-gray-700 text-jade-500 focus:ring-jade-500"
          />
          <label for="remember" class="ml-2 text-sm text-gray-300">
            Remember me
          </label>
        </div>

        <!-- Login Button -->
        <button
          type="submit"
          class="btn-primary w-full"
          :class="{ 'opacity-75 cursor-wait': isLoading }"
          :disabled="isLoading"
        >
          <span v-if="isLoading">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Logging in...
          </span>
          <span v-else>Login</span>
        </button>

        <!-- Error Message -->
        <div v-if="error" class="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {{ error }}
        </div>

        <!-- Demo Credentials -->
        <div class="text-center space-y-2">
          <p class="text-sm">
            <span class="text-gray-400">Demo credentials:</span>
          </p>
          <div class="flex flex-col gap-1">
            <code class="px-2 py-1 rounded bg-backdrop-light text-jade font-mono text-sm">
              Username: linkops-demo
            </code>
            <code class="px-2 py-1 rounded bg-backdrop-light text-jade font-mono text-sm">
              Password: demo123
            </code>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/store/useMainStore'

const router = useRouter()
const store = useMainStore()
const isLoading = ref(false)
const error = ref('')
const errors = reactive({
  username: '',
  password: ''
})

const form = reactive({
  username: '',
  password: '',
  remember: false
})

async function handleLogin() {
  // Reset errors
  error.value = ''
  errors.username = ''
  errors.password = ''

  // Validate
  if (!form.username) {
    errors.username = 'Username is required'
    return
  }
  if (!form.password) {
    errors.password = 'Password is required'
    return
  }

  try {
    isLoading.value = true

    // Demo credentials check
    if (form.username === 'linkops-demo' && form.password === 'demo123') {
      // Create a demo JWT token (for demonstration purposes)
      const demoToken = 'demo.' + btoa(JSON.stringify({
        sub: 'linkops-demo',
        role: 'full',
        exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours
      })) + '.demo'

      // Set token in store
      await store.setToken(demoToken)

      // Store remember preference
      if (form.remember) {
        localStorage.setItem('remember-demo', 'true')
      }

      // Redirect to dashboard
      router.push('/')
      return
    }

    // For non-demo credentials, try real API
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: form.username,
        password: form.password
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.message || 'Login failed')
    }

    // Set token in store
    await store.setToken(data.token)

    // Store remember preference
    if (form.remember) {
      localStorage.setItem('remember', 'true')
    }

    // Redirect to dashboard
    router.push('/')
  } catch (err) {
    error.value = 'Invalid username or password'
  } finally {
    isLoading.value = false
  }
}

// Auto-fill demo credentials in development
if (import.meta.env.DEV) {
  form.username = 'linkops-demo'
  form.password = 'demo123'
}
</script>

<style scoped>
/* loader spinner animation handled by Tailwind utility classes */
</style>
