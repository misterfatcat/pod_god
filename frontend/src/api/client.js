import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export const submitQuiz = (data) => api.post('/quiz', data)
export const getProfile = () => api.get('/profile')
export const generateRecommendations = () => api.post('/recommendations/generate')
export const getWeekRecommendations = () => api.get('/recommendations/week')
export const submitFeedback = (data) => api.post('/feedback', data)
