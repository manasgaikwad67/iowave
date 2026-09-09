<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { invoicesApi } from '@/services/api-modules'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { RouterLink } from 'vue-router'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  EyeIcon,
} from '@heroicons/vue/24/outline'
import { DocumentTextIcon as DocumentTextIconSolid } from '@heroicons/vue/24/solid'
import { format } from 'date-fns'

const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()
const toast = useToast()

const invoices = ref([])
const loading = ref(false)
const pagination = ref({ current_page: 1, last_page: 1, total: 0, per_page: 15 })
const filters = ref({
  search: '',
  status: '',
  client_id: '',
  start_date: '',
  end_date: '',
  sort: '-issue_date',
  per_page: 15,
})
const showFilters = ref(false)
const clients = ref([])
const deletingId = ref(null)

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'sent', label: 'Sent' },
  { value: 'viewed', label: 'Viewed' },
  { value: 'partial', label: 'Partial' },
  { value: 'paid', label: 'Paid' },
  { value: 'overdue', label: 'Overdue' },
  { value: 'cancelled', label: 'Cancelled' },
]

const statusColors = {
  draft: 'gray',
  sent: 'blue',
  viewed: 'indigo',
  partial: 'yellow',
  paid: 'green',
  overdue: 'red',
  cancelled: 'red',
}

async function fetchInvoices() {
  loading.value = true
  try {
    const response = await invoicesApi.list(filters.value)
    invoices.value = response.data.data
    pagination.value = response.data.meta
  } catch (error) {
    toast.error('Failed to load invoices')
  } finally {
    loading.value = false
  }
}

async function fetchClients() {
  try {
    const response = await api.get('/clients', { params: { per_page: 100, is_active: true } })
    clients.value = response.data.data
  } catch (error) {
    console.error('Failed to load clients')
  }
}

function getStatusColor(status) {
  return statusColors[status] || 'gray'
}

function formatCurrency(amount) {
  if (!amount) return '$0'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(amount)
}

function formatDate(date) {
  return date ? format(new Date(date), 'MMM d, yyyy') : '—'
}

async function downloadInvoice(id) {
  try {
    const response = await invoicesApi.get(id)
    // In a real app, this would generate/download a PDF
    toast.success('Invoice download started')
  } catch (error) {
    toast.error('Failed to download invoice')
  }
}

watch(() => filters.value, () => {
  fetchInvoices()
}, { deep: true })

onMounted(() => {
  uiStore.setPageTitle('Invoices')
  uiStore.setBreadcrumbs([{ name: 'Billing' }, { name: 'Invoices' }])
  fetchInvoices()
  fetchClients()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">Invoices</h1>
        <p class="text-secondary-600 mt-1">Manage and track invoices</p>
      </div>
      <RouterLink to="/invoices/create" class="btn-primary">
        <PlusIcon class="w-5 h-5 mr-2" />
        Create Invoice
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
                  placeholder="Search invoices..."
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
            <button @click="filters = { search: '', status: '', client_id: '', start_date: '', end_date: '', sort: '-issue_date', per_page: 15 }" class="btn-secondary btn-sm">
              Clear Filters
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Invoices Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="table" v-if="!loading && invoices.length">
          <thead>
            <tr>
              <th>Invoice #</th>
              <th>Client</th>
              <th>Issue Date</th>
              <th>Due Date</th>
              <th>Amount</th>
              <th>Paid</th>
              <th>Balance</th>
              <th>Status</th>
              <th class="w-40">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="invoice in invoices" :key="invoice.id">
              <td>
                <RouterLink :to="`/invoices/${invoice.id}`" class="font-medium text-secondary-900 hover:text-primary-600">
                  {{ invoice.invoice_number }}
                </RouterLink>
              </td>
              <td>
                <span v-if="invoice.client">{{ invoice.client.name }}</span>
                <span v-else class="text-secondary-400">—</span>
              </td>
              <td>{{ formatDate(invoice.issue_date) }}</td>
              <td :class="invoice.is_overdue ? 'text-danger-600 font-medium' : ''">{{ formatDate(invoice.due_date) }}</td>
              <td class="font-medium text-secondary-900">{{ formatCurrency(invoice.total_amount) }}</td>
              <td>{{ formatCurrency(invoice.amount_paid) }}</td>
              <td :class="invoice.balance_due > 0 ? 'text-danger-600 font-medium' : 'text-success-600'">
                {{ formatCurrency(invoice.balance_due) }}
              </td>
              <td>
                <span :class="`badge badge-${getStatusColor(invoice.status)}`" class="capitalize">{{ invoice.status }}</span>
              </td>
              <td>
                <div class="flex items-center gap-1">
                  <RouterLink :to="`/invoices/${invoice.id}`" class="btn-ghost btn-sm p-2" title="View">
                    <EyeIcon class="w-4 h-4" />
                  </RouterLink>
                  <button @click="downloadInvoice(invoice.id)" class="btn-ghost btn-sm p-2" title="Download PDF">
                    <ArrowDownTrayIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-secondary-500">Loading invoices...</p>
        </div>
        
        <div v-if="!loading && !invoices.length" class="p-12 text-center">
          <DocumentTextIcon class="w-16 h-16 mx-auto mb-4 text-secondary-300" />
          <h3 class="text-lg font-medium text-secondary-900 mb-2">No invoices found</h3>
          <p class="text-secondary-500 mb-4">Create your first invoice</p>
          <RouterLink to="/invoices/create" class="btn-primary inline-flex">
            <PlusIcon class="w-5 h-5 mr-2" />
            Create Invoice
          </RouterLink>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.last_page > 1" class="px-6 py-4 border-t border-secondary-200 flex items-center justify-between">
        <p class="text-sm text-secondary-500">
          Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} invoices
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
</script>

<style scoped>
/* Invoices view styles */
</style>