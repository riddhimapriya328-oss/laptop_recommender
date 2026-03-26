import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Attach stored JWT to every request
const api = axios.create({ baseURL: BASE })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Auth ────────────────────────────────────────────────────
export async function loginUser(email, password) {
  const { data } = await api.post('/api/auth/login', { email, password })
  return data
}

export async function signupUser(email, password, fullName) {
  const { data } = await api.post('/api/auth/signup', {
    email,
    password,
    full_name: fullName,
  })
  return data
}

// ── Recommendation Flow ─────────────────────────────────────
export async function analyzeQuery(query) {
  const { data } = await api.post('/api/analyze-query', { query })
  return data // { budget_inr, use_case, priorities, brand_pref }
}

export async function getRecommendations(intent, limit = 3) {
  const { data } = await api.post('/api/recommend', { ...intent, limit })
  return data // { recommendations: [...] }
}

export async function getExplanations(laptops, userQuery, intent) {
  const { data } = await api.post('/api/explain', {
    laptops,
    user_query: userQuery,
    intent,
  })
  return data // { explanations: {id: text}, why_not: "..." }
}

// ── Laptops ─────────────────────────────────────────────────
export async function fetchLaptops(limit = 20, offset = 0) {
  const { data } = await api.get('/api/laptops', {
    params: { limit, offset },
  })
  return data
}

export async function fetchLaptopById(id) {
  const { data } = await api.get(`/api/laptops/${id}`)
  return data
}

// ── History ─────────────────────────────────────────────────
export async function saveHistory(queryText, intent, recommendations) {
  const { data } = await api.post('/api/history', {
    query_text: queryText,
    intent,
    recommendations,
  })
  return data
}

export async function fetchHistory() {
  const { data } = await api.get('/api/history')
  return data // { history: [...] }
}

// ── Compare ─────────────────────────────────────────────────
export async function saveToCompare(laptopId) {
  const { data } = await api.post('/api/compare/save', { laptop_id: laptopId })
  return data
}

export async function fetchCompare() {
  const { data } = await api.get('/api/compare')
  return data
}
