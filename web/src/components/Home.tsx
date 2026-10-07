import { useState } from 'react'
import { topics } from '../content/load'
import { hrefTopic } from '../route'
import { setName, topicStats } from '../store/progress'
import { useProgress } from '../store/useProgress'
import { Rich } from './Tex'

const STATUS: Record<string, string> = {
  new: 'Новая',
  learning: 'В процессе',
  checked: 'Проверка пройдена',
  trained: 'Освоено',
}

function Welcome() {
  const { update } = useProgress()
  const [name, setN] = useState('')
  return (
    <section className="welcome card">
      <h1>Матеша 👋</h1>
      <p>
        Алгебра 8 класса по шагам: понятное объяснение, проверка, тренировка. Как тебя зовут?
      </p>
      <form
        className="input-row"
        onSubmit={(e) => {
          e.preventDefault()
          update((s) => setName(s, name.trim() || 'Ученик'))
        }}
      >
        <input value={name} onChange={(e) => setN(e.target.value)} placeholder="Имя" aria-label="Имя" autoFocus />
        <button className="btn primary" type="submit">Поехали</button>
      </form>
    </section>
  )
}

export function Home() {
  const { state, update } = useProgress()
  if (!state.name) {
    return (
      <main className="page">
        <Welcome />
      </main>
    )
  }
  return (
    <main className="page">
      <header className="home-head">
        <div>
          <p className="eyebrow">Алгебра · 8 класс</p>
          <h1>Привет, {state.name}!</h1>
        </div>
        <div className="stats">
          <div className="stat" title="Очки опыта">
            <strong>⭐ {state.xp}</strong>
            <span>очков</span>
          </div>
          <div className="stat" title="Дней подряд">
            <strong>🔥 {state.streak}</strong>
            <span>{pluralDays(state.streak)}</span>
          </div>
        </div>
      </header>
      <ul className="topic-list">
        {topics.map((t) => {
          const p = state.topics[t.id]
          const st = topicStats(t, p)
          const cta = st.status === 'new' ? 'Начать' : 'Продолжить'
          const tab = !p?.explainDone ? 'learn' : !p.checkPassed ? 'check' : 'train'
          return (
            <li key={t.id} className="card topic-card">
              <a href={hrefTopic(t.id, tab, tab === 'learn' ? p?.stepReached : undefined)}>
                <div className="topic-top">
                  <span className="topic-num">{t.order}</span>
                  <div>
                    <h2>{t.title}</h2>
                    <p className="muted">
                      <Rich text={t.summary} />
                    </p>
                  </div>
                </div>
                <div className="progress-bar">
                  <div style={{ width: `${st.percent}%` }} />
                </div>
                <div className="topic-bottom">
                  <span className={`status ${st.status}`}>{STATUS[st.status]}</span>
                  <span className="muted">{st.percent}%</span>
                  <span className="cta">{cta} ▸</span>
                </div>
              </a>
            </li>
          )
        })}
      </ul>
      <p className="foot muted">
        Прогресс хранится в этом браузере.{' '}
        <button
          className="link-btn"
          onClick={() => {
            if (window.confirm('Сбросить имя и весь прогресс на этом устройстве?')) {
              localStorage.removeItem('matesha.v1')
              update(() => ({ v: 1, name: '', xp: 0, streak: 0, lastDay: null, topics: {} }))
            }
          }}
        >
          Сбросить
        </button>
      </p>
    </main>
  )
}

function pluralDays(n: number): string {
  const m10 = n % 10
  const m100 = n % 100
  if (m10 === 1 && m100 !== 11) return 'день подряд'
  if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return 'дня подряд'
  return 'дней подряд'
}
