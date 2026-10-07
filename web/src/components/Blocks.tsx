import { useState } from 'react'
import type { Block } from '../content/types'
import { Viz } from '../viz'
import { Rich, Tex } from './Tex'

function Example({ title, steps, reveal = true }: { title?: string; steps: string[]; reveal?: boolean }) {
  const [shown, setShown] = useState(reveal ? 1 : steps.length)
  const more = shown < steps.length
  return (
    <div className="example">
      {title && (
        <h4>
          <Rich text={title} />
        </h4>
      )}
      <ol>
        {steps.slice(0, shown).map((s, i) => (
          <li key={i} className={reveal && i === shown - 1 && i > 0 ? 'fresh' : ''}>
            <Rich text={s} />
          </li>
        ))}
      </ol>
      {more && (
        <div className="example-actions">
          <button className="btn small" onClick={() => setShown(shown + 1)}>
            Дальше ▸
          </button>
          <button className="btn small ghost" onClick={() => setShown(steps.length)}>
            Показать всё
          </button>
        </div>
      )}
    </div>
  )
}

export function BlockView({ block }: { block: Block }) {
  switch (block.type) {
    case 'text':
      return (
        <p className="lesson-text">
          <Rich text={block.text} />
        </p>
      )
    case 'math':
      return (
        <div className="math-block">
          <Tex tex={block.tex} display />
        </div>
      )
    case 'note':
      return (
        <aside className={`note ${block.kind}`}>
          <span className="note-icon" aria-hidden>
            {block.kind === 'warn' ? '⚠️' : '💡'}
          </span>
          <div>
            <Rich text={block.text} />
          </div>
        </aside>
      )
    case 'example':
      return <Example title={block.title} steps={block.steps} reveal={block.reveal} />
    case 'viz':
      return <Viz id={block.id} preset={block.preset} />
  }
}
