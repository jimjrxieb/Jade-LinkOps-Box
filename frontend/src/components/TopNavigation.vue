<template>
  <nav class="top-navigation">
    <div class="nav-container">
      <!-- Logo/Brand -->
      <router-link to="/" class="nav-brand">
        <span class="brand-icon">💠</span>
        <span class="brand-text">LinkOps AI Box</span>
      </router-link>

      <!-- Navigation Links -->
      <div class="nav-links">
        <router-link to="/" class="nav-link" exact-active-class="active">
          🏠 Home
        </router-link>
        <router-link to="/dashboard" class="nav-link" active-class="active">
          📊 Dashboard
        </router-link>
        <router-link to="/htc-trainer" class="nav-link" active-class="active">
          🧠 HTC Learning
        </router-link>
        <a href="/api/docs" target="_blank" class="nav-link">
          📚 API Docs
        </a>
      </div>

      <!-- Status Indicator -->
      <div class="nav-status">
        <div class="status-dot"></div>
        <span class="status-text">Jade Online</span>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'TopNavigation'
}
</script>

<style scoped>
.top-navigation {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0.75rem 0;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
}

.brand-icon {
  font-size: 1.5rem;
  background: linear-gradient(135deg, #00f5ff, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-text {
  background: linear-gradient(135deg, #00f5ff, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #00f5ff;
  background: rgba(0, 245, 255, 0.1);
}

.nav-link.active {
  color: #00f5ff;
  background: rgba(0, 245, 255, 0.1);
  border: 1px solid rgba(0, 245, 255, 0.3);
}

.nav-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #22c55e;
  font-size: 0.8rem;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-text {
  font-weight: 500;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* Mobile responsive */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
  }
  
  .nav-links {
    gap: 1rem;
  }
  
  .nav-link {
    padding: 0.5rem;
    font-size: 0.8rem;
  }
  
  .brand-text {
    display: none;
  }
  
  .nav-status {
    font-size: 0.7rem;
  }
}
</style>