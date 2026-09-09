<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { UserIcon, CameraIcon } from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const toast = useToast()

const activeTab = ref('profile')
const loading = ref(false)
const avatarFile = ref(null)
const avatarPreview = ref(null)

const profileForm = reactive({
  first_name: authStore.user?.first_name || '',
  last_name: authStore.user?.last_name || '',
  email: authStore.user?.email || '',
  phone: authStore.user?.phone || '',
  job_title: authStore.user?.job_title || '',
  timezone: authStore.user?.timezone || 'UTC',
  locale: authStore.user?.locale || 'en',
})

const passwordForm = reactive({
  current_password: '',
  password: '',
  password_confirmation: '',
})

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const timezones = [
  'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
  'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Asia/Tokyo', 'Asia/Shanghai',
  'Australia/Sydney', 'Pacific/Auckland',
]

const locales = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'ja', name: 'Japanese' },
  { code: 'zh', name: 'Chinese' },
]

async function updateProfile() {
  loading.value = true
  try {
    await authStore.updateProfile(profileForm)
    toast.success('Profile updated successfully')
  } catch (error) {
    toast.error('Failed to update profile')
  } finally {
    loading.value = false
  }
}

async function updatePassword() {
  if (passwordForm.password !== passwordForm.password_confirmation) {
    toast.error('Passwords do not match')
    return
  }
  
  loading.value = true
  try {
    await authStore.updatePassword(passwordForm)
    toast.success('Password updated successfully')
    passwordForm.current_password = ''
    passwordForm.password = ''
    passwordForm.password_confirmation = ''
  } catch (error) {
    toast.error(error.response?.data?.message || 'Failed to update password')
  } finally {
    loading.value = false
  }
}

function handleAvatarUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  
  if (file.size > 2 * 1024 * 1024) {
    toast.error('File size must be less than 2MB')
    return
  }
  
  if (!file.type.startsWith('image/')) {
    toast.error('File must be an image')
    return
  }
  
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

function removeAvatar() {
  avatarFile.value = null
  avatarPreview.value = null
}
</script>

<template>
  <div class="space-y-6">
    <!-- Tabs -->
    <div class="border-b border-secondary-200">
      <nav class="flex gap-8" aria-label="Settings tabs">
        <button
          v-for="tab in ['profile', 'password']"
          :key="tab"
          @click="activeTab = tab"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab ? 'border-primary-500 text-primary-600' : 'border-transparent text-secondary-500 hover:text-secondary-700'
          ]"
        >
          {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
        </button>
      </nav>
    </div>

    <!-- Profile Tab -->
    <div v-if="activeTab === 'profile'" class="space-y-6">
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-secondary-900 mb-6">Profile Information</h2>
        
        <!-- Avatar -->
        <div class="flex items-center gap-6 mb-6">
          <div class="relative">
            <img
              :src="avatarPreview || authStore.userAvatar"
              :alt="authStore.userName"
              class="w-24 h-24 rounded-full bg-secondary-100"
            >
            <label class="absolute bottom-0 right-0 bg-primary-600 text-white p-2 rounded-full cursor-pointer hover:bg-primary-700 transition-colors">
              <CameraIcon class="w-5 h-5" />
              <input type="file" @change="handleAvatarUpload" accept="image/*" class="sr-only" />
            </label>
          </div>
          <div>
            <h3 class="font-medium text-secondary-900">Profile Photo</h3>
            <p class="text-sm text-secondary-500">JPG, PNG up to 2MB</p>
            <button v-if="avatarPreview" @click="removeAvatar" class="text-sm text-danger-600 hover:text-danger-700 mt-1">
              Remove photo
            </button>
          </div>
        </div>

        <form @submit.prevent="updateProfile" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="first_name" class="label">First Name</label>
              <input
                id="first_name"
                v-model="profileForm.first_name"
                type="text"
                class="input mt-1"
                required
                :disabled="loading"
              />
            </div>
            
            <div>
              <label for="last_name" class="label">Last Name</label>
              <input
                id="last_name"
                v-model="profileForm.last_name"
                type="text"
                class="input mt-1"
                required
                :disabled="loading"
              />
            </div>
          </div>

          <div>
            <label for="email" class="label">Email Address</label>
            <input
              id="email"
              v-model="profileForm.email"
              type="email"
              class="input mt-1"
              required
              :disabled="loading"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="phone" class="label">Phone Number</label>
              <input
                id="phone"
                v-model="profileForm.phone"
                type="tel"
                class="input mt-1"
                :disabled="loading"
              />
            </div>
            
            <div>
              <label for="job_title" class="label">Job Title</label>
              <input
                id="job_title"
                v-model="profileForm.job_title"
                type="text"
                class="input mt-1"
                :disabled="loading"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="timezone" class="label">Timezone</label>
              <select
                id="timezone"
                v-model="profileForm.timezone"
                class="input mt-1"
                :disabled="loading"
              >
                <option v-for="tz in timezones" :key="tz" :value="tz">{{ tz }}</option>
              </select>
            </div>
            
            <div>
              <label for="locale" class="label">Language</label>
              <select
                id="locale"
                v-model="profileForm.locale"
                class="input mt-1"
                :disabled="loading"
              >
                <option v-for="loc in locales" :key="loc.code" :value="loc.code">{{ loc.name }}</option>
              </select>
            </div>
          </div>

          <div class="flex justify-end pt-4 border-t border-secondary-100">
            <button type="submit" :disabled="loading" class="btn-primary">
              {{ loading ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Password Tab -->
    <div v-if="activeTab === 'password'" class="space-y-6">
      <div class="card p-6 max-w-md">
        <h2 class="text-lg font-semibold text-secondary-900 mb-6">Change Password</h2>
        
        <form @submit.prevent="updatePassword" class="space-y-6">
          <div>
            <label for="current_password" class="label">Current Password</label>
            <div class="relative mt-1">
              <input
                id="current_password"
                :type="showCurrentPassword ? 'text' : 'password'"
                v-model="passwordForm.current_password"
                class="input pr-10"
                required
                :disabled="loading"
                autocomplete="current-password"
              />
              <button
                type="button"
                @click="showCurrentPassword = !showCurrentPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
              >
                <EyeIcon v-if="showCurrentPassword" class="w-5 h-5" />
                <EyeSlashIcon v-else class="w-5 h-5" />
              </button>
            </div>
          </div>

          <div>
            <label for="password" class="label">New Password</label>
            <div class="relative mt-1">
              <input
                id="password"
                :type="showNewPassword ? 'text' : 'password'"
                v-model="passwordForm.password"
                class="input pr-10"
                required
                :disabled="loading"
                autocomplete="new-password"
                minlength="8"
              />
              <button
                type="button"
                @click="showNewPassword = !showNewPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
              >
                <EyeIcon v-if="showNewPassword" class="w-5 h-5" />
                <EyeSlashIcon v-else class="w-5 h-5" />
              </button>
            </div>
            <p class="mt-1 text-sm text-secondary-500">Must be at least 8 characters</p>
          </div>

          <div>
            <label for="password_confirmation" class="label">Confirm New Password</label>
            <div class="relative mt-1">
              <input
                id="password_confirmation"
                :type="showConfirmPassword ? 'text' : 'password'"
                v-model="passwordForm.password_confirmation"
                class="input pr-10"
                required
                :disabled="loading"
                autocomplete="new-password"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
              >
                <EyeIcon v-if="showConfirmPassword" class="w-5 h-5" />
                <EyeSlashIcon v-else class="w-5 h-5" />
              </button>
            </div>
          </div>

          <div class="flex justify-end pt-4 border-t border-secondary-100">
            <button type="submit" :disabled="loading" class="btn-primary">
              {{ loading ? 'Updating...' : 'Update Password' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { h } from 'vue'
import { EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
</script>

<style scoped>
/* Profile settings styles */
</style>