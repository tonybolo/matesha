import { useEffect } from 'react'
import type { Topic } from '../content/types'
import { go, hrefTopic } from '../route'
import { finishExplain, reachStep } from '../store/progress'
import { useProgress } from '../store/useProgress'
import { BlockView } from './Blocks'

export function Lesson({ topic, step }: { topic: Topic; step: number }) {
  const { update } = useProgress()
  const last = topic.steps.length - 1
  const idx = Math.min(step, last)
  const cur = topic.steps[idx]

  useEffect(() => {
    update((s) => reachStep(s, topic.id, idx))
  }, [topic.id, idx, update])

  const toStep = (n: number) => go(hrefTopic(topic.id, 'learn', n))

  return (
    <section className="lesson">
      <div className="dots" role="tablist" aria-label="Шаги объяснения">
        {topic.steps.map((s, i) => (
          <button
            key={s.id}
            role="tab"
            aria-selected={i === idx}
            aria-label={`Шаг ${i + 1}: ${s.title}`}
            className={`dot ${i === idx ? 'on' : ''} ${i < idx ? 'done' : ''}`}
            onClick={() => toStep(i)}
          >
            {i + 1}
          </button>
        ))}
      </div>
      <h2 className="step-title">
        <span className="step-num">Шаг {idx + 1} из {topic.steps.length}</span>
        {cur.title}
      </h2>
      <div className="step-body">
        {cur.blocks.map((b, i) => (
          <BlockView key={`${cur.id}-${i}`} block={b} />
        ))}
      </div>
      <div className="nav-row">
        <button className="btn ghost" disabled={idx === 0} onClick={() => toStep(idx - 1)}>
          ◂ Назад
        </button>
        {idx < last ? (
          <button className="btn primary" onClick={() => toStep(idx + 1)}>
            Дальше ▸
          </button>
        ) : (
          <button
            className="btn primary"
            onClick={() => {
              update((s) => finishExplain(s, topic.id))
              go(hrefTopic(topic.id, 'check'))
            }}
          >
            Всё понятно — проверить себя ▸
          </button>
        )}
      </div>
    </section>
  )
}
