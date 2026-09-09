<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { useToast } from 'vue-toastification'

const authStore = useAuthStore()
const uiStore = useUIStore()
const toast = useToast()

const preferences = reactive({
  theme: uiStore.theme,
  language: authStore.user?.locale || 'en',
  timezone: authStore.user?.timezone || 'UTC',
  date_format: 'MM/DD/YYYY',
  time_format: '12h',
  email_notifications: true,
  weekly_summary: true,
  project_updates: true,
  invoice_reminders: true,
  task_assignments: true,
  desktop_notifications: false,
  sound_notifications: false,
  compact_mode: uiStore.sidebarCollapsed,
  auto_save: true,
  items_per_page: 15,
})

const timezones = [
  'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
  'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Asia/Tokyo', 'Asia/Shanghai',
  'Australia/Sydney', 'Pacific/Auckland',
]

const dateFormats = [
  { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (US)' },
  { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (EU)' },
  { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (ISO)' },
]

const timeFormats = [
  { value: '12h', label: '12 Hour (1:30 PM)' },
  { value: '24h', label: '24 Hour (13:30)' },
]

const pageSizes = [10, 15, 25, 50, 100]

async function savePreferences() {
  try {
    // Update UI store immediately
    uiStore.theme = preferences.theme
    uiStore.sidebarCollapsed = preferences.compact_mode
    
    // Update user preferences on server
    await authStore.updateProfile({
      locale: preferences.language,
      timezone: preferences.timezone,
    })
    
    toast.success('Preferences saved successfully')
  } catch (error) {
    toast.error('Failed to save preferences')
  }
}

function resetToDefaults() {
  preferences.theme = 'light'
  preferences.language = 'en'
  preferences.timezone = 'UTC'
  preferences.date_format = 'MM/DD/YYYY'
  preferences.time_format = '12h'
  preferences.email_notifications = true
  preferences.weekly_summary = true
  preferences.project_updates = true
  preferences.invoice_reminders = true
  preferences.task_assignments = true
  preferences.desktop_notifications = false
  preferences.sound_notifications = false
  preferences.compact_mode = false
  preferences.auto_save = true
  preferences.items_per_page = 15
  
  uiStore.theme = 'light'
  uiStore.sidebarCollapsed = false
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">Preferences</h1>
        <p class="text-secondary-600 mt-1">Customize your experience</p>
      </div>
      <button @click="savePreferences" class="btn-primary">
        Save Changes
      </button>
    </div>

    <!-- Appearance -->
    <div class="card p-6">
      <h2 class="text-lg font-semibold text-secondary-900 mb-6 flex items-center gap-2">
        <PaintBrushIcon class="w-5 h-5" />
        Appearance
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label class="label">Theme</label>
          <div class="grid grid-cols-2 gap-3 mt-1">
            <label class="relative cursor-pointer">
              <input type="radio" v-model="preferences.theme" value="light" class="sr-only peer" />
              <div class="p-4 border-2 rounded-lg text-center transition-colors peer-checked:border-primary-500 peer-checked:bg-primary-50 peer-checked:ring-2 peer-checked:ring-primary-500 hover:border-primary-300">
                <SunIcon class="w-8 h-8 mx-auto mb-2 text-warning-500" />
                <p class="font-medium text-secondary-900">Light</p>
              </div>
            </label>
            <label class="relative cursor-pointer">
              <input type="radio" v-model="preferences.theme" value="dark" class="sr-only peer" />
              <div class="p-4 border-2 rounded-lg text-center transition-colors peer-checked:border-primary-500 peer-checked:bg-primary-50 peer-checked:ring-2 peer-checked:ring-primary-500 hover:border-primary-300">
                <MoonIcon class="w-8 h-8 mx-auto mb-2 text-secondary-400" />
                <p class="font-medium text-secondary-900">Dark</p>
              </div>
            </label>
          </div>
        </div>
        
        <div>
          <label for="compact_mode" class="label">Sidebar Mode</label>
          <div class="mt-1">
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                id="compact_mode"
                type="checkbox"
                v-model="preferences.compact_mode"
                class="w-4 h-4 rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
              >
              <span class="text-sm text-secondary-700">Compact sidebar (icons only)</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Regional -->
    <div class="card p-6">
      <h2 class="text-lg font-semibold text-secondary-900 mb-6 flex items-center gap-2">
        <GlobeAltIcon class="w-5 h-5" />
        Regional Settings
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label for="language" class="label">Language</label>
          <select id="language" v-model="preferences.language" class="input mt-1">
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="ja">Japanese</option>
            <option value="zh">Chinese</option>
          </select>
        </div>
        
        <div>
          <label for="timezone" class="label">Timezone</label>
          <select id="timezone" v-model="preferences.timezone" class="input mt-1">
            <option v-for="tz in timezones" :key="tz" :value="tz">{{ tz }}</option>
          </select>
        </div>
        
        <div>
          <label for="date_format" class="label">Date Format</label>
          <select id="date_format" v-model="preferences.date_format" class="input mt-1">
            <option v-for="fmt in dateFormats" :key="fmt.value" :value="fmt.value">{{ fmt.label }}</option>
          </select>
        </div>
        
        <div>
          <label for="time_format" class="label">Time Format</label>
          <select id="time_format" v-model="preferences.time_format" class="input mt-1">
            <option v-for="fmt in timeFormats" :key="fmt.value" :value="fmt.value">{{ fmt.label }}</option>
          </select>
        </div>
        
        <div>
          <label for="items_per_page" class="label">Items Per Page</label>
          <select id="items_per_page" v-model="preferences.items_per_page" class="input mt-1">
            <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <div class="card p-6">
      <h2 class="text-lg font-semibold text-secondary-900 mb-6 flex items-center gap-2">
        <BellIcon class="w-5 h-5" />
        Notifications
      </h2>
      
      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <NotificationToggle v-model="preferences.email_notifications" title="Email Notifications" description="Receive notifications via email" />
          <NotificationToggle v-model="preferences.desktop_notifications" title="Desktop Notifications" description="Show browser notifications" />
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <NotificationToggle v-model="preferences.sound_notifications" title="Sound Notifications" description="Play sound for alerts" />
          <NotificationToggle v-model="preferences.auto_save" title="Auto Save" description="Automatically save drafts" />
        </div>
      </div>
      
      <h3 class="text-sm font-medium text-secondary-700 mt-6 mb-3">Email Preferences</h3>
      <div class="space-y-3">
        <NotificationToggle v-model="preferences.weekly_summary" title="Weekly Summary" description="Receive weekly activity summary" />
        <NotificationToggle v-model="preferences.project_updates" title="Project Updates" description="Get notified about project changes" />
        <NotificationToggle v-model="preferences.invoice_reminders" title="Invoice Reminders" description="Reminders for due/overdue invoices" />
        <NotificationToggle v-model="preferences.task_assignments" title="Task Assignments" description="When assigned to new tasks" />
      </div>
    </div>

    <!-- Actions -->
    <div class="card p-6">
      <h2 class="text-lg font-semibold text-secondary-900 mb-6 flex items-center gap-2">
        <ArrowPathIcon class="w-5 h-5" />
        Reset
      </h2>
      <p class="text-secondary-600 mb-4">Reset all preferences to their default values.</p>
      <button @click="resetToDefaults" class="btn-secondary">
        Reset to Defaults
      </button>
    </div>
  </div>
</template>

<script>
import { h } from 'vue'
import { SunIcon, MoonIcon, GlobeAltIcon, BellIcon, ArrowPathIcon, PaintBrushIcon } from '@heroicons/vue/24/outline'

const NotificationToggle = {
  props: ['modelValue', 'title', 'description'],
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('label', { class: 'flex items-center gap-3 cursor-pointer' }, [
      h('input', {
        type: 'checkbox',
        checked: props.modelValue,
        onChange: (e) => emit('update:modelValue', e.target.checked),
        class: 'w-4 h-4 rounded border-secondary-300 text-primary-600 focus:ring-primary-500',
      }),
      h('div', [
        h('p', { class: 'font-medium text-secondary-900' }, props.title),
        h('p', { class: 'text-sm text-secondary-500' }, props.description),
      ]),
    ])
  },
}
</script>

<style scoped>
/* Preferences styles */
</style>