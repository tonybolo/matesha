import { useMemo, useState } from 'react'
import { renderPrompt } from '../content/prompt'
import type { Task, Topic } from '../content/types'
import { checkAnswer, type CheckResult } from '../lib/check'
import { toTex } from '../lib/expr'
import { markRevealed, recordAttempt } from '../store/progress'
import { useProgress } from '../store/useProgress'
import { AnswerInput, varsOf } from './AnswerInput'
import { Rich } from './Tex'

const LEVELS: { level: 1 | 2 | 3; title: string; hint: string }[] = [
  { level: 1, title: 'Уровень 1', hint: 'как в учебнике' },
  { level: 2, title: 'Уровень 2', hint: 'посложнее' },
  { level: 3, title: 'Уровень 3', hint: 'с подвохом' },
]

function TaskPanel({ topic, task, onNext }: { topic: Topic; task: Task; onNext: () => void }) {
  const { state, update } = useProgress()
  const st = state.topics[topic.id]?.tasks[task.id]
  const [value, setValue] = useState('')
  const [res, setRes] = useState<CheckResult | null>(null)
  const [hint, setHint] = useState(false)
  const [solution, setSolution] = useState(false)
  const solved = !!st?.solved

  const submit = () => {
    if (solved) return
    const r = checkAnswer(value, task.answer, task.answerKind, { reduce: task.reduce })
    setRes(r)
    if (r.status === 'correct') update((s) => recordAttempt(s, topic.id, task.id, true))
    else if (r.status === 'wrong') update((s) => recordAttempt(s, topic.id, task.id, false))
  }

  const showSolution = () => {
    setSolution(true)
    update((s) => markRevealed(s, topic.id, task.id))
  }

  const vars = useMemo(() => varsOf(task.expr, task.answer), [task])
  const attempts = st?.attempts ?? 0

  return (
    <div className="task">
      <div className="task-head">
        <span className="badge">№ {task.id.split('-')[1]}</span>
        <span className="muted">{task.source}</span>
        {solved && <span className="badge ok">решено{st?.firstTry ? ' с первой попытки' : ''}</span>}
      </div>
      <p className="q-prompt">
        <Rich text={renderPrompt(task.prompt, task.expr)} />
      </p>
      <AnswerInput
        value={value}
        onChange={(v) => {
          setValue(v)
          if (res && res.status !== 'correct') setRes(null)
        }}
        onSubmit={submit}
        kind={task.answerKind}
        vars={vars}
        disabled={solved}
      />
      {res && (
        <div className={`feedback ${res.status === 'correct' ? 'ok' : res.status === 'wrong' ? 'bad' : 'soft'}`}>
          <strong>{res.status === 'correct' ? 'Верно! 🎉' : res.message}</strong>
          {res.status === 'correct' && <p>{st?.firstTry ? '+10 очков' : '+5 очков'}</p>}
        </div>
      )}
      <div className="task-actions">
        {!solved && (
          <button className="btn small ghost" onClick={() => setHint(true)} disabled={hint}>
            💡 Подсказка
          </button>
        )}
        {(solved || attempts > 0 || hint) && (
          <button className="btn small ghost" onClick={showSolution} disabled={solution}>
            Показать решение
          </button>
        )}
        {solved && (
          <button className="btn primary" onClick={onNext}>
            Следующая ▸
          </button>
        )}
        {!solved && (
          <button className="btn small ghost" onClick={onNext}>
            Пропустить
          </button>
        )}
      </div>
      {hint && !solved && (
        <aside className="note tip">
          <span className="note-icon" aria-hidden>💡</span>
          <div>
            <Rich text={task.hint} />
          </div>
        </aside>
      )}
      {solution && (
        <div className="example">
          <h4>Решение</h4>
          <ol>
            {task.solution.map((s, i) => (
              <li key={i}>
                <Rich text={s} />
              </li>
            ))}
          </ol>
          <p className="muted">
            Ответ: <Rich text={'$' + (task.answerKind === 'roots' ? task.answer.replace(/;/g, ';\\ ') : (toTex(task.answer) ?? task.answer)) + '$'} />
          </p>
        </div>
      )}
    </div>
  )
}

export function Trainer({ topic }: { topic: Topic }) {
  const { state } = useProgress()
  const progress = state.topics[topic.id]
  const tasksOf = (lv: number) => topic.tasks.filter((t) => t.level === lv)
  const openIndex = (lv: number) => Math.max(0, tasksOf(lv).findIndex((t) => !progress?.tasks[t.id]?.solved))
  const [level, setLevel] = useState<1 | 2 | 3>(1)
  // Номер задачи закреплён: решённая задача не должна «убегать» из-под ученика.
  const [pos, setPos] = useState(() => openIndex(1))
  const list = useMemo(() => topic.tasks.filter((t) => t.level === level), [topic, level])
  const idx = Math.min(pos, list.length - 1)
  const task = list[idx]

  const goNext = () => {
    const nextOpen = list.findIndex((t, i) => i > idx && !progress?.tasks[t.id]?.solved)
    setPos(nextOpen >= 0 ? nextOpen : (idx + 1) % list.length)
  }

  return (
    <section className="trainer">
      <div className="levels" role="tablist">
        {LEVELS.map((l) => {
          const items = topic.tasks.filter((t) => t.level === l.level)
          const done = items.filter((t) => progress?.tasks[t.id]?.solved).length
          return (
            <button
              key={l.level}
              role="tab"
              aria-selected={level === l.level}
              className={`level ${level === l.level ? 'on' : ''}`}
              onClick={() => {
                setLevel(l.level)
                setPos(openIndex(l.level))
              }}
            >
              <strong>{l.title}</strong>
              <span>{l.hint}</span>
              <span className="muted">
                {done} / {items.length}
              </span>
            </button>
          )
        })}
      </div>
      <div className="chips" aria-label="Задачи уровня">
        {list.map((t, i) => {
          const ts = progress?.tasks[t.id]
          return (
            <button
              key={t.id}
              className={`chip ${i === idx ? 'on' : ''} ${ts?.solved ? 'solved' : ts && ts.attempts > 0 ? 'tried' : ''}`}
              onClick={() => setPos(i)}
              aria-label={`Задача ${i + 1}${ts?.solved ? ', решена' : ''}`}
            >
              {i + 1}
            </button>
          )
        })}
      </div>
      {task && <TaskPanel key={task.id} topic={topic} task={task} onNext={goNext} />}
    </section>
  )
}
