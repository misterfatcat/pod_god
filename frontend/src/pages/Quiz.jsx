import { useState } from 'react'
import QuizStep from '../components/QuizStep'
import { submitQuiz } from '../api/client'
import './Quiz.css'

const CATEGORIES = [
  'technology', 'science', 'true crime', 'business', 'history',
  'comedy', 'politics', 'health', 'sports', 'arts', 'education',
  'society', 'finance', 'environment', 'philosophy', 'food',
  'travel', 'design', 'parenting', 'spirituality'
]

const FORMATS = ['interview', 'narrative', 'solo', 'panel', 'news']
const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
const TIME_SLOTS = ['morning', 'afternoon', 'evening', 'night']

const AGE_RANGES = [
  'Under 25', '25–34', '35–44', '45–54', '55–64', '65 or older',
]

const US_STATES = [
  'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
  'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
  'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
  'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
  'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
  'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
  'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
  'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
  'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
  'Washington D.C.', 'West Virginia', 'Wisconsin', 'Wyoming',
]

const PRIMARY_GOALS = [
  { value: 'learn', label: 'Learn something new' },
  { value: 'entertain', label: 'Be entertained' },
  { value: 'stay_informed', label: 'Stay informed' },
  { value: 'relax', label: 'Relax and unwind' },
  { value: 'professional', label: 'Grow professionally' },
]

const SECONDARY_GOALS = ['learn', 'entertain', 'stay_informed', 'relax', 'professional']

export default function Quiz({ onComplete, initialProfile = null }) {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState({
    interest_categories: initialProfile?.interest_categories ?? [],
    goals: {
      primary: initialProfile?.goals?.primary ?? '',
      secondary: initialProfile?.goals?.secondary ?? [],
    },
    preferred_formats: initialProfile?.preferred_formats ?? [],
    preferred_length_bucket: initialProfile?.preferred_length_bucket ?? 'no_preference',
    complexity_level: initialProfile?.complexity_level ?? 'balanced',
    trending_vs_timeless: initialProfile?.trending_vs_timeless ?? 'mixed',
    mainstream_vs_niche: initialProfile?.mainstream_vs_niche ?? 'no_preference',
    preferred_listen_schedule: initialProfile?.preferred_listen_schedule ?? {},
    age_range: initialProfile?.age_range ?? null,
    location_region: initialProfile?.location_region ?? null,
  })

  const next = () => setStep(s => s + 1)
  const back = () => setStep(s => s - 1)

  const handleSubmit = async () => {
    await submitQuiz(answers)
    onComplete()
  }

  const toggleCategory = (category) => {
    const existing = answers.interest_categories.find(c => c.category === category)
    if (existing) {
      setAnswers(a => ({
        ...a,
        interest_categories: a.interest_categories.filter(c => c.category !== category)
      }))
    } else {
      setAnswers(a => ({
        ...a,
        interest_categories: [...a.interest_categories, { category, intensity: 3 }]
      }))
    }
  }

  const setIntensity = (category, intensity) => {
    setAnswers(a => ({
      ...a,
      interest_categories: a.interest_categories.map(c =>
        c.category === category ? { ...c, intensity } : c
      )
    }))
  }

  const toggleFormat = (format) => {
    setAnswers(a => ({
      ...a,
      preferred_formats: a.preferred_formats.includes(format)
        ? a.preferred_formats.filter(f => f !== format)
        : [...a.preferred_formats, format]
    }))
  }

  const toggleScheduleSlot = (day, slot) => {
    setAnswers(a => {
      const daySlots = a.preferred_listen_schedule[day] || []
      const updated = daySlots.includes(slot)
        ? daySlots.filter(s => s !== slot)
        : [...daySlots, slot]
      return {
        ...a,
        preferred_listen_schedule: { ...a.preferred_listen_schedule, [day]: updated }
      }
    })
  }

  const toggleSecondaryGoal = (goal) => {
    setAnswers(a => ({
      ...a,
      goals: {
        ...a.goals,
        secondary: a.goals.secondary.includes(goal)
          ? a.goals.secondary.filter(g => g !== goal)
          : [...a.goals.secondary, goal]
      }
    }))
  }

  const steps = [
    // Step 0: Topic interests
    <QuizStep
      key={0}
      title={initialProfile ? 'Editing your profile' : 'What topics interest you?'}
      subtitle={initialProfile ? 'Update your topics — changes apply immediately after you finish.' : 'Pick as many as you like, then rate how much each one matters to you.'}
      onNext={next}
      isFirst
    >
      <div className="chip-grid">
        {CATEGORIES.map(cat => {
          const selected = answers.interest_categories.find(c => c.category === cat)
          return (
            <button
              key={cat}
              className={`chip ${selected ? 'selected' : ''}`}
              onClick={() => toggleCategory(cat)}
            >
              {cat}
            </button>
          )
        })}
      </div>
      {answers.interest_categories.length > 0 && (
        <div>
          <p className="optional-label">How much do you care about each?</p>
          {answers.interest_categories.map(({ category, intensity }) => (
            <div key={category} className="intensity-row">
              <span>{category}</span>
              {[1, 2, 3, 4, 5].map(n => (
                <button
                  key={n}
                  className={`chip ${intensity === n ? 'selected' : ''}`}
                  onClick={() => setIntensity(category, n)}
                  style={{ minWidth: 36 }}
                >
                  {n}
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
    </QuizStep>,

    // Step 1: Listening goals
    <QuizStep
      key={1}
      title="Why do you listen to podcasts?"
      subtitle="Choose your main reason, then any secondary ones."
      onNext={next}
      onBack={back}
    >
      <p className="optional-label">Primary goal</p>
      <div className="option-list" style={{ marginBottom: '1.5rem' }}>
        {PRIMARY_GOALS.map(({ value, label }) => (
          <button
            key={value}
            className={`option-card ${answers.goals.primary === value ? 'selected' : ''}`}
            onClick={() => setAnswers(a => ({ ...a, goals: { ...a.goals, primary: value } }))}
          >
            {label}
          </button>
        ))}
      </div>
      <p className="optional-label">Secondary goals (optional)</p>
      <div className="chip-grid">
        {SECONDARY_GOALS.filter(g => g !== answers.goals.primary).map(goal => (
          <button
            key={goal}
            className={`chip ${answers.goals.secondary.includes(goal) ? 'selected' : ''}`}
            onClick={() => toggleSecondaryGoal(goal)}
          >
            {PRIMARY_GOALS.find(g => g.value === goal)?.label || goal}
          </button>
        ))}
      </div>
    </QuizStep>,

    // Step 2: Preferred formats
    <QuizStep
      key={2}
      title="What podcast formats do you enjoy?"
      subtitle="Select all that apply."
      onNext={next}
      onBack={back}
    >
      <div className="option-list">
        {FORMATS.map(format => (
          <button
            key={format}
            className={`option-card ${answers.preferred_formats.includes(format) ? 'selected' : ''}`}
            onClick={() => toggleFormat(format)}
          >
            {format.charAt(0).toUpperCase() + format.slice(1)}
          </button>
        ))}
      </div>
    </QuizStep>,

    // Step 3: Episode length
    <QuizStep
      key={3}
      title="How long should episodes be?"
      onNext={next}
      onBack={back}
    >
      <div className="option-list">
        {[
          { value: 'under_20', label: 'Under 20 minutes' },
          { value: '20_to_45', label: '20–45 minutes' },
          { value: 'over_45', label: 'Over 45 minutes' },
          { value: 'no_preference', label: 'No preference' },
        ].map(({ value, label }) => (
          <button
            key={value}
            className={`option-card ${answers.preferred_length_bucket === value ? 'selected' : ''}`}
            onClick={() => setAnswers(a => ({ ...a, preferred_length_bucket: value }))}
          >
            {label}
          </button>
        ))}
      </div>
    </QuizStep>,

    // Step 4: Complexity level
    <QuizStep
      key={4}
      title="How deep do you want to go?"
      onNext={next}
      onBack={back}
    >
      <div className="option-list">
        {[
          { value: 'beginner', label: 'Beginner friendly — accessible and easy to follow' },
          { value: 'balanced', label: 'Balanced — some depth, still accessible' },
          { value: 'deep_dive', label: 'Deep dive — expert-level, I want to be challenged' },
        ].map(({ value, label }) => (
          <button
            key={value}
            className={`option-card ${answers.complexity_level === value ? 'selected' : ''}`}
            onClick={() => setAnswers(a => ({ ...a, complexity_level: value }))}
          >
            {label}
          </button>
        ))}
      </div>
    </QuizStep>,

    // Step 5: Trending vs timeless
    <QuizStep
      key={5}
      title="Trending or timeless?"
      subtitle="Should your recommendations be current news, or evergreen content?"
      onNext={next}
      onBack={back}
    >
      <div className="option-list">
        {[
          { value: 'trending', label: 'Trending — what\'s happening right now' },
          { value: 'mixed', label: 'Mix of both' },
          { value: 'timeless', label: 'Timeless — classic topics that don\'t expire' },
        ].map(({ value, label }) => (
          <button
            key={value}
            className={`option-card ${answers.trending_vs_timeless === value ? 'selected' : ''}`}
            onClick={() => setAnswers(a => ({ ...a, trending_vs_timeless: value }))}
          >
            {label}
          </button>
        ))}
      </div>
    </QuizStep>,

    // Step 6: Mainstream vs niche
    <QuizStep
      key={6}
      title="Mainstream or niche?"
      subtitle="Do you want popular shows or hidden gems?"
      onNext={next}
      onBack={back}
    >
      <div className="option-list">
        {[
          { value: 'mainstream', label: 'Mainstream — well-known, widely recommended' },
          { value: 'no_preference', label: 'No preference' },
          { value: 'niche', label: 'Niche — lesser-known, more specific' },
        ].map(({ value, label }) => (
          <button
            key={value}
            className={`option-card ${answers.mainstream_vs_niche === value ? 'selected' : ''}`}
            onClick={() => setAnswers(a => ({ ...a, mainstream_vs_niche: value }))}
          >
            {label}
          </button>
        ))}
      </div>
    </QuizStep>,

    // Step 7: Listening schedule
    <QuizStep
      key={7}
      title="When do you usually listen?"
      subtitle="Tap any time slots that fit your routine."
      onNext={next}
      onBack={back}
    >
      <div className="schedule-grid">
        <div className="schedule-header" />
        {TIME_SLOTS.map(slot => (
          <div key={slot} className="schedule-header">{slot}</div>
        ))}
        {DAYS.map(day => (
          <>
            <div key={`${day}-label`} className="schedule-day-label">{day.slice(0, 3)}</div>
            {TIME_SLOTS.map(slot => {
              const active = (answers.preferred_listen_schedule[day] || []).includes(slot)
              return (
                <button
                  key={`${day}-${slot}`}
                  className={`schedule-cell ${active ? 'selected' : ''}`}
                  onClick={() => toggleScheduleSlot(day, slot)}
                >
                  {active ? '●' : '○'}
                </button>
              )
            })}
          </>
        ))}
      </div>
    </QuizStep>,

    // Step 8: Optional demographics
    <QuizStep
      key={8}
      title="Almost done!"
      subtitle="These are optional — they help us surface region-relevant content."
      onNext={handleSubmit}
      onBack={back}
      isLast
    >
      <label className="optional-label">Age range (optional)</label>
      <div className="chip-grid" style={{ marginBottom: '1.5rem' }}>
        {AGE_RANGES.map(age => (
          <button
            key={age}
            className={`chip ${answers.age_range === age ? 'selected' : ''}`}
            onClick={() => setAnswers(a => ({ ...a, age_range: a.age_range === age ? null : age }))}
          >
            {age}
          </button>
        ))}
      </div>
      <label className="optional-label">State (optional)</label>
      <select
        className="text-input"
        value={answers.location_region || ''}
        onChange={e => setAnswers(a => ({ ...a, location_region: e.target.value || null }))}
      >
        <option value="">Select a state…</option>
        {US_STATES.map(state => (
          <option key={state} value={state}>{state}</option>
        ))}
      </select>
    </QuizStep>,
  ]

  return steps[step]
}
