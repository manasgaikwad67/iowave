<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { RouterLink, RouterView } from 'vue-router'
import { useToast } from 'vue-toastification'
import {
  UserCircleIcon,
  Cog6ToothIcon,
  UsersIcon,
  BuildingOfficeIcon,
  ShieldCheckIcon,
  BellIcon,
  PaintBrushIcon,
} from '@heroicons/vue/24/outline'
import {
  UserCircleIcon as UserCircleIconSolid,
  Cog6ToothIcon as Cog6ToothIconSolid,
  UsersIcon as UsersIconSolid,
  BuildingOfficeIcon as BuildingOfficeIconSolid,
  ShieldCheckIcon as ShieldCheckIconSolid,
  BellIcon as BellIconSolid,
  PaintBrushIcon as PaintBrushIconSolid,
} from '@heroicons/vue/24/solid'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUIStore()
const toast = useToast()

const settingsNav = [
  { name: 'Profile', href: '/settings/profile', icon: UserCircleIcon, iconSolid: UserCircleIconSolid, permission: null },
  { name: 'Preferences', href: '/settings/preferences', icon: PaintBrushIcon, iconSolid: PaintBrushIconSolid, permission: null },
  { name: 'Notifications', href: '/settings/notifications', icon: BellIcon, iconSolid: BellIconSolid, permission: null },
  { name: 'Users', href: '/settings/users', icon: UsersIcon, iconSolid: UsersIconSolid, permission: 'users.view' },
  { name: 'Departments', href: '/settings/departments', icon: BuildingOfficeIcon, iconSolid: BuildingOfficeIconSolid, permission: 'departments.view' },
  { name: 'Roles & Permissions', href: '/settings/roles', icon: ShieldCheckIcon, iconSolid: ShieldCheckIconSolid, permission: 'users.manage_roles' },
]

const filteredNav = computed(() => 
  settingsNav.filter(item => !item.permission || authStore.hasPermission(item.permission))
)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">Settings</h1>
        <p class="text-secondary-600 mt-1">Manage your account and system preferences</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Sidebar Navigation -->
      <div class="lg:col-span-1">
        <nav class="card p-4 space-y-1" aria-label="Settings navigation">
          <template v-for="item in filteredNav" :key="item.name">
            <RouterLink
              :to="item.href"
              :class="[
                'sidebar-link',
                route.path === item.href || route.path.startsWith(item.href + '/') ? 'sidebar-link-active' : '',
              ]"
            >
              <component :is="route.path === item.href || route.path.startsWith(item.href + '/') ? item.iconSolid : item.icon" class="w-5 h-5 flex-shrink-0" />
              {{ item.name }}
            </RouterLink>
          </template>
        </nav>
      </div>

      <!-- Content Area -->
      <div class="lg:col-span-3">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<script>
import { h } from 'vue'
</script>

<style scoped>
/* Settings view styles */
</style>