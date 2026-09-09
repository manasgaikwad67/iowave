import api from './api'

export const projectsApi = {
  list: (params) => api.get('/projects', { params }),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
  members: (id) => api.get(`/projects/${id}/members`),
  addMember: (id, data) => api.post(`/projects/${id}/members`, data),
  removeMember: (id, userId) => api.delete(`/projects/${id}/members/${userId}`),
  updateMember: (id, userId, data) => api.put(`/projects/${id}/members/${userId}`, data),
  statistics: () => api.get('/projects/statistics'),
}

export const timeEntriesApi = {
  list: (params) => api.get('/time-entries', { params }),
  get: (id) => api.get(`/time-entries/${id}`),
  create: (data) => api.post('/time-entries', data),
  bulkCreate: (data) => api.post('/time-entries/bulk', data),
  update: (id, data) => api.put(`/time-entries/${id}`, data),
  delete: (id) => api.delete(`/time-entries/${id}`),
  submit: (id) => api.post(`/time-entries/${id}/submit`),
  approve: (id) => api.post(`/time-entries/${id}/approve`),
  reject: (id, reason) => api.post(`/time-entries/${id}/reject`, { rejection_reason: reason }),
  myEntries: (params) => api.get('/time-entries/my/entries', { params }),
  weeklySummary: (params) => api.get('/time-entries/my/weekly-summary', { params }),
  pendingApprovals: (params) => api.get('/time-entries/pending/approvals', { params }),
}

export const clientsApi = {
  list: (params) => api.get('/clients', { params }),
  get: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
  contacts: (id, params) => api.get(`/clients/${id}/contacts`, { params }),
}

export const invoicesApi = {
  list: (params) => api.get('/invoices', { params }),
  get: (id) => api.get(`/invoices/${id}`),
  create: (data) => api.post('/invoices', data),
  update: (id, data) => api.put(`/invoices/${id}`, data),
  delete: (id) => api.delete(`/invoices/${id}`),
  send: (id) => api.post(`/invoices/${id}/send`),
  addPayment: (id, data) => api.post(`/invoices/${id}/payments`, data),
}

export const expensesApi = {
  list: (params) => api.get('/expenses', { params }),
  get: (id) => api.get(`/expenses/${id}`),
  create: (data) => api.post('/expenses', data),
  update: (id, data) => api.put(`/expenses/${id}`, data),
  delete: (id) => api.delete(`/expenses/${id}`),
  approve: (id) => api.post(`/expenses/${id}/approve`),
  reject: (id, reason) => api.post(`/expenses/${id}/reject`, { rejection_reason: reason }),
}

export const usersApi = {
  list: (params) => api.get('/users', { params }),
  get: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  assignRole: (id, role) => api.post(`/users/${id}/roles`, { role }),
  removeRole: (id, role) => api.delete(`/users/${id}/roles/${role}`),
}

export const departmentsApi = {
  list: (params) => api.get('/departments', { params }),
  get: (id) => api.get(`/departments/${id}`),
  create: (data) => api.post('/departments', data),
  update: (id, data) => api.put(`/departments/${id}`, data),
  delete: (id) => api.delete(`/departments/${id}`),
}

export const dashboardApi = {
  stats: () => api.get('/dashboard/stats'),
}

export const reportsApi = {
  utilization: (params) => api.get('/reports/utilization', { params }),
  projectProfitability: (params) => api.get('/reports/project-profitability', { params }),
  financial: (params) => api.get('/reports/financial', { params }),
  timeEntries: (params) => api.get('/reports/time-entries', { params }),
}