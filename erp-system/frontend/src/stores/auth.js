import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userName = computed(() => user.value ? `${user.value.first_name} ${user.value.last_name}` : '')
  const userAvatar = computed(() => user.value?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(userName.value)}&background=random`)
  const roles = computed(() => user.value?.roles || [])
  const permissions = computed(() => user.value?.permissions || [])

  const hasRole = (role) => roles.value.includes(role)
  const hasAnyRole = (roleList) => roleList.some(role => roles.value.includes(role))
  const hasPermission = (permission) => permissions.value.includes(permission)
  const hasAnyPermission = (permissionList) => permissionList.some(p => permissions.value.includes(p))

  async function initAuth() {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      try {
        const response = await api.get('/auth/me')
        user.value = response.data.data
      } catch (error) {
        logout()
      }
    }
    initialized.value = true
  }

  async function login(credentials) {
    const response = await api.post('/auth/login', credentials)
    token.value = response.data.data.token
    user.value = response.data.data.user
    localStorage.setItem('token', token.value)
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    return response.data
  }

  async function register(userData) {
    const response = await api.post('/auth/register', userData)
    token.value = response.data.data.token
    user.value = response.data.data.user
    localStorage.setItem('token', token.value)
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    return response.data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
  }

  async function updateProfile(data) {
    const response = await api.put('/auth/profile', data)
    user.value = response.data.data
    return response.data
  }

  async function updatePassword(data) {
    return await api.put('/auth/password', data)
  }

  function setUser(userData) {
    user.value = userData
  }

  return {
    user,
    token,
    initialized,
    isAuthenticated,
    userName,
    userAvatar,
    roles,
    permissions,
    hasRole,
    hasAnyRole,
    hasPermission,
    hasAnyPermission,
    initAuth,
    login,
    register,
    logout,
    updateProfile,
    updatePassword,
    setUser,
  }
})