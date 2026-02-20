export default function EpisodeCard({ episode, onFeedback }) {
  const mins = Math.round((episode.duration_sec || 0) / 60)

  return (
    <div className="episode-card">
      {episode.artwork_url && (
        <img src={episode.artwork_url} alt={episode.title} className="artwork" />
      )}
      <div className="episode-info">
        <h3>{episode.title}</h3>
        <p className="reason">{episode.reason}</p>
        <span className="duration">{mins > 0 ? `${mins} min` : ''}</span>
      </div>
      <div className="episode-actions">
        <button
          onClick={() => onFeedback(episode, 'like')}
          className="btn-like"
          title="Like"
        >
          ♥
        </button>
        <button
          onClick={() => onFeedback(episode, 'dislike')}
          className="btn-dislike"
          title="Dislike"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
