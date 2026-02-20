import { useState } from 'react'
import Quiz from './pages/Quiz'
import WeeklyView from './pages/WeeklyView'
import FeedbackModal from './components/FeedbackModal'
import './App.css'

export default function App() {
  const [view, setView] = useState('quiz')
  const [feedbackEpisode, setFeedbackEpisode] = useState(null)

  return (
    <div className="app-root">
      {view === 'quiz' && (
        <Quiz onComplete={() => setView('weekly')} />
      )}
      {view === 'weekly' && (
        <WeeklyView
          onFeedback={(ep, reaction) => setFeedbackEpisode({ ep, reaction })}
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
