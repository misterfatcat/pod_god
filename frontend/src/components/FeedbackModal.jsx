import { useState } from 'react'
import { submitFeedback } from '../api/client'
import './FeedbackModal.css'

const REACTION_LABELS = {
  like: '♥ Liked',
  dislike: '✕ Disliked',
  not_interested: '⊘ Not Interested',
}

// All 10 flag keys — used in handleSubmit to ensure every DB column is always written
const ALL_FLAGS = [
  'great_storytelling', 'fascinating_topic', 'loved_guest', 'great_production',
  'too_long', 'too_short', 'poor_audio', 'too_basic', 'too_advanced', 'repetitive',
]

// Subset shown in the UI, differentiated by reaction type
const FLAGS_BY_REACTION = {
  like: [
    { key: 'great_storytelling', label: 'Great storytelling' },
    { key: 'fascinating_topic',  label: 'Fascinating topic' },
    { key: 'loved_guest',        label: 'Loved the guest' },
    { key: 'great_production',   label: 'Great production' },
  ],
  dislike: [
    { key: 'too_long',     label: 'Too long' },
    { key: 'too_short',    label: 'Too short' },
    { key: 'poor_audio',   label: 'Poor audio' },
    { key: 'too_basic',    label: 'Too basic' },
    { key: 'too_advanced', label: 'Too advanced' },
    { key: 'repetitive',   label: 'Repetitive' },
  ],
  not_interested: [
    { key: 'too_basic',    label: 'Too basic' },
    { key: 'too_advanced', label: 'Too advanced' },
    { key: 'too_long',     label: 'Too long' },
    { key: 'repetitive',   label: 'Repetitive' },
  ],
}

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
        ...Object.fromEntries(ALL_FLAGS.map(key => [key, flags[key] || false])),
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
            {REACTION_LABELS[reaction] || reaction}
          </span>
          <h2>{episode.title}</h2>
        </div>

        <p className="modal-label">{reaction === 'not_interested' ? 'What put you off? (optional)' : 'What stood out? (optional)'}</p>
        <div className="reason-grid">
          {(FLAGS_BY_REACTION[reaction] || []).map(r => (
            <button
              key={r.key}
              className={`reason-chip ${flags[r.key] ? 'selected' : ''}`}
              onClick={() => toggle(r.key)}
            >
              {r.label}
            </button>
          ))}
        </div>

        {reaction !== 'not_interested' && (
          <>
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
          </>
        )}

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
