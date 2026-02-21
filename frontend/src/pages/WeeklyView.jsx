import { useEffect, useState } from 'react'
import EpisodeCard from '../components/EpisodeCard'
import EpisodeDetailModal from '../components/EpisodeDetailModal'
import { generateRecommendations, getWeekRecommendations } from '../api/client'
import './WeeklyView.css'

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

const TODAY_NAME = new Date().toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()

function formatWeekRange(weekOfIso) {
  const [year, month, day] = weekOfIso.split('-').map(Number)
  const monday = new Date(year, month - 1, day)
  const sunday = new Date(year, month - 1, day + 6)
  const fmt = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  return `Week of ${fmt(monday)} – ${fmt(sunday)}, ${year}`
}

function getDayLabel(dayName, weekOfIso) {
  if (!weekOfIso) return dayName.charAt(0).toUpperCase() + dayName.slice(1)
  const [year, month, day] = weekOfIso.split('-').map(Number)
  const dayIndex = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].indexOf(dayName)
  const date = new Date(year, month - 1, day + dayIndex)
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  return `${dayName.charAt(0).toUpperCase() + dayName.slice(1)} · ${dateStr}`
}

export default function WeeklyView({ onFeedback, onRedoQuiz, onLogout }) {
  const [recs, setRecs] = useState(null)
  const [weekOf, setWeekOf] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [detailEpisode, setDetailEpisode] = useState(null)

  useEffect(() => {
    getWeekRecommendations()
      .then(res => { setRecs(res.data.recommendations); setWeekOf(res.data.week_of) })
      .catch(() => {
        setLoading(true)
        generateRecommendations()
          .then(() => getWeekRecommendations())
          .then(res => { setRecs(res.data.recommendations); setWeekOf(res.data.week_of) })
          .catch(err => setError(err.message || 'Failed to generate recommendations'))
          .finally(() => setLoading(false))
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="weekly-loading">
        <p>Generating your week...</p>
        <p className="loading-sub">This may take a minute while the AI picks your episodes.</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="weekly-loading">
        <p>Something went wrong: {error}</p>
        <p className="loading-sub">Make sure Ollama is running and you have API credentials in .env</p>
      </div>
    )
  }

  return (
    <div className="weekly-view">
      <header className="weekly-header">
        <div>
          <h1>Your Week</h1>
          <p className="weekly-sub">{weekOf ? formatWeekRange(weekOf) : '3 episodes per day, picked for you'}</p>
        </div>
        <div className="weekly-header-actions">
          <button onClick={onRedoQuiz} className="btn-secondary">Redo Quiz</button>
          <button onClick={onLogout} className="btn-secondary">Sign Out</button>
        </div>
      </header>
      <div className="days-grid-wrapper">
      <div className="days-grid">
        {DAYS.map(day => (
          <div key={day} className={`day-column${day === TODAY_NAME ? ' day-column--today' : ''}`}>
            <div className="day-label-row">
              <h2 className="day-label">{getDayLabel(day, weekOf)}</h2>
              {day === TODAY_NAME && <span className="today-badge">Today</span>}
            </div>
            {(recs?.[day] || []).length === 0 ? (
              <p className="no-eps">No episodes</p>
            ) : (
              (recs?.[day] || []).map(ep => (
                <EpisodeCard
                  key={ep.id}
                  episode={ep}
                  onFeedback={onFeedback}
                  onOpenDetail={setDetailEpisode}
                />
              ))
            )}
          </div>
        ))}
      </div>
      </div>
      {detailEpisode && (
        <EpisodeDetailModal
          episode={detailEpisode}
          onFeedback={onFeedback}
          onClose={() => setDetailEpisode(null)}
        />
      )}
    </div>
  )
}
