<script setup>
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores/ui'
import { HomeIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const uiStore = useUIStore()
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4">
    <div class="text-center max-w-md">
      <div class="w-24 h-24 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <MagnifyingGlassIcon class="w-12 h-12 text-secondary-400" />
      </div>
      
      <h1 class="text-4xl font-bold text-secondary-900 mb-2">404</h1>
      <h2 class="text-xl text-secondary-600 mb-4">Page Not Found</h2>
      <p class="text-secondary-500 mb-8">
        Sorry, we couldn't find the page you're looking for. It might have been moved or doesn't exist.
      </p>
      
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          @click="() => router.push('/dashboard')"
          class="btn-primary"
        >
          <HomeIcon class="w-5 h-5 mr-2" />
          Go to Dashboard
        </button>
        <button
          @click="() => router.back()"
          class="btn-secondary"
        >
          Go Back
        </button>
      </div>
      
      <div class="mt-8 text-sm text-secondary-400">
        <p>Or try searching for what you need:</p>
        <input
          type="search"
          placeholder="Search..."
          class="input mt-2 max-w-xs mx-auto"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Not found view styles */
</style>