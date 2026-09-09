<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import api from '@/services/api'
import { RouterLink } from 'vue-router'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  UserPlusIcon,
  ShieldCheckIcon,
} from '@heroicons/vue/24/outline'
import { format } from 'date-fns'

const authStore = useAuthStore()
const toast = useToast()

const users = ref([])
const loading = ref(false)
const pagination = ref({ current_page: 1, last_page: 1, total: 0, per_page: 15 })
const filters = ref({
  search: '',
  role: '',
  department_id: '',
  is_active: '',
  sort: '-created_at',
  per_page: 15,
})
const showFilters = ref(false)
const departments = ref([])
const roles = ref([])
const deletingId = ref(null)

async function fetchUsers() {
  loading.value = true
  try {
    const response = await api.get('/users', { params: filters.value })
    users.value = response.data.data
    pagination.value = response.data.meta
  } catch (error) {
    toast.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

async function fetchFilterOptions() {
  try {
    const [deptsRes, rolesRes] = await Promise.all([
      api.get('/departments', { params: { is_active: true } }),
      api.get('/roles', { params: { per_page: 100 } }),
    ])
    departments.value = deptsRes.data.data
    roles.value = rolesRes.data.data
  } catch (error) {
    console.error('Failed to load filter options')
  }
}

async function deleteUser(id) {
  if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return
  
  deletingId.value = id
  try {
    await api.delete(`/users/${id}`)
    toast.success('User deleted successfully')
    fetchUsers()
  } catch (error) {
    toast.error('Failed to delete user')
  } finally {
    deletingId.value = null
  }
}

function formatDate(date) {
  return date ? format(new Date(date), 'MMM d, yyyy') : '—'
}

function getRoleBadge(role) {
  const colors = {
    'Super Admin': 'danger',
    'Admin': 'primary',
    'Project Manager': 'success',
    'Team Lead': 'warning',
    'Senior Consultant': 'blue',
    'Consultant': 'gray',
    'Client': 'indigo',
  }
  return colors[role] || 'gray'
}

watch(() => filters.value, () => {
  fetchUsers()
}, { deep: true })

onMounted(() => {
  fetchUsers()
  fetchFilterOptions()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-900">Users</h1>
        <p class="text-secondary-600 mt-1">Manage user accounts and permissions</p>
      </div>
      <RouterLink to="/settings/users/create" class="btn-primary">
        <UserPlusIcon class="w-5 h-5 mr-2" />
        Add User
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
                  placeholder="Search users..."
                />
              </div>
            </div>
            
            <div>
              <label for="role" class="label">Role</label>
              <select
                id="role"
                v-model="filters.role"
                class="input mt-1"
              >
                <option value="">All Roles</option>
                <option v-for="role in roles" :key="role.name" :value="role.name">{{ role.name }}</option>
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
            
            <div>
              <label for="is_active" class="label">Status</label>
              <select
                id="is_active"
                v-model="filters.is_active"
                class="input mt-1"
              >
                <option value="">All</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
          </div>
          
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-secondary-100">
            <button @click="filters = { search: '', role: '', department_id: '', is_active: '', sort: '-created_at', per_page: 15 }" class="btn-secondary btn-sm">
              Clear Filters
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Users Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="table" v-if="!loading && users.length">
          <thead>
            <tr>
              <th class="w-1/3">User</th>
              <th>Role</th>
              <th>Department</th>
              <th>Status</th>
              <th>Last Login</th>
              <th class="w-32">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>
                <div class="flex items-center gap-3">
                  <img :src="user.avatar" :alt="user.full_name" class="w-8 h-8 rounded-full" />
                  <div>
                    <RouterLink :to="`/settings/users/${user.id}`" class="font-medium text-secondary-900 hover:text-primary-600">
                      {{ user.full_name }}
                    </RouterLink>
                    <p class="text-sm text-secondary-500">{{ user.email }}</p>
                  </div>
                </div>
              </td>
              <td>
                <span v-for="role in user.roles" :key="role" :class="`badge badge-${getRoleBadge(role)}`" class="mr-1">
                  {{ role }}
                </span>
              </td>
              <td>{{ user.department?.name || '—' }}</td>
              <td>
                <span :class="user.is_active ? 'badge badge-success' : 'badge badge-danger'">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="text-sm text-secondary-500">{{ formatDate(user.last_login_at) }}</td>
              <td>
                <div class="flex items-center gap-1">
                  <RouterLink :to="`/settings/users/${user.id}`" class="btn-ghost btn-sm p-2" title="View">
                    <EyeIcon class="w-4 h-4" />
                  </RouterLink>
                  <RouterLink :to="`/settings/users/${user.id}/edit`" class="btn-ghost btn-sm p-2" title="Edit">
                    <PencilIcon class="w-4 h-4" />
                  </RouterLink>
                  <RouterLink :to="`/settings/users/${user.id}/roles`" class="btn-ghost btn-sm p-2" title="Manage Roles">
                    <ShieldCheckIcon class="w-4 h-4" />
                  </RouterLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-secondary-500">Loading users...</p>
        </div>
        
        <div v-if="!loading && !users.length" class="p-12 text-center">
          <UsersIcon class="w-16 h-16 mx-auto mb-4 text-secondary-300" />
          <h3 class="text-lg font-medium text-secondary-900 mb-2">No users found</h3>
          <p class="text-secondary-500 mb-4">Add your first user</p>
          <RouterLink to="/settings/users/create" class="btn-primary inline-flex">
            <PlusIcon class="w-5 h-5 mr-2" />
            Add User
          </RouterLink>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.last_page > 1" class="px-6 py-4 border-t border-secondary-200 flex items-center justify-between">
        <p class="text-sm text-secondary-500">
          Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} users
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
import { UsersIcon, EyeIcon, PencilIcon } from '@heroicons/vue/24/outline'
</script>

<style scoped>
/* Users settings styles */
</style>