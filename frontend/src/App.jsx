import { useState, useEffect } from 'react'
import Auth from './pages/Auth'
import Quiz from './pages/Quiz'
import WeeklyView from './pages/WeeklyView'
import FeedbackModal from './components/FeedbackModal'
import { getProfile } from './api/client'
import './App.css'

export default function App() {
  const [view, setView] = useState('loading')
  const [feedbackEpisode, setFeedbackEpisode] = useState(null)
  const [existingProfile, setExistingProfile] = useState(null)
  const [shouldRegenerateRecs, setShouldRegenerateRecs] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) { setView('auth'); return }
    getProfile()
      .then((res) => { setExistingProfile(res.data); setView('weekly') })
      .catch((err) => {
        if (err.response?.status === 401) {
          localStorage.removeItem('token')
          setView('auth')
        } else {
          setView('quiz')
        }
      })
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    setView('auth')
  }

  if (view === 'loading') return null

  return (
    <div className="app-root">
      {view === 'auth' && (
        <Auth onAuthenticated={(v, profile) => {
          if (profile) setExistingProfile(profile)
          setView(v)
        }} />
      )}
      {view === 'quiz' && (
        <Quiz
          initialProfile={existingProfile}
          onComplete={() => {
            setShouldRegenerateRecs(true)
            setView('weekly')
          }}
        />
      )}
      {view === 'weekly' && (
        <WeeklyView
          onFeedback={(ep, reaction) => setFeedbackEpisode({ ep, reaction })}
          onRedoQuiz={() => setView('quiz')}
          onLogout={handleLogout}
          shouldRegenerate={shouldRegenerateRecs}
          onRegenerated={() => setShouldRegenerateRecs(false)}
        />
      )}
      {feedbackEpisode && (
        <FeedbackModal
          episode={feedbackEpisode.ep}
          reaction={feedbackEpisode.reaction}
          onClose={() => setFeedbackEpisode(null)}
        />
      )}
    </div>
  )
}
