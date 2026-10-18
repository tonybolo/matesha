import { Fragment, useMemo, useState } from 'react'
import { renderPrompt } from '../content/prompt'
import type { Task, Topic } from '../content/types'
import { checkAnswer, expectedOrder, type CheckResult } from '../lib/check'
import { toTex } from '../lib/expr'
import { hrefTopic } from '../route'
import { Figure } from '../viz'
import { GROUP_GOAL, markRevealed, recordAttempt, type TopicProgress } from '../store/progress'
import { useProgress } from '../store/useProgress'
import { AnswerInput, varsOf } from './AnswerInput'
import { Rich } from './Tex'

const LEVELS: { level: 1 | 2 | 3; title: string; hint: string }[] = [
  { level: 1, title: 'Уровень 1', hint: 'как в учебнике' },
  { level: 2, title: 'Уровень 2', hint: 'посложнее' },
  { level: 3, title: 'Уровень 3', hint: 'с подвохом' },
]

const LEVEL_NAMES = { 1: 'как в учебнике', 2: 'посложнее', 3: 'с подвохом' } as const

export function answerText(task: Task): string {
  if (task.answerTex) return '$' + task.answerTex + '$'
  switch (task.answerKind) {
    case 'roots':
      return '$' + task.answer.split(';').map((p) => toTex(p.trim()) ?? p).join(';\\ ') + '$'
    case 'compare':
      return `«${task.answer === '<' ? '<' : task.answer === '>' ? '>' : '='}»`
    case 'choice':
      return task.options?.[Number(task.answer)] ?? task.answer
    case 'order': {
      const order = task.items ? expectedOrder(task.items) : null
      if (!order || !task.items) return task.answer
      return order.map((i) => '$' + (toTex(task.items![i]) ?? task.items![i]) + '$').join(' < ')
    }
    default:
      return '$' + (toTex(task.answer) ?? task.answer) + '$'
  }
}

export function taskPrompt(task: Task): string {
  return renderPrompt(task.prompt, task.expr, { expr2: task.expr2, items: task.items, tex: task.tex })
}

/** Переходы между заданиями: null — на краю списка кнопка неактивна. */
type Nav = { prev: (() => void) | null; next: (() => void) | null }

function TaskPanel({ topic, task, nav }: { topic: Topic; task: Task; nav: Nav }) {
  const { state, update } = useProgress()
  const st = state.topics[topic.id]?.tasks[task.id]
  const [value, setValue] = useState('')
  const [res, setRes] = useState<CheckResult | null>(null)
  const [hint, setHint] = useState(false)
  const solved = !!st?.solved
  // Вернулись к заданию, которое уже решено раньше: вместо пустого поля показываем ответ и решение.
  const [revisit] = useState(solved)
  const [solution, setSolution] = useState(solved)

  const submit = () => {
    if (solved) return
    const r = checkAnswer(value, task.answer, task.answerKind, { reduce: task.reduce, radical: task.radical, items: task.items })
    setRes(r)
    if (r.status === 'correct') update((s) => recordAttempt(s, topic.id, task.id, true, undefined, task.skills))
    else if (r.status === 'wrong') update((s) => recordAttempt(s, topic.id, task.id, false, undefined, task.skills))
  }

  const showSolution = () => {
    setSolution(true)
    update((s) => markRevealed(s, topic.id, task.id))
  }

  const vars = useMemo(() => varsOf(task.expr, task.answer), [task])
  const sqrtKey = useMemo(() => [task.expr, task.expr2, task.answer, task.prompt].some((t) => t?.includes('sqrt') || t?.includes('√')), [task])
  const attempts = st?.attempts ?? 0
  const label = task.num ?? (task.group ? `Ур. ${task.level}` : `№ ${task.id.split('-')[1]}`)

  return (
    <div className="task">
      <div className="task-head">
        <span className="badge">{label}</span>
        <span className="muted">{task.group ? LEVEL_NAMES[task.level] : task.source}</span>
        {solved && <span className="badge ok">решено{st?.firstTry ? ' с первой попытки' : ''}</span>}
      </div>
      <p className="q-prompt">
        <Rich text={taskPrompt(task)} />
      </p>
      {task.fig && <Figure fig={task.fig} />}
      {revisit ? (
        <div className="feedback ok revisit">
          <strong>Уже решено ✓</strong>
          <p>
            Ответ: <Rich text={answerText(task)} />
          </p>
        </div>
      ) : (
        <>
          <AnswerInput
            value={value}
            onChange={(v) => {
              setValue(v)
              if (res && res.status !== 'correct') setRes(null)
            }}
            onSubmit={submit}
            kind={task.answerKind}
            vars={vars}
            sqrtKey={sqrtKey}
            placeholder={task.placeholder ?? (/^-?\d+([./]\d+)?$/.test(task.answer) && task.answerKind === 'expr' ? 'ответ числом, например 7 или 3/4' : undefined)}
            options={task.options}
            items={task.items}
            disabled={solved}
          />
          {res && (
            <div className={`feedback ${res.status === 'correct' ? 'ok' : res.status === 'wrong' ? 'bad' : 'soft'}`}>
              <strong>{res.status === 'correct' ? 'Верно! 🎉' : res.message}</strong>
              {res.status === 'correct' && <p>{st?.firstTry ? '+10 очков' : '+5 очков'}</p>}
            </div>
          )}
        </>
      )}
      <div className="task-actions">
        {!solved && (
          <button className="btn small ghost" onClick={() => setHint(true)} disabled={hint}>
            💡 Подсказка
          </button>
        )}
        {!revisit && (solved || attempts > 0 || hint) && (
          <button className="btn small ghost" onClick={showSolution} disabled={solution}>
            Показать решение
          </button>
        )}
      </div>
      <div className="nav-row task-nav">
        <button className="btn ghost" onClick={nav.prev ?? undefined} disabled={!nav.prev}>
          ◂ Предыдущая
        </button>
        <button className={`btn ${solved ? 'primary' : 'ghost'}`} onClick={nav.next ?? undefined} disabled={!nav.next}>
          Следующая ▸
        </button>
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
          {!revisit && (
            <p className="muted">
              Ответ: <Rich text={answerText(task)} />
            </p>
          )}
        </div>
      )}
    </div>
  )
}

/** Ряд номеров заданий: зелёный — решено, жёлтый — были попытки, рамка — открыто сейчас. */
function TaskChips({ list, idx, progress, onPick }: { list: Task[]; idx: number; progress: TopicProgress | undefined; onPick: (i: number) => void }) {
  if (list.length < 2) return null
  return (
    <div className="chips small" role="group" aria-label="Задания, нажми на номер, чтобы открыть">
      {list.map((t, i) => {
        const ts = progress?.tasks[t.id]
        return (
          <button
            key={t.id}
            className={`chip ${i === idx ? 'on' : ''} ${ts?.solved ? 'solved' : ts && ts.attempts > 0 ? 'tried' : ''}`}
            onClick={() => onPick(i)}
            aria-label={`Задача ${i + 1}${ts?.solved ? ', решена' : ''}`}
            aria-current={i === idx ? 'true' : undefined}
          >
            {i + 1}
          </button>
        )
      })}
    </div>
  )
}

const stepNav = (idx: number, length: number, setPos: (i: number) => void): Nav => ({
  prev: idx > 0 ? () => setPos(idx - 1) : null,
  next: idx < length - 1 ? () => setPos(idx + 1) : null,
})

/** Тренажёр с группами типов (сгенерированные задания): внутри группы идём по порядку, уровни растут. */
function GroupTrainer({ topic, initialGroup }: { topic: Topic; initialGroup?: string }) {
  const { state } = useProgress()
  const progress = state.topics[topic.id]
  const groups = topic.groups ?? []
  const startGroup = groups.find((g) => g.id === initialGroup)?.id ?? groups[0]?.id ?? ''
  const [gid, setGid] = useState(startGroup)
  const list = useMemo(() => topic.tasks.filter((t) => t.group === gid), [topic, gid])
  const current = groups.find((g) => g.id === gid)
  const firstOpen = (l: Task[]) => {
    const i = l.findIndex((t) => !progress?.tasks[t.id]?.solved)
    return i < 0 ? 0 : i
  }
  const [pos, setPos] = useState(() => firstOpen(topic.tasks.filter((t) => t.group === startGroup)))
  const idx = Math.min(pos, Math.max(0, list.length - 1))
  const task = list[idx]
  const groupSolved = (id: string) => topic.tasks.filter((t) => t.group === id && progress?.tasks[t.id]?.solved).length
  const doneAll = list.length > 0 && groupSolved(gid) >= Math.min(GROUP_GOAL, list.length)

  return (
    <section className="trainer">
      <div className="groups" role="tablist" aria-label="Типы заданий">
        {groups.map((g, i) => {
          const done = Math.min(GROUP_GOAL, groupSolved(g.id))
          return (
            <Fragment key={g.id}>
              {g.star && !groups[i - 1]?.star && <p className="groups-label">⭐ Олимпиада: задачи посложнее учебных</p>}
              <button
                role="tab"
                aria-selected={gid === g.id}
                className={`group ${gid === g.id ? 'on' : ''} ${done >= GROUP_GOAL ? 'done' : ''}`}
                onClick={() => {
                  setGid(g.id)
                  setPos(firstOpen(topic.tasks.filter((t) => t.group === g.id)))
                }}
              >
                <strong>{g.title}</strong>
                <span className="muted">
                  {done} / {GROUP_GOAL}
                </span>
              </button>
            </Fragment>
          )
        })}
      </div>
      {current?.lessonStep !== undefined && (
        <p className="group-lesson">
          <a className="link" href={hrefTopic(topic.id, 'learn', current.lessonStep)}>
            📖 Как решать этот тип: открыть объяснение
          </a>
        </p>
      )}
      {doneAll && <p className="feedback ok">Цель по этому типу выполнена ({GROUP_GOAL} решено). Можно идти дальше или потренироваться ещё.</p>}
      <TaskChips list={list} idx={idx} progress={progress} onPick={setPos} />
      {task && <TaskPanel key={task.id} topic={topic} task={task} nav={stepNav(idx, list.length, setPos)} />}
    </section>
  )
}

export function Trainer({ topic, initialGroup }: { topic: Topic; initialGroup?: string }) {
  if (topic.groups?.length) return <GroupTrainer topic={topic} initialGroup={initialGroup} />
  return <LevelTrainer topic={topic} />
}

function LevelTrainer({ topic }: { topic: Topic }) {
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
      <TaskChips list={list} idx={idx} progress={progress} onPick={setPos} />
      {task && <TaskPanel key={task.id} topic={topic} task={task} nav={stepNav(idx, list.length, setPos)} />}
    </section>
  )
}
