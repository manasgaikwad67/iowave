import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { layout: 'auth', requiresGuest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { layout: 'auth', requiresGuest: true },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/projects',
    name: 'projects',
    component: () => import('@/views/projects/ProjectsView.vue'),
    meta: { requiresAuth: true, permission: 'projects.view' },
  },
  {
    path: '/projects/:id',
    name: 'projects-show',
    component: () => import('@/views/projects/ProjectDetailView.vue'),
    meta: { requiresAuth: true, permission: 'projects.view' },
    props: true,
  },
  {
    path: '/time-entries',
    name: 'time-entries',
    component: () => import('@/views/time-tracking/TimeEntriesView.vue'),
    meta: { requiresAuth: true, permission: 'time_entries.view' },
  },
  {
    path: '/clients',
    name: 'clients',
    component: () => import('@/views/clients/ClientsView.vue'),
    meta: { requiresAuth: true, permission: 'clients.view' },
  },
  {
    path: '/invoices',
    name: 'invoices',
    component: () => import('@/views/billing/InvoicesView.vue'),
    meta: { requiresAuth: true, permission: 'invoices.view' },
  },
  {
    path: '/expenses',
    name: 'expenses',
    component: () => import('@/views/billing/ExpensesView.vue'),
    meta: { requiresAuth: true, permission: 'expenses.view' },
  },
  {
    path: '/reports',
    name: 'reports',
    component: () => import('@/views/reports/ReportsView.vue'),
    meta: { requiresAuth: true, permission: 'reports.view' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'profile',
        name: 'settings-profile',
        component: () => import('@/views/settings/ProfileSettingsView.vue'),
      },
      {
        path: 'preferences',
        name: 'settings-preferences',
        component: () => import('@/views/settings/PreferencesSettingsView.vue'),
      },
      {
        path: 'users',
        name: 'settings-users',
        component: () => import('@/views/settings/UsersSettingsView.vue'),
        meta: { permission: 'users.view' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }

    return { top: 0 }
  },
})

export default router
