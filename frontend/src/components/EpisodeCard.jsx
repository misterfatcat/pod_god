export default function EpisodeCard({ episode, onFeedback, onOpenDetail }) {
  const mins = Math.round((episode.duration_sec || 0) / 60)
  const categories = Array.isArray(episode.categories)
    ? episode.categories
    : (typeof episode.categories === 'string' ? JSON.parse(episode.categories || '[]') : [])

  return (
    <div className="episode-card">
      <div className="episode-card-body" onClick={() => onOpenDetail(episode)}>
        {episode.artwork_url ? (
          <img src={episode.artwork_url} alt={episode.title} className="artwork" />
        ) : (
          <div className="artwork artwork-placeholder" />
        )}
        <div className="episode-info">
          <h3>{episode.title}</h3>
          {categories.length > 0 && (
            <div className="episode-categories">
              {categories.slice(0, 3).map(cat => (
                <span key={cat} className="category-chip">{cat}</span>
              ))}
            </div>
          )}
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
