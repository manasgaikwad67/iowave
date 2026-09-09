<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { projectsApi } from '@/services/api-modules'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { RouterLink } from 'vue-router'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  FunnelIcon,
  BriefcaseIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/vue/24/outline'
import { BriefcaseIcon as BriefcaseIconSolid } from '@heroicons/vue/24/solid'
import { TransitionRoot } from '@headlessui/vue'
import { format } from 'date-fns'

const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()
const toast = useToast()

const projects = ref([])
const loading = ref(false)
const pagination = ref({ current_page: 1, last_page: 1, total: 0, per_page: 15 })
const filters = ref({
  search: '',
  status: '',
  client_id: '',
  department_id: '',
  sort: '-created_at',
  per_page: 15,
})
const showFilters = ref(false)
const clients = ref([])
const departments = ref([])
const deletingId = ref(null)

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'planning', label: 'Planning' },
  { value: 'active', label: 'Active' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
]

const statusColors = {
  planning: 'gray',
  active: 'blue',
  on_hold: 'yellow',
  completed: 'green',
  cancelled: 'red',
}

async function fetchProjects() {
  loading.value = true
  try {
    const response = await projectsApi.list(filters.value)
    projects.value = response.data.data
    pagination.value = response.data.meta
  } catch (error) {
    toast.error('Failed to load projects')
  } finally {
    loading.value = false
  }
}

async function fetchFilterOptions() {
  try {
    const [clientsRes, deptsRes] = await Promise.all([
      api.get('/clients', { params: { per_page: 100, is_active: true } }),
      api.get('/departments', { params: { is_active: true } }),
    ])
    clients.value = clientsRes.data.data
    departments.value = deptsRes.data.data
  } catch (error) {
    console.error('Failed to load filter options')
  }
}

async function deleteProject(id) {
  if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) return
  
  deletingId.value = id
  try {
    await projectsApi.delete(id)
    toast.success('Project deleted successfully')
    fetchProjects()
  } catch (error) {
    toast.error('Failed to delete project')
  } finally {
    deletingId.value = null
  }
}

function getStatusColor(status) {
  return statusColors[status] || 'gray'
}

function formatDate(date) {
  return date ? format(new Date(date), 'MMM d, yyyy') : '—'
}

watch(() => filters.value, () => {
  fetchProjects()
}, { deep: true })

onMounted(() => {
  uiStore.setPageTitle('Projects')
  uiStore.setBreadcrumbs([{ name: 'Projects' }])
  fetchProjects()
  fetchFilterOptions()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">Projects</h1>
        <p class="text-secondary-600 mt-1">Manage and track all your projects</p>
      </div>
      <RouterLink to="/projects/create" class="btn-primary">
        <PlusIcon class="w-5 h-5 mr-2" />
        New Project
      </RouterLink>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="px-6 py-4 border-b border-secondary-200 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-secondary-900 flex items-center gap-2">
          <FunnelIcon class="w-5 h-5" />
          Filters
        </h2>
        <button
          @click="showFilters = !showFilters"
          class="btn-secondary btn-sm"
        >
          <MagnifyingGlassIcon class="w-4 h-4 mr-1" />
          {{ showFilters ? 'Hide' : 'Show' }} Filters
        </button>
      </div>
      
      <TransitionRoot
        :show="showFilters"
        appear
        enter="transition ease-out duration-200"
        enter-from="opacity-0 -translate-y-2"
        enter-to="opacity-100 translate-y-0"
        leave="transition ease-in duration-150"
        leave-from="opacity-100 translate-y-0"
        leave-to="opacity-0 -translate-y-2"
      >
        <div v-show="showFilters" class="px-6 py-4 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label for="search" class="label">Search</label>
              <div class="relative mt-1">
                <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
                <input
                  id="search"
                  v-model="filters.search"
                  type="text"
                  class="input pl-10"
                  placeholder="Search projects..."
                  @keyup.enter="fetchProjects"
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
              <label for="client_id" class="label">Client</label>
              <select
                id="client_id"
                v-model="filters.client_id"
                class="input mt-1"
              >
                <option value="">All Clients</option>
                <option v-for="client in clients" :key="client.id" :value="client.id">{{ client.name }}</option>
              </select>
            </div>
            
            <div>
              <label for="department_id" class="label">Department</label>
              <select
                id="department_id"
                v-model="filters.department_id"
                class="input mt-1"
              >
                <option value="">All Departments</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
              </select>
            </div>
          </div>
          
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-secondary-100">
            <button @click="filters = { search: '', status: '', client_id: '', department_id: '', sort: '-created_at', per_page: 15 }" class="btn-secondary btn-sm">
              Clear Filters
            </button>
          </div>
        </div>
      </TransitionRoot>
    </div>

    <!-- Projects Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="table" v-if="!loading && projects.length">
          <thead>
            <tr>
              <th class="w-1/3">Project</th>
              <th>Client</th>
              <th>Status</th>
              <th>Progress</th>
              <th>Budget</th>
              <th class="w-32">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="project in projects" :key="project.id">
              <td>
                <RouterLink :to="`/projects/${project.id}`" class="font-medium text-secondary-900 hover:text-primary-600">
                  {{ project.name }}
                </RouterLink>
                <p class="text-sm text-secondary-500">{{ project.code }}</p>
              </td>
              <td>
                <span v-if="project.client">{{ project.client.name }}</span>
                <span v-else class="text-secondary-400">Internal</span>
              </td>
              <td>
                <span :class="`badge badge-${getStatusColor(project.status)}`" class="capitalize">{{ project.status.replace('_', ' ') }}</span>
              </td>
              <td>
                <div class="w-32">
                  <div class="h-1.5 bg-secondary-100 rounded-full overflow-hidden">
                    <div class="h-full bg-primary-600 rounded-full" :style="{ width: project.progress + '%' }"></div>
                  </div>
                  <p class="text-xs text-secondary-500 mt-1">{{ project.progress }}% complete</p>
                </div>
              </td>
              <td>
                <p class="font-medium text-secondary-900">${{ project.estimated_budget?.toLocaleString() || '0' }}</p>
                <p class="text-sm text-secondary-500">{{ project.budget_utilization }}% used</p>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <RouterLink :to="`/projects/${project.id}`" class="btn-ghost btn-sm p-2" title="View">
                    <BriefcaseIconSolid class="w-4 h-4" />
                  </RouterLink>
                  <RouterLink :to="`/projects/${project.id}/edit`" class="btn-ghost btn-sm p-2" title="Edit">
                    <PencilIcon class="w-4 h-4" />
                  </RouterLink>
                  <button @click="deleteProject(project.id)" :disabled="deletingId === project.id" class="btn-ghost btn-sm p-2 text-danger-600 hover:bg-danger-50" title="Delete">
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-secondary-500">Loading projects...</p>
        </div>
        
        <div v-if="!loading && !projects.length" class="p-12 text-center">
          <BriefcaseIcon class="w-16 h-16 mx-auto mb-4 text-secondary-300" />
          <h3 class="text-lg font-medium text-secondary-900 mb-2">No projects found</h3>
          <p class="text-secondary-500 mb-4">Get started by creating your first project</p>
          <RouterLink to="/projects/create" class="btn-primary inline-flex">
            <PlusIcon class="w-5 h-5 mr-2" />
            Create Project
          </RouterLink>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.last_page > 1" class="px-6 py-4 border-t border-secondary-200 flex items-center justify-between">
        <p class="text-sm text-secondary-500">
          Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} projects
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
import api from '@/services/api'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
</script>

<style scoped>
/* Projects view styles */
</style>