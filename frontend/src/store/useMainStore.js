import { defineStore } from 'pinia';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { jwtDecode } from 'jwt-decode';

const ACTIVITY_REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes in ms
const WARNING_THRESHOLD = 5 * 60 * 1000; // Show warning 5 minutes before expiry

export const useMainStore = defineStore('main', {
  state: () => ({
    token: null,
    role: 'slim',
    user: null,
    logoutTimer: null,
    warningTimer: null,
    lastActivity: Date.now(),
    showSessionWarning: false,
    sessionTimeLeft: 0,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isFullAccess: (state) => state.role === 'full',
    currentUser: (state) => state.user,
  },

  actions: {
    async setToken(token) {
      this.token = token;
      if (token) {
        // Save token to localStorage
        localStorage.setItem('token', token);
        
        // Set axios auth header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        try {
          const { exp, sub, role } = jwtDecode(token);
          const expiresIn = exp * 1000 - Date.now();

          // Clear existing timers
          this.clearTimers();

          if (expiresIn > 0) {
            // Set warning timer
            const warningTime = expiresIn - WARNING_THRESHOLD;
            if (warningTime > 0) {
              this.warningTimer = setTimeout(() => {
                this.showSessionWarning = true;
                this.startSessionCountdown(expiresIn - warningTime);
              }, warningTime);
            }

            // Set logout timer
            this.logoutTimer = setTimeout(() => {
              this.logout();
            }, expiresIn);

            // Update user info
            this.setUser(sub);
            this.setRole(role);
          } else {
            this.logout();
          }
        } catch (e) {
          console.error('Failed to decode token:', e);
          this.logout();
        }
      } else {
        // Remove token from localStorage
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
      }
    },

    clearTimers() {
      if (this.logoutTimer) {
        clearTimeout(this.logoutTimer);
        this.logoutTimer = null;
      }
      if (this.warningTimer) {
        clearTimeout(this.warningTimer);
        this.warningTimer = null;
      }
    },

    startSessionCountdown(duration) {
      this.sessionTimeLeft = Math.floor(duration / 1000);
      const countdownInterval = setInterval(() => {
        this.sessionTimeLeft--;
        if (this.sessionTimeLeft <= 0) {
          clearInterval(countdownInterval);
        }
      }, 1000);
    },

    async refreshSession() {
      try {
        const response = await axios.post('/auth/refresh');
        if (response.data.access_token) {
          this.setToken(response.data.access_token);
          this.showSessionWarning = false;
          return true;
        }
      } catch (e) {
        console.error('Failed to refresh session:', e);
        this.logout();
        return false;
      }
    },

    async silentRefresh() {
      const now = Date.now();
      if (now - this.lastActivity > ACTIVITY_REFRESH_THRESHOLD) {
        this.lastActivity = now;
        return this.refreshSession();
      }
      return true;
    },

    updateActivity() {
      this.lastActivity = Date.now();
    },

    setRole(role) {
      this.role = role;
    },

    setUser(username) {
      this.user = username;
    },

    async logout() {
      try {
        // Call logout endpoint to clear refresh token cookie
        await axios.post('/auth/logout');
      } catch (e) {
        console.error('Error during logout:', e);
      }

      // Clear all auth state
      this.clearTimers();
      this.token = null;
      this.role = 'slim';
      this.user = null;
      this.showSessionWarning = false;
      this.sessionTimeLeft = 0;

      // Clear localStorage
      localStorage.removeItem('token');
      
      // Clear axios auth header
      delete axios.defaults.headers.common['Authorization'];

      // Redirect to login
      const router = useRouter();
      router.push('/login');
    },

    // Initialize auth state
    async initializeAuth() {
      // Try to refresh the session
      const success = await this.refreshSession();
      if (!success) {
        this.logout();
      }
    },
  },

});
