import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { topics } from '../content/load'
import { checkAnswer, type CheckResult } from '../lib/check'
import { buildExam, formatOf, FORMATS, gradeLabel, type Difficulty, type ExamItem, type ExamKind, type ExamVariant } from '../lib/exam'
import { hrefTopic } from '../route'
import { recordExam, type ExamResult } from '../store/progress'
import { useProgress } from '../store/useProgress'
import { AnswerInput, varsOf } from './AnswerInput'
import { Rich } from './Tex'
import { answerText, taskPrompt } from './Trainer'

const KEY = 'matesha.exam'

type Saved = {
  phase: 'run' | 'result'
  seed: number
  difficulty: Difficulty
  kind: ExamKind
  timer: boolean
  startedAt: number
  finishedAt?: number
  idx: number
  answers: Record<string, string>
}

function load(): Saved | null {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return null
    const s = JSON.parse(raw) as Saved
    return { ...s, kind: FORMATS.some((f) => f.id === s.kind) ? s.kind : 'class' }
  } catch {
    return null
  }
}
function save(s: Saved | null): void {
  try {
    if (s) localStorage.setItem(KEY, JSON.stringify(s))
    else localStorage.removeItem(KEY)
  } catch {
    /* без сохранения контрольная всё равно работает */
  }
}

function grade(item: ExamItem, answer: string): CheckResult {
  const t = item.task
  try {
    return checkAnswer(answer, t.answer, t.answerKind, { reduce: t.reduce, radical: t.radical, items: t.items })
  } catch {
    return { status: 'invalid', message: 'Не удалось проверить запись.' }
  }
}

const mmss = (sec: number) => `${String(Math.floor(Math.max(0, sec) / 60)).padStart(2, '0')}:${String(Math.max(0, sec) % 60).padStart(2, '0')}`

function ItemView({ item, value, onChange, onNext }: { item: ExamItem; value: string; onChange: (v: string) => void; onNext: () => void }) {
  const t = item.task
  const vars = useMemo(() => varsOf(t.expr, t.answer), [t])
  const sqrtKey = [t.expr, t.expr2, t.answer, t.prompt].some((x) => x?.includes('sqrt') || x?.includes('√'))
  return (
    <div className="task">
      <div className="task-head">
        <span className="badge">{item.label})</span>
      </div>
      <p className="q-prompt">
        <Rich text={taskPrompt(t)} />
      </p>
      <AnswerInput
        key={item.id}
        value={value}
        onChange={onChange}
        onSubmit={onNext}
        kind={t.answerKind}
        vars={vars}
        sqrtKey={sqrtKey}
        options={t.options}
        items={t.items}
        placeholder={/^-?\d+([./]\d+)?$/.test(t.answer) && t.answerKind === 'expr' ? 'ответ числом, например 7 или 3/4' : undefined}
        hideSubmit
      />
    </div>
  )
}

function Result({ exam, saved, onAgain }: { exam: ExamVariant; saved: Saved; onAgain: () => void }) {
  const items = exam.sections.flatMap((s) => s.items)
  const graded = items.map((it) => ({ it, res: grade(it, saved.answers[it.id] ?? '') }))
  const score = graded.filter((g) => g.res.status === 'correct').length
  const seconds = Math.round(((saved.finishedAt ?? Date.now()) - saved.startedAt) / 1000)
  const weakGroups = [...new Map(graded.filter((g) => g.res.status !== 'correct').map((g) => [g.it.groupId, g.it])).values()]
  return (
    <section className="check-result exam-result">
      <h2>Результат контрольной</h2>
      <p className="big-score">
        {score} из {items.length}
      </p>
      <p>{gradeLabel(score, items.length)}</p>
      <p className="muted">
        {formatOf(exam.kind).title} · вариант № {exam.seed} · время {mmss(seconds)}
      </p>
      <ol className="exam-review">
        {graded.map(({ it, res }) => {
          const ok = res.status === 'correct'
          const ans = saved.answers[it.id]
          return (
            <li key={it.id} className={`review ${ok ? 'ok' : 'bad'}`}>
              <div className="review-head">
                <span className={`mark ${ok ? 'ok' : 'bad'}`}>{ok ? '✓' : '✗'}</span>
                <strong>{it.label})</strong>
                <span className="muted">{it.groupTitle}</span>
              </div>
              <p className="q-prompt">
                <Rich text={taskPrompt(it.task)} />
              </p>
              <p>
                Твой ответ: <strong>{ans ? <AnswerShown item={it} answer={ans} /> : 'нет ответа'}</strong>
              </p>
              {!ok && (
                <>
                  {res.status !== 'empty' && res.status !== 'wrong' && <p className="soft-msg">{res.message}</p>}
                  <p>
                    Правильный ответ: <Rich text={answerText(it.task)} />
                  </p>
                  <details>
                    <summary>Показать решение</summary>
                    <ol className="example">
                      {it.task.solution.map((s, i) => (
                        <li key={i}>
                          <Rich text={s} />
                        </li>
                      ))}
                    </ol>
                  </details>
                  <a className="link" href={hrefTopic(it.topicId, 'learn', it.lessonStep)}>
                    ↩ Повторить урок по этой теме
                  </a>
                </>
              )}
            </li>
          )
        })}
      </ol>
      {weakGroups.length > 0 && (
        <div className="card">
          <h3>Что потренировать</h3>
          <ul className="weak-list">
            {weakGroups.map((g) => (
              <li key={g.groupId}>
                <a href={hrefTopic(g.topicId, 'train')}>{g.groupTitle}</a>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="nav-row">
        <a className="btn ghost" href="#/">
          На главную
        </a>
        <button className="btn primary" onClick={onAgain}>
          Новый вариант ▸
        </button>
      </div>
    </section>
  )
}

function AnswerShown({ item, answer }: { item: ExamItem; answer: string }) {
  const t = item.task
  if (t.answerKind === 'compare') return <>«{answer}»</>
  if (t.answerKind === 'choice') return <Rich text={t.options?.[Number(answer)] ?? answer} />
  if (t.answerKind === 'order') {
    return (
      <Rich
        text={answer
          .split(',')
          .map((i) => '$' + (t.items?.[Number(i)] ? t.items[Number(i)].replace(/sqrt\(([^)]*)\)/g, '\\sqrt{$1}') : i) + '$')
          .join(' < ')}
      />
    )
  }
  return <>{answer}</>
}

export function Exam() {
  const { update } = useProgress()
  const [saved, setSaved] = useState<Saved | null>(() => load())
  const [difficulty, setDifficulty] = useState<Difficulty>('basic')
  const [kind, setKind] = useState<ExamKind>('class')
  const [timer, setTimer] = useState(true)
  const [now, setNow] = useState(() => Date.now())
  const recorded = useRef(false)

  const exam = useMemo(() => (saved ? buildExam(topics, saved.seed, saved.difficulty, saved.kind) : null), [saved?.seed, saved?.difficulty, saved?.kind]) // eslint-disable-line react-hooks/exhaustive-deps
  const items = useMemo(() => exam?.sections.flatMap((s) => s.items) ?? [], [exam])

  const persist = useCallback((next: Saved | null) => {
    setSaved(next)
    save(next)
  }, [])

  const finish = useCallback(
    (cur: Saved) => {
      if (!exam) return
      const done: Saved = { ...cur, phase: 'result', finishedAt: Date.now() }
      const all = exam.sections.flatMap((s) => s.items)
      const graded = all.map((it) => ({ it, res: grade(it, done.answers[it.id] ?? '') }))
      const result: ExamResult = {
        at: new Date().toISOString(),
        seed: cur.seed,
        difficulty: cur.difficulty,
        kind: cur.kind,
        score: graded.filter((g) => g.res.status === 'correct').length,
        total: all.length,
        wrong: graded.filter((g) => g.res.status !== 'correct').map((g) => g.it.id),
        seconds: Math.round((done.finishedAt! - cur.startedAt) / 1000),
      }
      if (!recorded.current) {
        recorded.current = true
        update((s) => recordExam(s, result, graded.map((g) => ({ skills: g.it.task.skills ?? [], correct: g.res.status === 'correct' }))))
      }
      persist(done)
      window.scrollTo({ top: 0 })
    },
    [exam, persist, update],
  )

  const running = saved?.phase === 'run'
  useEffect(() => {
    if (!running) return
    const id = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(id)
  }, [running])

  const minutes = formatOf(saved?.kind ?? kind).minutes
  const left = saved?.timer ? minutes * 60 - Math.floor((now - saved.startedAt) / 1000) : null
  useEffect(() => {
    if (saved && running && left !== null && left <= 0) finish(saved)
  }, [left, running, saved, finish])

  const start = () => {
    recorded.current = false
    persist({ phase: 'run', seed: 1000 + Math.floor(Math.random() * 9000), difficulty, kind, timer, startedAt: Date.now(), idx: 0, answers: {} })
    setNow(Date.now())
  }

  if (!saved || !exam) {
    return (
      <main className="page">
        <a className="back" href="#/">
          ← На главную
        </a>
        <header className="topic-head">
          <p className="eyebrow">Тренировка</p>
          <h1>Контрольная</h1>
        </header>
        <div className="card">
          <fieldset className="seg formats" aria-label="Формат работы">
            <legend className="muted">Какую работу писать</legend>
            {FORMATS.map((f) => (
              <label key={f.id} className={kind === f.id ? 'on' : ''}>
                <input type="radio" name="kind" checked={kind === f.id} onChange={() => setKind(f.id)} />
                <span>
                  <strong>{f.title}</strong>
                  <span className="muted">{f.blurb}</span>
                </span>
              </label>
            ))}
          </fieldset>
          <p className="muted">Подсказок во время работы нет, ответы и разбор ошибок — в конце. Каждый раз новый вариант.</p>
          <fieldset className="seg" aria-label="Сложность">
            <legend className="muted">Сложность</legend>
            <label className={difficulty === 'basic' ? 'on' : ''}>
              <input type="radio" name="d" checked={difficulty === 'basic'} onChange={() => setDifficulty('basic')} /> Как в тетради и книге
            </label>
            <label className={difficulty === 'advanced' ? 'on' : ''}>
              <input type="radio" name="d" checked={difficulty === 'advanced'} onChange={() => setDifficulty('advanced')} /> Посложнее
            </label>
          </fieldset>
          <label className="check-line">
            <input type="checkbox" checked={timer} onChange={(e) => setTimer(e.target.checked)} /> С таймером ({minutes} минут)
          </label>
          <button className="btn primary" onClick={start}>
            Начать контрольную ▸
          </button>
        </div>
      </main>
    )
  }

  if (saved.phase === 'result') {
    return (
      <main className="page">
        <Result exam={exam} saved={saved} onAgain={() => { persist(null); recorded.current = false }} />
      </main>
    )
  }

  const item = items[Math.min(saved.idx, items.length - 1)]
  const answered = items.filter((it) => (saved.answers[it.id] ?? '').trim() !== '').length
  const go = (idx: number) => persist({ ...saved, idx: Math.max(0, Math.min(items.length - 1, idx)) })
  const section = exam.sections.find((s) => s.items.includes(item))!

  return (
    <main className="page">
      <div className="exam-bar" role="status">
        <span>
          Вариант № {exam.seed} · отвечено {answered} из {items.length}
        </span>
        {left !== null && <span className={`timer ${left < 300 ? 'low' : ''}`}>⏱ {mmss(left)}</span>}
      </div>
      <div className="chips" aria-label="Задания">
        {items.map((it, i) => (
          <button
            key={it.id}
            className={`chip ${i === saved.idx ? 'on' : ''} ${(saved.answers[it.id] ?? '').trim() ? 'solved' : ''}`}
            onClick={() => go(i)}
            aria-label={`Задание ${it.label}${(saved.answers[it.id] ?? '').trim() ? ', есть ответ' : ''}`}
          >
            {it.label}
          </button>
        ))}
      </div>
      <h2 className="step-title">
        <span className="step-num">{section.kicker}</span>
        {section.title}
      </h2>
      <ItemView
        item={item}
        value={saved.answers[item.id] ?? ''}
        onChange={(v) => persist({ ...saved, answers: { ...saved.answers, [item.id]: v } })}
        onNext={() => go(saved.idx + 1)}
      />
      <div className="nav-row">
        <button className="btn ghost" disabled={saved.idx === 0} onClick={() => go(saved.idx - 1)}>
          ◂ Назад
        </button>
        {saved.idx < items.length - 1 ? (
          <button className="btn primary" onClick={() => go(saved.idx + 1)}>
            Дальше ▸
          </button>
        ) : (
          <button
            className="btn primary"
            onClick={() => {
              const empty = items.length - answered
              if (empty === 0 || window.confirm(`Без ответа осталось: ${empty}. Сдать работу?`)) finish(saved)
            }}
          >
            Сдать работу
          </button>
        )}
      </div>
      <p className="foot">
        <button
          className="link-btn"
          onClick={() => {
            if (window.confirm('Прервать контрольную? Результат не сохранится.')) {
              persist(null)
              recorded.current = false
            }
          }}
        >
          Прервать
        </button>
      </p>
    </main>
  )
}
