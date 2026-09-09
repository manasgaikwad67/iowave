import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const sidebarOpen = ref(false)
  const sidebarCollapsed = ref(false)
  const theme = ref(localStorage.getItem('theme') || 'light')
  const rightSidebarOpen = ref(false)
  const loading = ref(false)
  const pageTitle = ref('')
  const breadcrumbs = ref([])

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function closeSidebar() {
    sidebarOpen.value = false
  }

  function toggleSidebarCollapsed() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function initTheme() {
    if (theme.value === 'dark' || (!theme.value && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    initTheme()
  }

  watch(theme, (newTheme) => {
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('theme', newTheme)
  })

  function setLoading(value) {
    loading.value = value
  }

  function setPageTitle(title) {
    pageTitle.value = title
    document.title = title ? `${title} | ERP System` : 'ERP System'
  }

  function setBreadcrumbs(crumbs) {
    breadcrumbs.value = crumbs
  }

  function toggleRightSidebar() {
    rightSidebarOpen.value = !rightSidebarOpen.value
  }

  function closeRightSidebar() {
    rightSidebarOpen.value = false
  }

  return {
    sidebarOpen,
    sidebarCollapsed,
    theme,
    rightSidebarOpen,
    loading,
    pageTitle,
    breadcrumbs,
    toggleSidebar,
    closeSidebar,
    toggleSidebarCollapsed,
    initTheme,
    toggleTheme,
    setLoading,
    setPageTitle,
    setBreadcrumbs,
    toggleRightSidebar,
    closeRightSidebar,
  }
})