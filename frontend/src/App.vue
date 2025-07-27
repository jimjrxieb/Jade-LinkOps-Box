<template>
  <div id="app">
    <TopNavigation v-if="showNavigation" />
    <router-view />
    <SessionTimer v-if="store.isAuthenticated" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '@/store/useMainStore';
import SessionTimer from '@/components/SessionTimer.vue';
import TopNavigation from '@/components/TopNavigation.vue';

const store = useMainStore();
const route = useRoute();

// Show navigation on all pages except login
const showNavigation = computed(() => {
  return route.path !== '/login';
});
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
