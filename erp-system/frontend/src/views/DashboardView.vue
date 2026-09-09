<script setup>
import { onMounted, ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { pinia } from '@/stores/pinia'
import api from '@/services/api'
import { dashboardApi } from '@/services/api-modules'
import { format } from 'date-fns'
import {
  BriefcaseIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  UsersIcon,
  ArrowTrendingUpIcon,
  DocumentTextIcon,
} from '@heroicons/vue/24/outline'
import { RouterLink } from 'vue-router'

const authStore = useAuthStore(pinia)
const uiStore = useUIStore(pinia)

const stats = ref(null)
const loading = ref(true)
const recentProjects = ref([])
const recentTimeEntries = ref([])
const pendingApprovals = ref([])

const statCards = computed(() => {
  if (!stats.value) return []
  
  return [
    {
      title: 'My Projects',
      value: stats.value.my_projects || 0,
      icon: BriefcaseIcon,
      color: 'primary',
      href: '/projects',
    },
    {
      title: 'Active Projects',
      value: stats.value.active_projects || 0,
      icon: ChartBarIcon,
      color: 'success',
      href: '/projects?status=active',
    },
    {
      title: 'This Week Hours',
      value: (stats.value.this_week_hours || 0).toFixed(1),
      icon: ClockIcon,
      color: 'warning',
      href: '/time-entries/weekly',
      suffix: 'h',
    },
    {
      title: 'Pending Entries',
      value: stats.value.pending_time_entries || 0,
      icon: ExclamationTriangleIcon,
      color: 'danger',
      href: '/time-entries?status=pending',
    },
  ]
})

const adminStatCards = computed(() => {
  if (!stats.value || !authStore.hasPermission('projects.view_all')) return []
  
  return [
    {
      title: 'Total Projects',
      value: stats.value.total_projects || 0,
      icon: BriefcaseIcon,
      color: 'primary',
      href: '/projects',
    },
    {
      title: 'Pending Approvals',
      value: stats.value.pending_approvals || 0,
      icon: DocumentTextIcon,
      color: 'warning',
      href: '/time-entries/pending/approvals',
    },
    {
      title: 'Overdue Invoices',
      value: stats.value.overdue_invoices || 0,
      icon: ExclamationTriangleIcon,
      color: 'danger',
      href: '/invoices?status=overdue',
    },
    {
      title: 'Outstanding Amount',
      value: `$${(stats.value.outstanding_amount || 0).toLocaleString()}`,
      icon: CurrencyDollarIcon,
      color: 'success',
      href: '/invoices?status=outstanding',
    },
  ]
})

async function fetchData() {
  try {
    uiStore.setLoading(true)
    const [statsRes, projectsRes, timeEntriesRes, approvalsRes] = await Promise.allSettled([
      dashboardApi.stats(),
      api.get('/projects', { params: { per_page: 5, sort: '-created_at' } }),
      api.get('/time-entries/my/entries', { params: { per_page: 5, sort: '-date' } }),
      api.get('/time-entries/pending/approvals', { params: { per_page: 5 } }),
    ])
    
    if (statsRes.status === 'fulfilled') stats.value = statsRes.value.data
    if (projectsRes.status === 'fulfilled') recentProjects.value = projectsRes.value.data.data
    if (timeEntriesRes.status === 'fulfilled') recentTimeEntries.value = timeEntriesRes.value.data.data
    if (approvalsRes.status === 'fulfilled') pendingApprovals.value = approvalsRes.value.data.data
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    uiStore.setLoading(false)
    loading.value = false
  }
}

onMounted(() => {
  uiStore.setPageTitle('Dashboard')
  uiStore.setBreadcrumbs([{ name: 'Dashboard' }])
  fetchData()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">
          Welcome back, {{ authStore.user?.first_name }}!
        </h1>
        <p class="text-secondary-600 mt-1">Here's what's happening with your projects today.</p>
      </div>
      <div class="flex gap-3">
        <RouterLink to="/time-entries/create" class="btn-primary">
          <ClockIcon class="w-5 h-5 mr-2" />
          Log Time
        </RouterLink>
        <RouterLink to="/projects/create" class="btn-secondary">
          <PlusIcon class="w-5 h-5 mr-2" />
          New Project
        </RouterLink>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        v-for="card in statCards"
        :key="card.title"
        :title="card.title"
        :value="card.value"
        :icon="card.icon"
        :color="card.color"
        :href="card.href"
        :suffix="card.suffix"
      />
    </div>

    <!-- Admin Stats -->
    <div v-if="authStore.hasPermission('projects.view_all')" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        v-for="card in adminStatCards"
        :key="card.title"
        :title="card.title"
        :value="card.value"
        :icon="card.icon"
        :color="card.color"
        :href="card.href"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent Projects -->
      <div class="lg:col-span-2">
        <div class="card">
          <div class="px-6 py-4 border-b border-secondary-200 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-secondary-900">Recent Projects</h2>
            <RouterLink to="/projects" class="text-sm text-primary-600 hover:text-primary-700">View all</RouterLink>
          </div>
          <div class="divide-y divide-secondary-100">
            <div v-if="loading || !recentProjects.length" class="p-6 text-center text-secondary-500">
              <BriefcaseIcon class="w-12 h-12 mx-auto mb-3 text-secondary-300" />
              <p>No projects yet</p>
              <RouterLink to="/projects/create" class="text-primary-600 hover:text-primary-700 mt-2 inline-block">
                Create your first project
              </RouterLink>
            </div>
            <template v-else>
              <div v-for="project in recentProjects" :key="project.id" class="px-6 py-4 hover:bg-secondary-50 transition-colors">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3 min-w-0">
                    <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <BriefcaseIcon class="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <RouterLink :to="`/projects/${project.id}`" class="font-medium text-secondary-900 hover:text-primary-600 truncate block">
                        {{ project.name }}
                      </RouterLink>
                      <p class="text-sm text-secondary-500">{{ project.code }} • {{ project.client?.name || 'Internal' }}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-4">
                    <Badge :color="project.status_color">{{ project.status }}</Badge>
                    <div class="text-right">
                      <p class="text-sm font-medium text-secondary-900">{{ project.progress }}%</p>
                      <p class="text-xs text-secondary-500">Complete</p>
                    </div>
                  </div>
                </div>
                <div class="mt-2 h-1.5 bg-secondary-100 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-primary-600 rounded-full transition-all duration-300" 
                    :style="{ width: project.progress + '%' }"
                  ></div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Sidebar Widgets -->
      <div class="space-y-6">
        <!-- Quick Actions -->
        <div class="card">
          <div class="px-6 py-4 border-b border-secondary-200">
            <h2 class="text-lg font-semibold text-secondary-900">Quick Actions</h2>
          </div>
          <div class="p-4 space-y-3">
            <RouterLink to="/time-entries/create" class="btn-secondary w-full justify-start gap-3">
              <ClockIcon class="w-5 h-5" />
              <span>Log Time Entry</span>
            </RouterLink>
            <RouterLink to="/projects/create" class="btn-secondary w-full justify-start gap-3">
              <BriefcaseIcon class="w-5 h-5" />
              <span>Create Project</span>
            </RouterLink>
            <RouterLink to="/clients/create" class="btn-secondary w-full justify-start gap-3">
              <UsersIcon class="w-5 h-5" />
              <span>Add Client</span>
            </RouterLink>
            <RouterLink to="/invoices/create" class="btn-secondary w-full justify-start gap-3">
              <DocumentTextIcon class="w-5 h-5" />
              <span>Create Invoice</span>
            </RouterLink>
          </div>
        </div>

        <!-- This Week Summary -->
        <div class="card">
          <div class="px-6 py-4 border-b border-secondary-200">
            <h2 class="text-lg font-semibold text-secondary-900">This Week</h2>
          </div>
          <div class="p-6">
            <div class="text-center mb-6">
              <p class="text-4xl font-bold text-secondary-900">{{ stats?.this_week_hours || 0 }}h</p>
              <p class="text-secondary-500">Logged this week</p>
            </div>
            <div class="space-y-3">
              <div v-for="day in weekDays" :key="day" class="flex items-center justify-between">
                <span class="text-sm text-secondary-600">{{ day.name }}</span>
                <span class="text-sm font-medium text-secondary-900">{{ day.hours }}h</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Pending Approvals (for managers) -->
        <div v-if="authStore.hasPermission('time_entries.approve')" class="card">
          <div class="px-6 py-4 border-b border-secondary-200 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-secondary-900">Pending Approvals</h2>
            <RouterLink to="/time-entries/pending/approvals" class="text-sm text-primary-600 hover:text-primary-700">View all</RouterLink>
          </div>
          <div class="divide-y divide-secondary-100">
            <div v-if="pendingApprovals.length === 0" class="p-6 text-center text-secondary-500">
              <CheckCircleIcon class="w-12 h-12 mx-auto mb-3 text-success-500" />
              <p>All caught up!</p>
            </div>
            <template v-else>
              <div v-for="entry in pendingApprovals.slice(0, 5)" :key="entry.id" class="px-6 py-4">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3 min-w-0">
                    <div class="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <ClockIcon class="w-4 h-4 text-warning-600" />
                    </div>
                    <div>
                      <p class="font-medium text-secondary-900 truncate">{{ entry.user?.full_name }}</p>
                      <p class="text-sm text-secondary-500">{{ entry.project?.name }} • {{ entry.formatted_duration }}</p>
                    </div>
                  </div>
                  <Badge color="warning">Pending</Badge>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { h } from 'vue'

const StatCard = {
  props: ['title', 'value', 'icon', 'color', 'href', 'suffix'],
  setup(props) {
    const colors = {
      primary: 'bg-primary-50 text-primary-600 border-primary-100',
      success: 'bg-success-50 text-success-600 border-success-100',
      warning: 'bg-warning-50 text-warning-600 border-warning-100',
      danger: 'bg-danger-50 text-danger-600 border-danger-100',
    }
    return () => h('div', { class: `card p-6 border ${colors[props.color]}` }, [
      h('div', { class: 'flex items-center justify-between' }, [
        h('div', { class: 'flex-1 min-w-0' }, [
          h('p', { class: 'text-sm font-medium text-secondary-600 truncate' }, props.title),
          h('div', { class: 'mt-1 flex items-baseline gap-1' }, [
            h('p', { class: 'text-2xl font-bold text-secondary-900' }, props.value),
            props.suffix && h('span', { class: 'text-secondary-500' }, props.suffix),
          ]),
        ]),
        h('div', { class: `w-12 h-12 rounded-xl flex items-center justify-center ${colors[props.color]}` }, [
          h(props.icon, { class: 'w-6 h-6' }),
        ]),
      ]),
      props.href && h('a', { 
        href: props.href, 
        class: 'mt-4 block text-sm font-medium hover:underline',
        style: { color: `var(--tw-text-opacity, 1)${getComputedStyle(document.documentElement).getPropertyValue('--tw-text-opacity')}` }
      }, 'View details →'),
    ])
  },
}

const Badge = {
  props: ['color', 'children'],
  setup(props, { slots }) {
    const colors = {
      primary: 'bg-primary-100 text-primary-800',
      success: 'bg-success-100 text-success-600',
      warning: 'bg-warning-100 text-warning-600',
      danger: 'bg-danger-100 text-danger-600',
      gray: 'bg-secondary-100 text-secondary-600',
    }
    return () => h('span', { class: `badge ${colors[props.color] || colors.gray}` }, slots.default())
  },
}

const CheckCircleIcon = {
  setup() {
    return () => h('svg', { class: 'w-12 h-12', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' }),
    ])
  },
}

const PlusIcon = {
  setup() {
    return () => h('svg', { class: 'w-5 h-5', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 4v16m8-8H4' }),
    ])
  },
}

const weekDays = [
  { name: 'Mon', hours: '2.5' },
  { name: 'Tue', hours: '7.0' },
  { name: 'Wed', hours: '6.5' },
  { name: 'Thu', hours: '8.0' },
  { name: 'Fri', hours: '4.0' },
  { name: 'Sat', hours: '0' },
  { name: 'Sun', hours: '0' },
]
</script>

<style scoped>
/* Dashboard styles */
</style>