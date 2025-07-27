import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'

// Import styles
import './assets/tailwind.css'

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('./views/LandingAssistant.vue')
    },
    {
      path: '/landing',
      component: () => import('./views/LandingAssistant.vue')
    },
    {
      path: '/login',
      component: () => import('./views/Login.vue')
    },
    {
      path: '/dashboard',
      component: () => import('./views/DemoDashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/htc-trainer',
      component: () => import('./components/HTCTrainer.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Auth guard
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = localStorage.getItem('token')
    if (!token) {
      next('/login')
      return
    }
  }
  next()
})

// Create Pinia store
const pinia = createPinia()

// Create and mount app
const app = createApp(App)
app.use(pinia)
app.use(router)
app.mount('#app')
