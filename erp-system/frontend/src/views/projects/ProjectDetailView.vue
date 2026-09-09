<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { projectsApi } from '@/services/api-modules'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { RouterLink } from 'vue-router'
import {
  BriefcaseIcon,
  UsersIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/vue/24/outline'
import { format } from 'date-fns'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const project = ref(null)
const loading = ref(true)
const activeTab = ref('overview')
const tasks = ref([])
const timeEntries = ref([])
const members = ref([])

const tabs = [
  { id: 'overview', name: 'Overview', icon: BriefcaseIcon },
  { id: 'tasks', name: 'Tasks', icon: ChartBarIcon },
  { id: 'team', name: 'Team', icon: UsersIcon },
  { id: 'time', name: 'Time Entries', icon: ClockIcon },
  { id: 'financials', name: 'Financials', icon: CurrencyDollarIcon },
]

async function fetchProject() {
  loading.value = true
  try {
    const response = await projectsApi.get(route.params.id)
    project.value = response.data.data
    
    // Fetch related data
    const [tasksRes, timeRes, membersRes] = await Promise.allSettled([
      api.get(`/projects/${route.params.id}/tasks`, { params: { per_page: 100 } }),
      api.get(`/time-entries`, { params: { project_id: route.params.id, per_page: 50 } }),
      projectsApi.members(route.params.id),
    ])
    
    if (tasksRes.status === 'fulfilled') tasks.value = tasksRes.value.data.data
    if (timeRes.status === 'fulfilled') timeEntries.value = timeRes.value.data.data
    if (membersRes.status === 'fulfilled') members.value = membersRes.value.data
  } catch (error) {
    toast.error('Failed to load project')
    router.push('/projects')
  } finally {
    loading.value = false
  }
}

async function deleteProject() {
  if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) return
  
  try {
    await projectsApi.delete(route.params.id)
    toast.success('Project deleted successfully')
    router.push('/projects')
  } catch (error) {
    toast.error('Failed to delete project')
  }
}

function formatDate(date) {
  return date ? format(new Date(date), 'MMM d, yyyy') : '—'
}

function formatCurrency(amount) {
  if (!amount) return '$0'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(amount)
}

function getStatusColor(status) {
  const colors = {
    planning: 'gray',
    active: 'blue',
    on_hold: 'yellow',
    completed: 'green',
    cancelled: 'red',
  }
  return colors[status] || 'gray'
}

onMounted(() => {
  fetchProject()
})
</script>

<template>
  <div v-if="!loading" class="space-y-6">
    <!-- Project Header -->
    <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
      <div class="flex items-center gap-4">
        <RouterLink to="/projects" class="btn-ghost p-2">
          <ChevronLeftIcon class="w-5 h-5" />
        </RouterLink>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold text-secondary-900">{{ project.name }}</h1>
            <span :class="`badge badge-${getStatusColor(project.status)}`" class="capitalize">
              {{ project.status.replace('_', ' ') }}
            </span>
          </div>
          <p class="text-secondary-500 mt-1">{{ project.code }} • {{ project.client?.name || 'Internal Project' }}</p>
        </div>
      </div>
      
      <div class="flex gap-2">
        <RouterLink :to="`/projects/${project.id}/edit`" class="btn-secondary">
          <PencilIcon class="w-5 h-5 mr-2" />
          Edit
        </RouterLink>
        <button @click="deleteProject" class="btn-danger">
          <TrashIcon class="w-5 h-5 mr-2" />
          Delete
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard title="Progress" :value="project.progress + '%'" icon="ChartBarIcon" color="primary" />
      <StatCard title="Budget Used" :value="project.budget_utilization + '%'" icon="CurrencyDollarIcon" color="success" />
      <StatCard title="Hours Logged" :value="project.actual_hours + 'h'" icon="ClockIcon" color="warning" />
      <StatCard title="Team Members" :value="members.length" icon="UsersIcon" color="blue" />
    </div>

    <!-- Tabs -->
    <div class="border-b border-secondary-200">
      <nav class="flex gap-8" aria-label="Project tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id ? 'border-primary-500 text-primary-600' : 'border-transparent text-secondary-500 hover:text-secondary-700'
          ]"
        >
          <component :is="tab.icon" class="w-4 h-4 mr-1 inline-block" />
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div class="card">
      <div class="p-6">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="font-medium text-secondary-900 mb-3">Project Details</h3>
              <dl class="space-y-3">
                <div class="flex justify-between">
                  <dt class="text-secondary-500">Description</dt>
                  <dd class="text-secondary-900">{{ project.description || '—' }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-secondary-500">Billing Type</dt>
                  <dd class="text-secondary-900 capitalize">{{ project.billing_type.replace('_', ' ') }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-secondary-500">Hourly Rate</dt>
                  <dd class="text-secondary-900">{{ formatCurrency(project.hourly_rate) }}/hr</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-secondary-500">Fixed Price</dt>
                  <dd class="text-secondary-900">{{ formatCurrency(project.fixed_price) }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-secondary-500">Start Date</dt>
                  <dd class="text-secondary-900">{{ formatDate(project.start_date) }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-secondary-500">End Date</dt>
                  <dd class="text-secondary-900">{{ formatDate(project.end_date) }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-secondary-500">Project Manager</dt>
                  <dd class="text-secondary-900">{{ project.project_manager?.full_name || '—' }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-secondary-500">Department</dt>
                  <dd class="text-secondary-900">{{ project.department?.name || '—' }}</dd>
                </div>
              </dl>
            </div>
            
            <div>
              <h3 class="font-medium text-secondary-900 mb-3">Budget Overview</h3>
              <div class="space-y-4">
                <BudgetBar label="Estimated Budget" :value="project.estimated_budget" :max="project.estimated_budget" color="primary" />
                <BudgetBar label="Actual Cost" :value="project.actual_cost" :max="project.estimated_budget" color="danger" />
                <BudgetBar label="Remaining" :value="Math.max(0, project.estimated_budget - project.actual_cost)" :max="project.estimated_budget" color="success" />
              </div>
              
              <div class="pt-4 border-t border-secondary-200">
                <h4 class="font-medium text-secondary-900 mb-3">Hours</h4>
                <BudgetBar label="Estimated Hours" :value="project.estimated_hours" :max="project.estimated_hours" color="primary" suffix="h" />
                <BudgetBar label="Actual Hours" :value="project.actual_hours" :max="project.estimated_hours" color="danger" suffix="h" />
              </div>
            </div>
          </div>
        </div>

        <!-- Tasks Tab -->
        <div v-if="activeTab === 'tasks'">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-medium text-secondary-900">Tasks</h3>
            <RouterLink :to="`/projects/${project.id}/tasks/create`" class="btn-primary btn-sm">
              <PlusIcon class="w-4 h-4 mr-1" />
              Add Task
            </RouterLink>
          </div>
          
          <div v-if="tasks.length === 0" class="text-center py-8 text-secondary-500">
            <p>No tasks yet</p>
            <RouterLink :to="`/projects/${project.id}/tasks/create`" class="text-primary-600 hover:text-primary-700 mt-2 inline-block">
              Create your first task
            </RouterLink>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Assignee</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Due Date</th>
                  <th>Progress</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="task in tasks" :key="task.id">
                  <td>
                    <RouterLink :to="`/tasks/${task.id}`" class="font-medium text-secondary-900 hover:text-primary-600">
                      {{ task.title }}
                    </RouterLink>
                  </td>
                  <td>
                    <span v-if="task.assignee">{{ task.assignee.full_name }}</span>
                    <span v-else class="text-secondary-400">Unassigned</span>
                  </td>
                  <td><Badge :color="getStatusColor(task.status)">{{ task.status.replace('_', ' ') }}</Badge></td>
                  <td><Badge :color="getPriorityColor(task.priority)">{{ task.priority }}</Badge></td>
                  <td>{{ formatDate(task.due_date) }}</td>
                  <td>{{ task.progress }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Team Tab -->
        <div v-if="activeTab === 'team'">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-medium text-secondary-900">Team Members</h3>
            <button class="btn-primary btn-sm">
              <PlusIcon class="w-4 h-4 mr-1" />
              Add Member
            </button>
          </div>
          
          <div v-if="members.length === 0" class="text-center py-8 text-secondary-500">
            <p>No team members yet</p>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Role</th>
                  <th>Hourly Rate</th>
                  <th>Allocated Hours</th>
                  <th>Period</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="member in members" :key="member.id">
                  <td>
                    <div class="flex items-center gap-3">
                      <img :src="member.user?.avatar" :alt="member.user?.full_name" class="w-8 h-8 rounded-full" />
                      <span>{{ member.user?.full_name }}</span>
                    </div>
                  </td>
                  <td><Badge :color="getRoleColor(member.pivot.role)">{{ member.pivot.role }}</Badge></td>
                  <td>{{ formatCurrency(member.pivot.hourly_rate) }}/hr</td>
                  <td>{{ member.pivot.allocated_hours || '—' }}h/week</td>
                  <td>{{ formatDate(member.pivot.start_date) }} - {{ formatDate(member.pivot.end_date) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Time Entries Tab -->
        <div v-if="activeTab === 'time'">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-medium text-secondary-900">Recent Time Entries</h3>
            <RouterLink :to="`/time-entries?project_id=${project.id}`" class="btn-secondary btn-sm">
              View All
            </RouterLink>
          </div>
          
          <div v-if="timeEntries.length === 0" class="text-center py-8 text-secondary-500">
            <p>No time entries yet</p>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>User</th>
                  <th>Task</th>
                  <th>Duration</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="entry in timeEntries.slice(0, 10)" :key="entry.id">
                  <td>{{ formatDate(entry.date) }}</td>
                  <td>{{ entry.user?.full_name }}</td>
                  <td>{{ entry.task?.title || '—' }}</td>
                  <td>{{ formatDuration(entry.duration_minutes) }}</td>
                  <td><Badge :color="getStatusColor(entry.status)">{{ entry.status }}</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Financials Tab -->
        <div v-if="activeTab === 'financials'">
          <h3 class="font-medium text-secondary-900 mb-4">Financial Overview</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard title="Estimated Budget" :value="formatCurrency(project.estimated_budget)" icon="CurrencyDollarIcon" color="primary" />
            <StatCard title="Actual Cost" :value="formatCurrency(project.actual_cost)" icon="CurrencyDollarIcon" color="danger" />
            <StatCard title="Variance" :value="formatCurrency(project.estimated_budget - project.actual_cost)" icon="CurrencyDollarIcon" :color="project.actual_cost <= project.estimated_budget ? 'success' : 'danger'" />
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="flex items-center justify-center h-64">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
  </div>
</template>

<script>
import { h, computed } from 'vue'
import api from '@/services/api'
import { format } from 'date-fns'

const StatCard = {
  props: ['title', 'value', 'icon', 'color'],
  setup(props) {
    const colors = {
      primary: 'bg-primary-50 text-primary-600 border-primary-100',
      success: 'bg-success-50 text-success-600 border-success-100',
      warning: 'bg-warning-50 text-warning-600 border-warning-100',
      danger: 'bg-danger-50 text-danger-600 border-danger-100',
      blue: 'bg-blue-50 text-blue-600 border-blue-100',
      gray: 'bg-secondary-50 text-secondary-600 border-secondary-100',
    }
    return () => h('div', { class: `card p-4 border ${colors[props.color]}` }, [
      h('div', { class: 'flex items-center justify-between' }, [
        h('div', { class: 'flex-1 min-w-0' }, [
          h('p', { class: 'text-sm font-medium text-secondary-600 truncate' }, props.title),
          h('p', { class: 'text-2xl font-bold text-secondary-900 mt-1' }, props.value),
        ]),
        h('div', { class: `w-10 h-10 rounded-lg flex items-center justify-center ${colors[props.color]}` }, [
          h(props.icon, { class: 'w-5 h-5' }),
        ]),
      ]),
    ])
  },
}

const BudgetBar = {
  props: ['label', 'value', 'max', 'color', 'suffix'],
  setup(props) {
    const colors = {
      primary: 'bg-primary-600',
      success: 'bg-success-600',
      warning: 'bg-warning-600',
      danger: 'bg-danger-600',
    }
    const percentage = props.max > 0 ? Math.min(100, (props.value / props.max) * 100) : 0
    return () => h('div', { class: 'space-y-1' }, [
      h('div', { class: 'flex justify-between text-sm' }, [
        h('span', { class: 'text-secondary-500' }, props.label),
        h('span', { class: 'font-medium text-secondary-900' }, props.value + (props.suffix || '')),
      ]),
      h('div', { class: 'h-2 bg-secondary-100 rounded-full overflow-hidden' }, [
        h('div', { 
          class: `h-full rounded-full ${colors[props.color] || colors.primary} transition-all duration-300`,
          style: { width: percentage + '%' }
        }),
      ]),
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
      blue: 'bg-blue-100 text-blue-600',
    }
    return () => h('span', { class: `badge ${colors[props.color] || colors.gray}` }, slots.default())
  },
}

function getPriorityColor(priority) {
  const colors = { low: 'gray', medium: 'blue', high: 'orange', critical: 'red' }
  return colors[priority] || 'gray'
}

function getRoleColor(role) {
  const colors = { owner: 'danger', manager: 'primary', member: 'success', viewer: 'gray' }
  return colors[role] || 'gray'
}

function formatDuration(minutes) {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins.toString().padStart(2, '0')}m`
}
</script>

<style scoped>
/* Project detail styles */
</style>