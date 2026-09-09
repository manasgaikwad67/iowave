<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { timeEntriesApi, projectsApi } from '@/services/api-modules'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { RouterLink } from 'vue-router'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  CalendarIcon,
  ClockIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'
import { format } from 'date-fns'

const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()
const toast = useToast()

const timeEntries = ref([])
const loading = ref(false)
const pagination = ref({ current_page: 1, last_page: 1, total: 0, per_page: 15 })
const filters = ref({
  search: '',
  status: '',
  project_id: '',
  start_date: '',
  end_date: '',
  sort: '-date',
  per_page: 15,
})
const projects = ref([])
const showFilters = ref(false)
const deletingId = ref(null)

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'invoiced', label: 'Invoiced' },
]

const statusColors = {
  draft: 'gray',
  pending: 'yellow',
  approved: 'green',
  rejected: 'red',
  invoiced: 'blue',
}

const statusIcons = {
  draft: '',
  pending: ExclamationTriangleIcon,
  approved: CheckCircleIcon,
  rejected: XCircleIcon,
  invoiced: '',
}

async function fetchTimeEntries() {
  loading.value = true
  try {
    const response = await timeEntriesApi.list(filters.value)
    timeEntries.value = response.data.data
    pagination.value = response.data.meta
  } catch (error) {
    toast.error('Failed to load time entries')
  } finally {
    loading.value = false
  }
}

async function fetchProjects() {
  try {
    const response = await projectsApi.list({ per_page: 100, is_active: true })
    projects.value = response.data.data
  } catch (error) {
    console.error('Failed to load projects')
  }
}

async function deleteTimeEntry(id) {
  if (!confirm('Are you sure you want to delete this time entry?')) return
  
  deletingId.value = id
  try {
    await timeEntriesApi.delete(id)
    toast.success('Time entry deleted')
    fetchTimeEntries()
  } catch (error) {
    toast.error('Failed to delete time entry')
  } finally {
    deletingId.value = null
  }
}

async function approveTimeEntry(id) {
  try {
    await timeEntriesApi.approve(id)
    toast.success('Time entry approved')
    fetchTimeEntries()
  } catch (error) {
    toast.error('Failed to approve time entry')
  }
}

async function rejectTimeEntry(id) {
  const reason = prompt('Please enter a reason for rejection:')
  if (!reason) return
  
  try {
    await timeEntriesApi.reject(id, reason)
    toast.success('Time entry rejected')
    fetchTimeEntries()
  } catch (error) {
    toast.error('Failed to reject time entry')
  }
}

function getStatusColor(status) {
  return statusColors[status] || 'gray'
}

function formatDate(date) {
  return date ? format(new Date(date), 'MMM d, yyyy') : '—'
}

function formatDuration(minutes) {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins.toString().padStart(2, '0')}m`
}

watch(() => filters.value, () => {
  fetchTimeEntries()
}, { deep: true })

onMounted(() => {
  uiStore.setPageTitle('Time Entries')
  uiStore.setBreadcrumbs([{ name: 'Time Tracking' }, { name: 'Time Entries' }])
  fetchTimeEntries()
  fetchProjects()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">Time Entries</h1>
        <p class="text-secondary-600 mt-1">Track and manage time entries</p>
      </div>
      <div class="flex gap-3">
        <RouterLink to="/time-entries/weekly" class="btn-secondary">
          <CalendarIcon class="w-5 h-5 mr-2" />
          Weekly View
        </RouterLink>
        <RouterLink to="/time-entries/create" class="btn-primary">
          <PlusIcon class="w-5 h-5 mr-2" />
          Log Time
        </RouterLink>
      </div>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="px-6 py-4 border-b border-secondary-200 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-secondary-900 flex items-center gap-2">
          <MagnifyingGlassIcon class="w-5 h-5" />
          Filters
        </h2>
        <button
          @click="showFilters = !showFilters"
          class="btn-secondary btn-sm"
        >
          {{ showFilters ? 'Hide' : 'Show' }} Filters
        </button>
      </div>
      
      <Transition appear enter="transition ease-out duration-200" enter-from="opacity-0 -translate-y-2" enter-to="opacity-100 translate-y-0" leave="transition ease-in duration-150" leave-from="opacity-100 translate-y-0" leave-to="opacity-0 -translate-y-2">
        <div v-show="showFilters" class="px-6 py-4 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label for="search" class="label">Search</label>
              <div class="relative mt-1">
                <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
                <input
                  id="search"
                  v-model="filters.search"
                  type="text"
                  class="input pl-10"
                  placeholder="Search entries..."
                />
              </div>
            </div>
            
            <div>
              <label for="status" class="label">Status</label>
              <select
                id="status"
                v-model="filters.status"
                class="input mt-1"
              >
                <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            
            <div>
              <label for="project_id" class="label">Project</label>
              <select
                id="project_id"
                v-model="filters.project_id"
                class="input mt-1"
              >
                <option value="">All Projects</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
              </select>
            </div>
            
            <div>
              <label for="start_date" class="label">From</label>
              <input
                id="start_date"
                v-model="filters.start_date"
                type="date"
                class="input mt-1"
              />
            </div>
            
            <div>
              <label for="end_date" class="label">To</label>
              <input
                id="end_date"
                v-model="filters.end_date"
                type="date"
                class="input mt-1"
              />
            </div>
          </div>
          
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-secondary-100">
            <button @click="filters = { search: '', status: '', project_id: '', start_date: '', end_date: '', sort: '-date', per_page: 15 }" class="btn-secondary btn-sm">
              Clear Filters
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Time Entries Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="table" v-if="!loading && timeEntries.length">
          <thead>
            <tr>
              <th class="w-32">Date</th>
              <th>User</th>
              <th>Project</th>
              <th>Task</th>
              <th>Duration</th>
              <th>Description</th>
              <th>Status</th>
              <th class="w-40">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in timeEntries" :key="entry.id">
              <td class="whitespace-nowrap">{{ formatDate(entry.date) }}</td>
              <td>
                <div class="flex items-center gap-2">
                  <img :src="entry.user?.avatar" :alt="entry.user?.full_name" class="w-6 h-6 rounded-full" />
                  <span>{{ entry.user?.full_name }}</span>
                </div>
              </td>
              <td>
                <span v-if="entry.project">{{ entry.project.name }}</span>
                <span v-else class="text-secondary-400">—</span>
              </td>
              <td>
                <span v-if="entry.task">{{ entry.task.title }}</span>
                <span v-else class="text-secondary-400">—</span>
              </td>
              <td class="font-mono">{{ formatDuration(entry.duration_minutes) }}</td>
              <td class="max-w-xs truncate">{{ entry.description || '—' }}</td>
              <td>
                <span :class="`badge badge-${getStatusColor(entry.status)}`" class="capitalize flex items-center gap-1">
                  <component v-if="statusIcons[entry.status]" :is="statusIcons[entry.status]" class="w-3 h-3" />
                  {{ entry.status }}
                </span>
              </td>
              <td>
                <div class="flex items-center gap-1">
                  <RouterLink :to="`/time-entries/${entry.id}/edit`" class="btn-ghost btn-sm p-2" title="Edit">
                    <PencilIcon class="w-4 h-4" />
                  </RouterLink>
                  <template v-if="entry.status === 'pending' && authStore.hasPermission('time_entries.approve')">
                    <button @click="approveTimeEntry(entry.id)" class="btn-ghost btn-sm p-2 text-success-600 hover:bg-success-50" title="Approve">
                      <CheckCircleIcon class="w-4 h-4" />
                    </button>
                    <button @click="rejectTimeEntry(entry.id)" class="btn-ghost btn-sm p-2 text-danger-600 hover:bg-danger-50" title="Reject">
                      <XCircleIcon class="w-4 h-4" />
                    </button>
                  </template>
                  <button @click="deleteTimeEntry(entry.id)" :disabled="deletingId === entry.id" class="btn-ghost btn-sm p-2 text-danger-600 hover:bg-danger-50" title="Delete">
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-secondary-500">Loading time entries...</p>
        </div>
        
        <div v-if="!loading && !timeEntries.length" class="p-12 text-center">
          <ClockIcon class="w-16 h-16 mx-auto mb-4 text-secondary-300" />
          <h3 class="text-lg font-medium text-secondary-900 mb-2">No time entries found</h3>
          <p class="text-secondary-500 mb-4">Start tracking your time</p>
          <RouterLink to="/time-entries/create" class="btn-primary inline-flex">
            <PlusIcon class="w-5 h-5 mr-2" />
            Log Time
          </RouterLink>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.last_page > 1" class="px-6 py-4 border-t border-secondary-200 flex items-center justify-between">
        <p class="text-sm text-secondary-500">
          Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} entries
        </p>
        <div class="flex gap-2">
          <button
            @click="pagination.current_page > 1 && (filters.page = pagination.current_page - 1)"
            :disabled="pagination.current_page <= 1"
            class="btn-secondary btn-sm"
          >
            <ChevronLeftIcon class="w-4 h-4" />
          </button>
          <button
            @click="pagination.current_page < pagination.last_page && (filters.page = pagination.current_page + 1)"
            :disabled="pagination.current_page >= pagination.last_page"
            class="btn-secondary btn-sm"
          >
            <ChevronRightIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { h } from 'vue'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
</script>

<style scoped>
/* Time entries view styles */
</style>