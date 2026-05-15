import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('autoincome_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('autoincome_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const opportunitiesApi = {
  list: (params?: { min_score?: number; max_results?: number; tag?: string }) =>
    api.get('/opportunities', { params }).then((r) => r.data),
  get: (id: string) => api.get(`/opportunities/${id}`).then((r) => r.data),
  scan: (params?: { sources?: string[]; min_score?: number; max_results?: number }) =>
    api.post('/opportunities/scan', null, { params }).then((r) => r.data),
}

export const healthApi = {
  check: () => api.get('/health').then((r) => r.data),
}

export const userApi = {
  getProfile: () => api.get('/config/profile').then((r) => r.data),
  updateProfile: (data: Partial<UserProfile>) =>
    api.put('/config/profile', data).then((r) => r.data),
}

export const incomeApi = {
  list: () => api.get('/income').then((r) => r.data),
  create: (data: Partial<IncomeRecord>) =>
    api.post('/income', data).then((r) => r.data),
}

import type { UserProfile, IncomeRecord } from '../types'