import { useEffect, useState } from 'react'
import EpisodeCard from '../components/EpisodeCard'
import { generateRecommendations, getWeekRecommendations } from '../api/client'
import './WeeklyView.css'

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

export default function WeeklyView({ onFeedback }) {
  const [recs, setRecs] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getWeekRecommendations()
      .then(res => setRecs(res.data.recommendations))
      .catch(() => {
        setLoading(true)
        generateRecommendations()
          .then(() => getWeekRecommendations())
          .then(res => setRecs(res.data.recommendations))
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
        <h1>Your Week</h1>
        <p className="weekly-sub">3 episodes per day, picked for you</p>
      </header>
      <div className="days-grid">
        {DAYS.map(day => (
          <div key={day} className="day-column">
            <h2 className="day-label">{day.charAt(0).toUpperCase() + day.slice(1)}</h2>
            {(recs?.[day] || []).length === 0 ? (
              <p className="no-eps">No episodes</p>
            ) : (
              (recs?.[day] || []).map(ep => (
                <EpisodeCard key={ep.id} episode={ep} onFeedback={onFeedback} />
              ))
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
