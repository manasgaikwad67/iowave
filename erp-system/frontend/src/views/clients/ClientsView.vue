<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { clientsApi } from '@/services/api-modules'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { RouterLink } from 'vue-router'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  BuildingOfficeIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
} from '@heroicons/vue/24/outline'
import { BuildingOfficeIcon as BuildingOfficeIconSolid } from '@heroicons/vue/24/solid'
import { format } from 'date-fns'

const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()
const toast = useToast()

const clients = ref([])
const loading = ref(false)
const pagination = ref({ current_page: 1, last_page: 1, total: 0, per_page: 15 })
const filters = ref({
  search: '',
  status: '',
  account_manager_id: '',
  sort: 'name',
  per_page: 15,
})
const showFilters = ref(false)
const deletingId = ref(null)

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'lead', label: 'Lead' },
  { value: 'prospect', label: 'Prospect' },
  { value: 'active', label: 'Active' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'inactive', label: 'Inactive' },
]

const statusColors = {
  lead: 'gray',
  prospect: 'blue',
  active: 'green',
  on_hold: 'yellow',
  inactive: 'red',
}

async function fetchClients() {
  loading.value = true
  try {
    const response = await clientsApi.list(filters.value)
    clients.value = response.data.data
    pagination.value = response.data.meta
  } catch (error) {
    toast.error('Failed to load clients')
  } finally {
    loading.value = false
  }
}

async function deleteClient(id) {
  if (!confirm('Are you sure you want to delete this client? This action cannot be undone.')) return
  
  deletingId.value = id
  try {
    await clientsApi.delete(id)
    toast.success('Client deleted successfully')
    fetchClients()
  } catch (error) {
    toast.error('Failed to delete client')
  } finally {
    deletingId.value = null
  }
}

function getStatusColor(status) {
  return statusColors[status] || 'gray'
}

function formatCurrency(amount) {
  if (!amount) return '$0'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(amount)
}

watch(() => filters.value, () => {
  fetchClients()
}, { deep: true })

onMounted(() => {
  uiStore.setPageTitle('Clients')
  uiStore.setBreadcrumbs([{ name: 'Clients' }])
  fetchClients()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">Clients</h1>
        <p class="text-secondary-600 mt-1">Manage your client relationships</p>
      </div>
      <RouterLink to="/clients/create" class="btn-primary">
        <PlusIcon class="w-5 h-5 mr-2" />
        New Client
      </RouterLink>
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
                  placeholder="Search clients..."
                  @keyup.enter="fetchClients"
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
              <label for="account_manager_id" class="label">Account Manager</label>
              <select
                id="account_manager_id"
                v-model="filters.account_manager_id"
                class="input mt-1"
              >
                <option value="">All Managers</option>
                <option v-for="user in accountManagers" :key="user.id" :value="user.id">{{ user.first_name }} {{ user.last_name }}</option>
              </select>
            </div>
          </div>
          
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-secondary-100">
            <button @click="filters = { search: '', status: '', account_manager_id: '', sort: 'name', per_page: 15 }" class="btn-secondary btn-sm">
              Clear Filters
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Clients Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="table" v-if="!loading && clients.length">
          <thead>
            <tr>
              <th class="w-1/3">Client</th>
              <th>Contact</th>
              <th>Status</th>
              <th>Industry</th>
              <th>Projects</th>
              <th>Revenue</th>
              <th class="w-32">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="client in clients" :key="client.id">
              <td>
                <RouterLink :to="`/clients/${client.id}`" class="font-medium text-secondary-900 hover:text-primary-600">
                  {{ client.name }}
                </RouterLink>
                <p class="text-sm text-secondary-500">{{ client.code }}</p>
              </td>
              <td>
                <div v-if="client.contact_person">
                  <p>{{ client.contact_person }}</p>
                  <p class="text-sm text-secondary-500">{{ client.contact_email }}</p>
                </div>
                <span v-else class="text-secondary-400">—</span>
              </td>
              <td>
                <span :class="`badge badge-${getStatusColor(client.status)}`" class="capitalize">{{ client.status }}</span>
              </td>
              <td>{{ client.industry || '—' }}</td>
              <td class="font-medium text-secondary-900">{{ client.projects_count || 0 }}</td>
              <td>{{ formatCurrency(client.total_invoiced) }}</td>
              <td>
                <div class="flex items-center gap-2">
                  <RouterLink :to="`/clients/${client.id}`" class="btn-ghost btn-sm p-2" title="View">
                    <BuildingOfficeIconSolid class="w-4 h-4" />
                  </RouterLink>
                  <RouterLink :to="`/clients/${client.id}/edit`" class="btn-ghost btn-sm p-2" title="Edit">
                    <PencilIcon class="w-4 h-4" />
                  </RouterLink>
                  <button @click="deleteClient(client.id)" :disabled="deletingId === client.id" class="btn-ghost btn-sm p-2 text-danger-600 hover:bg-danger-50" title="Delete">
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-secondary-500">Loading clients...</p>
        </div>
        
        <div v-if="!loading && !clients.length" class="p-12 text-center">
          <BuildingOfficeIcon class="w-16 h-16 mx-auto mb-4 text-secondary-300" />
          <h3 class="text-lg font-medium text-secondary-900 mb-2">No clients found</h3>
          <p class="text-secondary-500 mb-4">Get started by adding your first client</p>
          <RouterLink to="/clients/create" class="btn-primary inline-flex">
            <PlusIcon class="w-5 h-5 mr-2" />
            Add Client
          </RouterLink>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.last_page > 1" class="px-6 py-4 border-t border-secondary-200 flex items-center justify-between">
        <p class="text-sm text-secondary-500">
          Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} clients
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

const accountManagers = ref([])
onMounted(async () => {
  try {
    const response = await api.get('/users', { params: { role: 'Senior Consultant', per_page: 100 } })
    accountManagers.value = response.data.data
  } catch (error) {
    console.error('Failed to load account managers')
  }
})
</script>

<style scoped>
/* Clients view styles */
</style>