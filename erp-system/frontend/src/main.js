import { createApp } from 'vue'
import { pinia } from './stores/pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import router from './router'
import { useAuthStore } from './stores/auth'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import './assets/main.css'
import App from './App.vue'

const app = createApp(App)
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore(pinia)
  const token = authStore.token || localStorage.getItem('token')
  const isAuthenticated = !!token

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.meta.requiresGuest && isAuthenticated) {
    return next({ name: 'dashboard' })
  }

  return next()
})

app.use(router)
app.use(Toast, {
  position: 'top-right',
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false,
})

app.mount('#app')