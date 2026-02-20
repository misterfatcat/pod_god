import { useState } from 'react'
import { submitFeedback } from '../api/client'
import './FeedbackModal.css'

const REASON_FLAGS = [
  { key: 'great_storytelling', label: 'Great storytelling' },
  { key: 'fascinating_topic', label: 'Fascinating topic' },
  { key: 'loved_guest', label: 'Loved the guest' },
  { key: 'great_production', label: 'Great production' },
  { key: 'too_long', label: 'Too long' },
  { key: 'too_short', label: 'Too short' },
  { key: 'poor_audio', label: 'Poor audio' },
  { key: 'too_basic', label: 'Too basic' },
  { key: 'too_advanced', label: 'Too advanced' },
  { key: 'repetitive', label: 'Repetitive' },
]

const CONTEXTS = ['commute', 'workout', 'cooking', 'relaxing', 'other']

export default function FeedbackModal({ episode, reaction, onClose }) {
  const [flags, setFlags] = useState({})
  const [context, setContext] = useState('')
  const [reasonText, setReasonText] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const toggle = (key) => setFlags(f => ({ ...f, [key]: !f[key] }))

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      await submitFeedback({
        episode_id: episode.episode_id,
        reaction,
        listen_context: context || null,
        reason_text: reasonText || null,
        ...Object.fromEntries(REASON_FLAGS.map(r => [r.key, flags[r.key] || false])),
      })
    } finally {
      setSubmitting(false)
      onClose()
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className={`reaction-badge ${reaction}`}>
            {reaction === 'like' ? '♥ Liked' : '✕ Disliked'}
          </span>
          <h2>{episode.title}</h2>
        </div>

        <p className="modal-label">What stood out? (optional)</p>
        <div className="reason-grid">
          {REASON_FLAGS.map(r => (
            <button
              key={r.key}
              className={`reason-chip ${flags[r.key] ? 'selected' : ''}`}
              onClick={() => toggle(r.key)}
            >
              {r.label}
            </button>
          ))}
        </div>

        <p className="modal-label">When did you listen?</p>
        <div className="context-row">
          {CONTEXTS.map(c => (
            <button
              key={c}
              className={`reason-chip ${context === c ? 'selected' : ''}`}
              onClick={() => setContext(prev => prev === c ? '' : c)}
            >
              {c}
            </button>
          ))}
        </div>

        <textarea
          className="feedback-textarea"
          placeholder="Anything else? (optional)"
          value={reasonText}
          onChange={e => setReasonText(e.target.value)}
          rows={3}
        />

        <div className="modal-actions">
          <button onClick={handleSubmit} className="btn-primary" disabled={submitting}>
            {submitting ? 'Saving...' : 'Save feedback'}
          </button>
          <button onClick={onClose} className="btn-secondary">Skip</button>
        </div>
      </div>
    </div>
  )
}
