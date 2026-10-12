import { useState } from 'react'
import { topics } from '../content/load'
import { hrefTopic } from '../route'
import { skillInfo } from '../content/skills'
import { planProgress } from '../lib/plan'
import { emptyState, setName, topicStats, weakSkills } from '../store/progress'
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
      <PlanCard />
      <ExamCard />
      <WeakSpots />
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
              update(() => emptyState())
            }
          }}
        >
          Сбросить
        </button>
      </p>
    </main>
  )
}

function PlanCard() {
  const { state } = useProgress()
  const rows = planProgress(topics, state)
  const classExams = state.exams.filter((e) => !e.kind || e.kind === 'class')
  const best = classExams.reduce<(typeof classExams)[number] | null>((m, e) => (!m || e.score / e.total > m.score / m.total ? e : m), null)
  return (
    <section className="card plan" aria-label="План подготовки к контрольной">
      <h2>🎯 Подготовка к контрольной</h2>
      <p className="muted">В контрольной три задания: сравнить числа, упростить выражения, решить квадратные уравнения. Иди по порядку: урок, потом минимум по пять задач каждого типа.</p>
      <ol className="plan-list">
        {rows.map((r, i) => {
          const percent = r.total ? Math.round((r.done / r.total) * 100) : 0
          const icon = r.next.kind === 'lesson' ? '📖' : r.next.kind === 'train' ? '✏️' : '✓'
          return (
            <li key={r.item.id}>
              <div className="plan-head">
                <span className="plan-num">{i + 1}</span>
                <strong>{r.item.title}</strong>
                <span className="muted">
                  {r.done} / {r.total}
                </span>
              </div>
              <div className="progress-bar" aria-hidden>
                <div style={{ width: `${percent}%` }} />
              </div>
              <div className="plan-actions">
                <a className={`btn small ${r.next.kind === 'done' ? '' : 'primary'}`} href={r.next.href}>
                  {icon} {r.next.label}
                </a>
                {r.next.kind !== 'lesson' && (
                  <a className="link" href={r.lessonHref}>
                    урок
                  </a>
                )}
              </div>
            </li>
          )
        })}
        <li>
          <div className="plan-head">
            <span className="plan-num">4</span>
            <strong>Пробная контрольная</strong>
            <span className="muted">{best ? `лучший результат ${best.score} из ${best.total}` : 'ещё не писали'}</span>
          </div>
          <div className="plan-actions">
            <a className="btn small" href="#/exam">
              📝 Написать
            </a>
          </div>
        </li>
      </ol>
    </section>
  )
}

function ExamCard() {
  const { state } = useProgress()
  const last = state.exams[state.exams.length - 1]
  return (
    <a className="card exam-card" href="#/exam">
      <div>
        <h2>📝 Контрольная</h2>
        <p className="muted">
          Классная работа или КР № 3, 4, 5 как в книге. Каждый раз новый вариант.
          {last && (
            <>
              {' '}
              Последний результат: <strong>{last.score} из {last.total}</strong>.
            </>
          )}
        </p>
      </div>
      <span className="cta">Начать ▸</span>
    </a>
  )
}

function WeakSpots() {
  const { state } = useProgress()
  const weak = weakSkills(state).filter((w) => skillInfo(w.id))
  if (weak.length === 0) return null
  return (
    <section className="card weak" aria-label="Что стоит повторить">
      <h2>🎯 Что стоит повторить</h2>
      <p className="muted">Здесь пока больше ошибок, чем успехов. Короткий урок поможет.</p>
      <ul className="weak-list">
        {weak.map((w) => {
          const info = skillInfo(w.id)!
          return (
            <li key={w.id}>
              <a href={hrefTopic(info.topic, 'learn', info.step)}>{info.title}</a>{' '}
              <span className="muted">
                (верно {w.ok}, ошибок {w.bad})
              </span>
            </li>
          )
        })}
      </ul>
    </section>
  )
}

function pluralDays(n: number): string {
  const m10 = n % 10
  const m100 = n % 100
  if (m10 === 1 && m100 !== 11) return 'день подряд'
  if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return 'дня подряд'
  return 'дней подряд'
}
