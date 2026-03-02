import { useState } from 'react'
import { login, register, getProfile } from '../api/client'
import './Auth.css'

export default function Auth({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const fn = mode === 'login' ? login : register
      const { data } = await fn(email, password)
      localStorage.setItem('token', data.access_token)
      const profileRes = await getProfile().catch(() => null)
      onAuthenticated(profileRes ? 'weekly' : 'quiz', profileRes?.data ?? null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <h1>Pod God</h1>
      <p className="auth-subtitle">
        {mode === 'login' ? 'Welcome back' : 'Create your account'}
      </p>
      <form onSubmit={handleSubmit} className="auth-form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        {error && <p className="auth-error">{error}</p>}
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
        </button>
      </form>
      <button
        className="auth-toggle"
        onClick={() => { setMode(m => m === 'login' ? 'register' : 'login'); setError('') }}
      >
        {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
      </button>
    </div>
  )
}
