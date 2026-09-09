<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { EyeIcon, EyeSlashIcon, EnvelopeIcon, LockClosedIcon, UserIcon, PhoneIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const errors = reactive({})

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  password_confirmation: '',
  phone: '',
  job_title: '',
})

const validateForm = () => {
  Object.keys(errors).forEach((key) => delete errors[key])
  let valid = true
  
  if (!form.first_name.trim()) {
    errors.first_name = 'First name is required'
    valid = false
  }
  
  if (!form.last_name.trim()) {
    errors.last_name = 'Last name is required'
    valid = false
  }
  
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
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    valid = false
  }
  
  if (form.password !== form.password_confirmation) {
    errors.password_confirmation = 'Passwords do not match'
    valid = false
  }
  
  return valid
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    await authStore.register(form)
    toast.success('Account created successfully!')
    router.push('/dashboard')
  } catch (error) {
    if (error.response?.data?.errors) {
      Object.assign(errors, error.response.data.errors)
    } else {
      toast.error(error.response?.data?.message || 'Registration failed. Please try again.')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-md mx-auto px-4">
    <div class="text-center mb-8">
      <h1 class="text-2xl font-bold text-secondary-900">Create your account</h1>
      <p class="mt-2 text-secondary-600">Start managing your projects today</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6" novalidate>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="first_name" class="label">First name</label>
          <div class="relative mt-1">
            <UserIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
            <input
              id="first_name"
              v-model="form.first_name"
              type="text"
              autocomplete="given-name"
              :class="['input pl-10', { 'input-error': errors.first_name }]"
              placeholder="John"
              :disabled="loading"
            />
          </div>
          <p v-if="errors.first_name" class="mt-1 text-sm text-danger-600">{{ errors.first_name }}</p>
        </div>
        
        <div>
          <label for="last_name" class="label">Last name</label>
          <div class="relative mt-1">
            <UserIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
            <input
              id="last_name"
              v-model="form.last_name"
              type="text"
              autocomplete="family-name"
              :class="['input pl-10', { 'input-error': errors.last_name }]"
              placeholder="Doe"
              :disabled="loading"
            />
          </div>
          <p v-if="errors.last_name" class="mt-1 text-sm text-danger-600">{{ errors.last_name }}</p>
        </div>
      </div>

      <div>
        <label for="email" class="label">Email address</label>
        <div class="relative mt-1">
          <EnvelopeIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
          <input
            id="email"
            v-model="form.email"
            type="email"
            autocomplete="email"
            :class="['input pl-10', { 'input-error': errors.email }]"
            placeholder="you@example.com"
            :disabled="loading"
          />
        </div>
        <p v-if="errors.email" class="mt-1 text-sm text-danger-600">{{ errors.email }}</p>
      </div>

      <div>
        <label for="phone" class="label">Phone (optional)</label>
        <div class="relative mt-1">
          <PhoneIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
          <input
            id="phone"
            v-model="form.phone"
            type="tel"
            autocomplete="tel"
            class="input pl-10"
            placeholder="+1 (555) 000-0000"
            :disabled="loading"
          />
        </div>
      </div>

      <div>
        <label for="job_title" class="label">Job Title (optional)</label>
        <input
          id="job_title"
          v-model="form.job_title"
          type="text"
          autocomplete="organization-title"
          class="input mt-1"
          placeholder="Software Engineer"
          :disabled="loading"
        />
      </div>

      <div>
        <label for="password" class="label">Password</label>
        <div class="relative mt-1">
          <LockClosedIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
          <input
            id="password"
            :type="showPassword ? 'text' : 'password'"
            v-model="form.password"
            autocomplete="new-password"
            :class="['input pl-10 pr-10', { 'input-error': errors.password }]"
            placeholder="••••••••"
            :disabled="loading"
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

      <div>
        <label for="password_confirmation" class="label">Confirm password</label>
        <div class="relative mt-1">
          <LockClosedIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
          <input
            id="password_confirmation"
            :type="showConfirmPassword ? 'text' : 'password'"
            v-model="form.password_confirmation"
            autocomplete="new-password"
            :class="['input pl-10 pr-10', { 'input-error': errors.password_confirmation }]"
            placeholder="••••••••"
            :disabled="loading"
          />
          <button
            type="button"
            @click="showConfirmPassword = !showConfirmPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
            :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
          >
            <component :is="showConfirmPassword ? EyeSlashIcon : EyeIcon" class="w-5 h-5" />
          </button>
        </div>
        <p v-if="errors.password_confirmation" class="mt-1 text-sm text-danger-600">{{ errors.password_confirmation }}</p>
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
          Creating account...
        </span>
        <span v-else>Create account</span>
      </button>
    </form>

    <div class="mt-6 text-center">
      <p class="text-secondary-600">
        Already have an account? 
        <RouterLink to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
          Sign in
        </RouterLink>
      </p>
    </div>
  </div>
</template>