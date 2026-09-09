<script setup>
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { pinia } from '@/stores/pinia'
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { RouterLink } from 'vue-router'
import {
  HomeIcon,
  BriefcaseIcon,
  ClockIcon,
  UsersIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  SunIcon,
  MoonIcon,
  BellIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline'
import {
  HomeIcon as HomeIconSolid,
  BriefcaseIcon as BriefcaseIconSolid,
  ClockIcon as ClockIconSolid,
  UsersIcon as UsersIconSolid,
  DocumentTextIcon as DocumentTextIconSolid,
  CurrencyDollarIcon as CurrencyDollarIconSolid,
  ChartBarIcon as ChartBarIconSolid,
  Cog6ToothIcon as Cog6ToothIconSolid,
} from '@heroicons/vue/24/solid'
import { TransitionRoot } from '@headlessui/vue'

const authStore = useAuthStore(pinia)
const uiStore = useUIStore(pinia)
const {
  sidebarOpen,
  sidebarCollapsed,
  theme,
  rightSidebarOpen,
  pageTitle,
  breadcrumbs,
} = storeToRefs(uiStore)
const { user, userName, userAvatar } = storeToRefs(authStore)
const {
  toggleSidebar,
  closeSidebar,
  toggleSidebarCollapsed,
  toggleTheme,
  closeRightSidebar,
} = uiStore
const logout = authStore.logout

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, iconSolid: HomeIconSolid, permission: null },
  { name: 'Projects', href: '/projects', icon: BriefcaseIcon, iconSolid: BriefcaseIconSolid, permission: 'projects.view' },
  { name: 'Time Tracking', href: '/time-entries', icon: ClockIcon, iconSolid: ClockIconSolid, permission: 'time_entries.view' },
  { name: 'Clients', href: '/clients', icon: UsersIcon, iconSolid: UsersIconSolid, permission: 'clients.view' },
  { name: 'Invoices', href: '/invoices', icon: DocumentTextIcon, iconSolid: DocumentTextIconSolid, permission: 'invoices.view' },
  { name: 'Expenses', href: '/expenses', icon: CurrencyDollarIcon, iconSolid: CurrencyDollarIconSolid, permission: 'expenses.view' },
  { name: 'Reports', href: '/reports', icon: ChartBarIcon, iconSolid: ChartBarIconSolid, permission: 'reports.view' },
  { name: 'Settings', href: '/settings/profile', icon: Cog6ToothIcon, iconSolid: Cog6ToothIconSolid, permission: null },
]

const filteredNavigation = computed(() => 
  navigation.filter(item => !item.permission || authStore.hasPermission(item.permission))
)

const userMenuItems = [
  { name: 'Profile', href: '/settings/profile', icon: UserCircleIcon },
  { name: 'Preferences', href: '/settings/preferences', icon: Cog6ToothIcon },
  { name: 'Logout', action: 'logout', icon: ArrowRightOnRectangleIcon, class: 'text-danger-600' },
]
</script>

<template>
  <div class="min-h-screen bg-secondary-50">
    <!-- Mobile sidebar overlay -->
    <TransitionRoot
      :show="sidebarOpen"
      appear
      enter="transition-opacity ease-linear duration-300"
      enter-from="opacity-0"
      enter-to="opacity-100"
      leave="transition-opacity ease-linear duration-300"
      leave-from="opacity-100"
      leave-to="opacity-0"
    >
      <div 
        v-if="sidebarOpen" 
        class="fixed inset-0 z-40 bg-black/50 lg:hidden" 
        @click="closeSidebar"
        aria-hidden="true"
      ></div>
    </TransitionRoot>

    <!-- Sidebar -->
    <TransitionRoot
      :show="sidebarOpen"
      appear
      enter="transition-transform ease-in-out duration-300"
      enter-from="-translate-x-full"
      enter-to="translate-x-0"
      leave="transition-transform ease-in-out duration-300"
      leave-from="translate-x-0"
      leave-to="-translate-x-full"
    >
      <aside 
        :class="[
          'fixed inset-y-0 left-0 z-50 bg-white border-r border-secondary-200 transition-all duration-300',
          sidebarCollapsed ? 'w-16' : 'w-64',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        ]"
        aria-label="Sidebar"
      >
        <div class="flex h-16 items-center px-4 border-b border-secondary-200">
          <RouterLink to="/dashboard" class="flex items-center gap-2" aria-label="ERP System Home">
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">ERP</span>
            </div>
            <span v-if="!sidebarCollapsed" class="font-semibold text-secondary-900">ERP System</span>
          </RouterLink>
          
          <button
            v-if="!sidebarCollapsed"
            @click="toggleSidebarCollapsed"
            class="ml-auto lg:hidden p-2 rounded-lg text-secondary-500 hover:bg-secondary-100"
            aria-label="Collapse sidebar"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Main navigation">
          <template v-for="item in filteredNavigation" :key="item.name">
            <RouterLink
              :to="item.href"
              :class="[
                'sidebar-link',
                $route.path.startsWith(item.href) && item.href !== '/dashboard' ? 'sidebar-link-active' : '',
                $route.path === item.href ? 'sidebar-link-active' : '',
                sidebarCollapsed ? 'justify-center px-2' : ''
              ]"
              :title="sidebarCollapsed ? item.name : ''"
            >
              <component :is="$route.path === item.href || $route.path.startsWith(item.href + '/') ? item.iconSolid : item.icon" class="w-5 h-5 flex-shrink-0" />
              <span v-if="!sidebarCollapsed" class="truncate">{{ item.name }}</span>
            </RouterLink>
          </template>
        </nav>

        <div v-if="!sidebarCollapsed" class="p-3 border-t border-secondary-200">
          <button
            @click="toggleTheme"
            class="flex items-center gap-3 w-full px-3 py-2 text-sm font-medium text-secondary-600 rounded-lg hover:bg-secondary-100 transition-colors"
          >
            <component :is="theme === 'dark' ? SunIcon : MoonIcon" class="w-5 h-5" />
            <span>{{ theme === 'dark' ? 'Light Mode' : 'Dark Mode' }}</span>
          </button>
        </div>
      </aside>
    </TransitionRoot>

    <!-- Main content -->
    <div :class="['lg:pl-64 transition-all duration-300', sidebarCollapsed ? 'lg:pl-16' : '']">
      <!-- Top header -->
      <header class="sticky top-0 z-30 bg-white/80 backdrop-blur-sm border-b border-secondary-200">
        <div class="flex h-16 items-center justify-between px-4 sm:px-6">
          <div class="flex items-center gap-4">
            <button
              @click="toggleSidebar"
              class="lg:hidden p-2 rounded-lg text-secondary-500 hover:bg-secondary-100"
              aria-label="Open sidebar"
            >
              <Bars3Icon class="w-6 h-6" />
            </button>
            
            <h1 v-if="pageTitle" class="text-lg font-semibold text-secondary-900 truncate">{{ pageTitle }}</h1>
            
            <nav v-if="breadcrumbs.length" class="hidden md:flex items-center gap-2 text-sm text-secondary-500" aria-label="Breadcrumb">
              <RouterLink to="/dashboard" class="hover:text-secondary-700">Dashboard</RouterLink>
              <span class="mx-2">/</span>
              <template v-for="(crumb, index) in breadcrumbs" :key="index">
                <RouterLink v-if="crumb.href" :to="crumb.href" class="hover:text-secondary-700">{{ crumb.name }}</RouterLink>
                <span v-else class="text-secondary-900 font-medium">{{ crumb.name }}</span>
                <span v-if="index < breadcrumbs.length - 1" class="mx-2">/</span>
              </template>
            </nav>
          </div>

          <div class="flex items-center gap-2">
            <!-- Notifications -->
            <div class="relative">
              <button class="p-2 rounded-lg text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700 relative" aria-label="Notifications">
                <BellIcon class="w-5 h-5" />
                <span class="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full"></span>
              </button>
            </div>

            <!-- Theme toggle (collapsed sidebar) -->
            <button
              v-if="sidebarCollapsed"
              @click="toggleTheme"
              class="p-2 rounded-lg text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700"
              :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
            >
              <component :is="theme === 'dark' ? SunIcon : MoonIcon" class="w-5 h-5" />
            </button>

            <!-- User menu -->
            <div class="relative">
              <button
                @click="uiStore.toggleRightSidebar"
                class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-secondary-100"
                aria-label="User menu"
              >
                <img 
                  :src="userAvatar" 
                  :alt="userName" 
                  class="w-8 h-8 rounded-full bg-secondary-100"
                >
                <span v-if="!sidebarCollapsed" class="text-sm font-medium text-secondary-700 hidden sm:block">{{ userName }}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Main content area -->
      <main class="p-4 sm:p-6 lg:p-8" id="main-content">
        <slot />
      </main>
    </div>

    <!-- Right Sidebar (User Menu) -->
    <TransitionRoot
      :show="rightSidebarOpen"
      appear
      enter="transition-transform ease-in-out duration-200"
      enter-from="translate-x-full"
      enter-to="translate-x-0"
      leave="transition-transform ease-in-out duration-200"
      leave-from="translate-x-0"
      leave-to="translate-x-full"
    >
      <div v-if="rightSidebarOpen" class="fixed inset-y-0 right-0 z-50 w-72 bg-white border-l border-secondary-200 lg:hidden">
        <div class="p-4 border-b border-secondary-200">
          <div class="flex items-center gap-3">
            <img :src="userAvatar" :alt="userName" class="w-10 h-10 rounded-full bg-secondary-100">
            <div>
              <p class="font-medium text-secondary-900">{{ userName }}</p>
              <p class="text-sm text-secondary-500">{{ user.value?.email }}</p>
            </div>
          </div>
        </div>
        <nav class="p-3 space-y-1">
          <template v-for="item in userMenuItems" :key="item.name">
            <RouterLink
              v-if="item.href"
              :to="item.href"
              @click="closeRightSidebar"
              class="dropdown-item flex items-center gap-3"
              :class="item.class"
            >
              <component :is="item.icon" class="w-5 h-5" />
              {{ item.name }}
            </RouterLink>
            <button
              v-else
              @click="logout"
              class="dropdown-item flex items-center gap-3 w-full"
              :class="item.class"
            >
              <component :is="item.icon" class="w-5 h-5" />
              {{ item.name }}
            </button>
          </template>
        </nav>
      </div>
    </TransitionRoot>

    <!-- Right Sidebar Overlay -->
    <TransitionRoot
      :show="rightSidebarOpen"
      appear
      enter="transition-opacity ease-linear duration-200"
      enter-from="opacity-0"
      enter-to="opacity-100"
      leave="transition-opacity ease-linear duration-200"
      leave-from="opacity-100"
      leave-to="opacity-0"
    >
      <div v-if="rightSidebarOpen" class="fixed inset-0 z-40 bg-black/50 lg:hidden" @click="closeRightSidebar" aria-hidden="true"></div>
    </TransitionRoot>
  </div>
</template>

<style scoped>
/* Custom scrollbar for sidebar */
aside::-webkit-scrollbar {
  width: 4px;
}
aside::-webkit-scrollbar-track {
  background: transparent;
}
aside::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 2px;
}
</style>