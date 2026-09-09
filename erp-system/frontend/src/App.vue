<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="min-h-screen">
    <router-view v-slot="{ Component }">
      <component
        :is="route.meta?.layout === 'auth' ? AuthLayout : DefaultLayout"
      >
        <component :is="Component" />
      </component>
    </router-view>
  </div>
</template>

<style scoped>
/* Global styles are handled by main.css. */
</style>