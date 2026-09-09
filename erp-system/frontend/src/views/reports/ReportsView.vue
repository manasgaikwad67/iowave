<script setup>
import { ref, onMounted } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { reportsApi } from '@/services/api-modules'
import { useToast } from 'vue-toastification'
import { RouterLink } from 'vue-router'
import {
  ChartBarIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ClockIcon,
  DocumentChartBarIcon,
} from '@heroicons/vue/24/outline'

const uiStore = useUIStore()
const authStore = useAuthStore()
const toast = useToast()

const reports = ref([
  {
    name: 'Utilization Report',
    description: 'Track team utilization and billable hours',
    icon: UserGroupIcon,
    color: 'primary',
    href: '/reports/utilization',
    permission: 'reports.utilization',
  },
  {
    name: 'Project Profitability',
    description: 'Analyze project margins and profitability',
    icon: CurrencyDollarIcon,
    color: 'success',
    href: '/reports/profitability',
    permission: 'reports.project_profitability',
  },
  {
    name: 'Time Entries Report',
    description: 'Detailed time tracking analytics',
    icon: ClockIcon,
    color: 'warning',
    href: '/reports/time-entries',
    permission: 'reports.time_entries',
  },
  {
    name: 'Financial Report',
    description: 'Revenue, invoicing, and payment analytics',
    icon: DocumentChartBarIcon,
    color: 'blue',
    href: '/reports/financial',
    permission: 'reports.financial',
  },
])

const availableReports = computed(() => 
  reports.value.filter(r => !r.permission || authStore.hasPermission(r.permission))
)

onMounted(() => {
  uiStore.setPageTitle('Reports & Analytics')
  uiStore.setBreadcrumbs([{ name: 'Reports' }])
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-secondary-900">Reports & Analytics</h1>
      <p class="text-secondary-600 mt-1">Gain insights into your business performance</p>
    </div>

    <!-- Reports Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <RouterLink
        v-for="report in availableReports"
        :key="report.name"
        :to="report.href"
        class="card-hover p-6 flex flex-col h-full"
      >
        <div :class="`w-12 h-12 rounded-xl flex items-center justify-center bg-${report.color}-100 text-${report.color}-600 mb-4`">
          <component :is="report.icon" class="w-6 h-6" />
        </div>
        <h3 class="font-semibold text-secondary-900 mb-1">{{ report.name }}</h3>
        <p class="text-sm text-secondary-500 flex-1">{{ report.description }}</p>
        <span class="mt-4 text-sm text-primary-600 font-medium flex items-center gap-1">
          View Report
          <ChevronRightIcon class="w-4 h-4" />
        </span>
      </RouterLink>
    </div>

    <!-- Quick Stats -->
    <div class="card">
      <div class="px-6 py-4 border-b border-secondary-200">
        <h2 class="text-lg font-semibold text-secondary-900">Quick Overview</h2>
      </div>
      <div class="p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Revenue" value="$245,000" change="+12.5%" changePositive />
        <StatCard title="Outstanding" value="$45,000" change="-3.2%" changePositive />
        <StatCard title="Utilization" value="78%" change="+2.1%" changePositive />
        <StatCard title="Avg. Project Margin" value="34%" change="-1.5%" :changePositive="false" />
      </div>
    </div>
  </div>
</template>

<script>
import { computed, h } from 'vue'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'

const StatCard = {
  props: ['title', 'value', 'change', 'changePositive'],
  setup(props) {
    return () => h('div', { class: 'text-center' }, [
      h('p', { class: 'text-sm text-secondary-500 mb-1' }, props.title),
      h('p', { class: 'text-2xl font-bold text-secondary-900' }, props.value),
      h('p', { 
        class: `text-sm font-medium ${props.changePositive ? 'text-success-600' : 'text-danger-600'}` 
      }, props.change),
    ])
  },
}
</script>

<style scoped>
/* Reports view styles */
</style>