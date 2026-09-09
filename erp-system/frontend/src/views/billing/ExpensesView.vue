<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { expensesApi, projectsApi } from '@/services/api-modules'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { RouterLink } from 'vue-router'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CreditCardIcon,
  ReceiptPercentIcon,
} from '@heroicons/vue/24/outline'
import { CreditCardIcon as CreditCardIconSolid } from '@heroicons/vue/24/solid'
import { format } from 'date-fns'

const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()
const toast = useToast()

const expenses = ref([])
const loading = ref(false)
const pagination = ref({ current_page: 1, last_page: 1, total: 0, per_page: 15 })
const filters = ref({
  search: '',
  status: '',
  project_id: '',
  category: '',
  start_date: '',
  end_date: '',
  sort: '-expense_date',
  per_page: 15,
})
const showFilters = ref(false)
const projects = ref([])
const categories = ['Travel', 'Meals', 'Software', 'Hardware', 'Training', 'Office Supplies', 'Other']
const deletingId = ref(null)

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'reimbursed', label: 'Reimbursed' },
]

const statusColors = {
  draft: 'gray',
  pending: 'yellow',
  approved: 'green',
  rejected: 'red',
  reimbursed: 'blue',
}

async function fetchExpenses() {
  loading.value = true
  try {
    const response = await expensesApi.list(filters.value)
    expenses.value = response.data.data
    pagination.value = response.data.meta
  } catch (error) {
    toast.error('Failed to load expenses')
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

watch(() => filters.value, () => {
  fetchExpenses()
}, { deep: true })

onMounted(() => {
  uiStore.setPageTitle('Expenses')
  uiStore.setBreadcrumbs([{ name: 'Billing' }, { name: 'Expenses' }])
  fetchExpenses()
  fetchProjects()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">Expenses</h1>
        <p class="text-secondary-600 mt-1">Track and manage expenses</p>
      </div>
      <RouterLink to="/expenses/create" class="btn-primary">
        <PlusIcon class="w-5 h-5 mr-2" />
        Add Expense
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
                  placeholder="Search expenses..."
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
              <label for="category" class="label">Category</label>
              <select
                id="category"
                v-model="filters.category"
                class="input mt-1"
              >
                <option value="">All Categories</option>
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
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
          </div>
          
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-secondary-100">
            <button @click="filters = { search: '', status: '', project_id: '', category: '', start_date: '', end_date: '', sort: '-expense_date', per_page: 15 }" class="btn-secondary btn-sm">
              Clear Filters
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Expenses Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="table" v-if="!loading && expenses.length">
          <thead>
            <tr>
              <th class="w-32">Date</th>
              <th>Submitted By</th>
              <th>Project</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Description</th>
              <th>Status</th>
              <th class="w-32">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="expense in expenses" :key="expense.id">
              <td class="whitespace-nowrap">{{ formatDate(expense.expense_date) }}</td>
              <td>
                <div class="flex items-center gap-2">
                  <img :src="expense.user?.avatar" :alt="expense.user?.full_name" class="w-6 h-6 rounded-full" />
                  <span>{{ expense.user?.full_name }}</span>
                </div>
              </td>
              <td>
                <span v-if="expense.project">{{ expense.project.name }}</span>
                <span v-else class="text-secondary-400">—</span>
              </td>
              <td>{{ expense.category }}</td>
              <td class="font-medium text-secondary-900">{{ formatCurrency(expense.amount) }}</td>
              <td class="max-w-xs truncate">{{ expense.description || '—' }}</td>
              <td>
                <span :class="`badge badge-${getStatusColor(expense.status)}`" class="capitalize">{{ expense.status }}</span>
              </td>
              <td>
                <div class="flex items-center gap-1">
                  <RouterLink :to="`/expenses/${expense.id}/edit`" class="btn-ghost btn-sm p-2" title="Edit">
                    <PencilIcon class="w-4 h-4" />
                  </RouterLink>
                  <template v-if="expense.status === 'pending' && authStore.hasPermission('expenses.approve')">
                    <button @click="approveExpense(expense.id)" class="btn-ghost btn-sm p-2 text-success-600 hover:bg-success-50" title="Approve">
                      <CheckCircleIcon class="w-4 h-4" />
                    </button>
                    <button @click="rejectExpense(expense.id)" class="btn-ghost btn-sm p-2 text-danger-600 hover:bg-danger-50" title="Reject">
                      <XCircleIcon class="w-4 h-4" />
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-secondary-500">Loading expenses...</p>
        </div>
        
        <div v-if="!loading && !expenses.length" class="p-12 text-center">
          <CreditCardIcon class="w-16 h-16 mx-auto mb-4 text-secondary-300" />
          <h3 class="text-lg font-medium text-secondary-900 mb-2">No expenses found</h3>
          <p class="text-secondary-500 mb-4">Add your first expense</p>
          <RouterLink to="/expenses/create" class="btn-primary inline-flex">
            <PlusIcon class="w-5 h-5 mr-2" />
            Add Expense
          </RouterLink>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.last_page > 1" class="px-6 py-4 border-t border-secondary-200 flex items-center justify-between">
        <p class="text-sm text-secondary-500">
          Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} expenses
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
import { PencilIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/vue/24/outline'

async function approveExpense(id) {
  try {
    await expensesApi.approve(id)
    toast.success('Expense approved')
    fetchExpenses()
  } catch (error) {
    toast.error('Failed to approve expense')
  }
}

async function rejectExpense(id) {
  const reason = prompt('Please enter a reason for rejection:')
  if (!reason) return
  
  try {
    await expensesApi.reject(id, reason)
    toast.success('Expense rejected')
    fetchExpenses()
  } catch (error) {
    toast.error('Failed to reject expense')
  }
}
</script>

<style scoped>
/* Expenses view styles */
</style>