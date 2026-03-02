import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const register = (email, password) =>
  api.post('/auth/register', { email, password })
export const login = (email, password) =>
  api.post('/auth/login', { email, password })
export const getProfile = () => api.get('/profile')
export const submitQuiz = (data) => api.post('/quiz', data)
export const generateRecommendations = () => api.post('/recommendations/generate')
export const getWeekRecommendations = () => api.get('/recommendations/week')
export const submitFeedback = (data) => api.post('/feedback', data)
export const regenerateDay = (day) => api.post(`/recommendations/regenerate/${day}`)
