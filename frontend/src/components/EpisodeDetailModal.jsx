import './EpisodeDetailModal.css'

export default function EpisodeDetailModal({ episode, onFeedback, onClose }) {
  const mins = Math.round((episode.duration_sec || 0) / 60)

  const publishedDate = episode.published_at
    ? new Date(episode.published_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    : null

  const handleFeedback = (reaction) => {
    onFeedback(episode, reaction)
    onClose()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>

        <div className="edm-artwork-row">
          {episode.artwork_url && (
            <img src={episode.artwork_url} alt={episode.title} className="edm-artwork" />
          )}
          <div className="edm-meta">
            <h2 className="edm-title">{episode.title}</h2>
            {episode.host_name && <span className="edm-host">{episode.host_name}</span>}
            {publishedDate && <span className="edm-date">{publishedDate}</span>}
            {mins > 0 && <span className="edm-duration">{mins} min</span>}
          </div>
        </div>

        {episode.reason && (
          <div>
            <p className="edm-section-label">Why this episode</p>
            <p className="edm-reason">{episode.reason}</p>
          </div>
        )}

        {episode.description && (
          <div>
            <p className="edm-section-label">About this episode</p>
            <p className="edm-description">{episode.description}</p>
          </div>
        )}

        <div className="edm-bottom-row">
          {episode.audio_url && (
            <a
              href={episode.audio_url}
              target="_blank"
              rel="noopener noreferrer"
              className="edm-listen-btn"
            >
              Listen →
            </a>
          )}
          <div className="edm-feedback-row">
            <button onClick={() => handleFeedback('like')} className="btn-like" title="Like">♥</button>
            <button onClick={() => handleFeedback('dislike')} className="btn-dislike" title="Dislike">✕</button>
            <button onClick={() => handleFeedback('not_interested')} className="btn-not-interested" title="Not interested">⊘</button>
          </div>
        </div>

        <div className="modal-actions">
          <button onClick={onClose} className="btn-secondary">Close</button>
        </div>
      </div>
    </div>
  )
}
