<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { pinia } from '@/stores/pinia'
import { useToast } from 'vue-toastification'
import { EyeIcon, EyeSlashIcon, EnvelopeIcon, LockClosedIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore(pinia)
const toast = useToast()

const showPassword = ref(false)
const loading = ref(false)
const errors = reactive({})

const form = reactive({
  email: '',
  password: '',
  remember: false,
})

const validateForm = () => {
  Object.keys(errors).forEach((key) => delete errors[key])
  let valid = true
  
  if (!form.email) {
    errors.email = 'Email is required'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Please enter a valid email'
    valid = false
  }
  
  if (!form.password) {
    errors.password = 'Password is required'
    valid = false
  }
  
  return valid
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    await authStore.login({
      email: form.email,
      password: form.password,
      remember: form.remember,
    })
    
    toast.success('Welcome back!')
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    if (error.response?.data?.errors) {
      Object.assign(errors, error.response.data.errors)
    } else {
      toast.error(error.response?.data?.message || 'Login failed. Please try again.')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-md mx-auto px-4">
    <div class="text-center mb-8">
      <h1 class="text-2xl font-bold text-secondary-900">Sign in to your account</h1>
      <p class="mt-2 text-secondary-600">Enter your credentials to access the dashboard</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6" novalidate>
      <div>
        <label for="email" class="label">Email address</label>
        <div class="relative">
          <EnvelopeIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
          <input
            id="email"
            v-model="form.email"
            type="email"
            autocomplete="email"
            :class="['input pl-10', { 'input-error': errors.email }]"
            placeholder="you@example.com"
            :disabled="loading"
            @blur="validateForm"
          />
        </div>
        <p v-if="errors.email" class="mt-1 text-sm text-danger-600">{{ errors.email }}</p>
      </div>

      <div>
        <div class="flex items-center justify-between">
          <label for="password" class="label mb-0">Password</label>
          <RouterLink to="/forgot-password" class="text-sm text-primary-600 hover:text-primary-700">
            Forgot password?
          </RouterLink>
        </div>
        <div class="relative mt-1">
          <LockClosedIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
          <input
            id="password"
            :type="showPassword ? 'text' : 'password'"
            v-model="form.password"
            autocomplete="current-password"
            :class="['input pl-10 pr-10', { 'input-error': errors.password }]"
            placeholder="••••••••"
            :disabled="loading"
            @blur="validateForm"
          />
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
          >
            <component :is="showPassword ? EyeSlashIcon : EyeIcon" class="w-5 h-5" />
          </button>
        </div>
        <p v-if="errors.password" class="mt-1 text-sm text-danger-600">{{ errors.password }}</p>
      </div>

      <div class="flex items-center justify-between">
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            v-model="form.remember"
            class="w-4 h-4 rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
          >
          <span class="text-sm text-secondary-600">Remember me</span>
        </label>
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="btn-primary w-full py-3"
      >
        <span v-if="loading" class="flex items-center justify-center gap-2">
          <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Signing in...
        </span>
        <span v-else>Sign in</span>
      </button>
    </form>

    <div class="mt-6 text-center">
      <p class="text-secondary-600">
        Don't have an account? 
        <RouterLink to="/register" class="text-primary-600 hover:text-primary-700 font-medium">
          Sign up
        </RouterLink>
      </p>
    </div>

    <!-- Demo credentials -->
    <div class="mt-8 p-4 bg-secondary-50 rounded-lg border border-secondary-200">
      <p class="text-sm font-medium text-secondary-700 mb-2">Demo Credentials:</p>
      <div class="space-y-1 text-sm text-secondary-600 font-mono">
        <p>Admin: admin@erp.local / password123</p>
        <p>PM: pm1@erp.local / password123</p>
        <p>Developer: dev1@erp.local / password123</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Login view styles */
</style>