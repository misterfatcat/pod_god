export default function EpisodeCard({ episode, onFeedback, onOpenDetail }) {
  const mins = Math.round((episode.duration_sec || 0) / 60)

  return (
    <div className="episode-card">
      <div className="episode-card-body" onClick={() => onOpenDetail(episode)}>
        {episode.artwork_url && (
          <img src={episode.artwork_url} alt={episode.title} className="artwork" />
        )}
        <div className="episode-info">
          <h3>{episode.title}</h3>
          <p className="reason">{episode.reason}</p>
          <span className="duration">{mins > 0 ? `${mins} min` : ''}</span>
        </div>
      </div>
      <div className="episode-actions">
        <button
          onClick={(e) => { e.stopPropagation(); onFeedback(episode, 'like') }}
          className="btn-like"
          title="Like"
        >
          ♥
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onFeedback(episode, 'dislike') }}
          className="btn-dislike"
          title="Dislike"
        >
          ✕
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onFeedback(episode, 'not_interested') }}
          className="btn-not-interested"
          title="Not interested"
        >
          ⊘
        </button>
      </div>
    </div>
  )
}
