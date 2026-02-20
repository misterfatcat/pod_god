export default function QuizStep({ title, subtitle, children, onNext, onBack, isFirst, isLast }) {
  return (
    <div className="quiz-step">
      <h1>{title}</h1>
      {subtitle && <p className="subtitle">{subtitle}</p>}
      <div className="quiz-content">{children}</div>
      <div className="quiz-nav">
        {!isFirst && <button onClick={onBack} className="btn-secondary">Back</button>}
        <button onClick={onNext} className="btn-primary">{isLast ? 'See My Recommendations' : 'Continue'}</button>
      </div>
    </div>
  )
}
