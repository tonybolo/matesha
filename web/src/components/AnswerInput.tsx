import { useLayoutEffect, useRef } from 'react'
import type { AnswerKind } from '../content/types'
import { parseNumberSet } from '../lib/check'
import { toTex, tryParse } from '../lib/expr'
import { Tex } from './Tex'

type Key = { label: string; insert: string; caret?: number; title?: string; wide?: boolean }

function keysFor(kind: AnswerKind, vars: string[]): Key[] {
  if (kind === 'roots') {
    return [
      { label: '−', insert: '-', title: 'минус' },
      { label: '/', insert: '/', title: 'дробная черта' },
      { label: ';', insert: '; ', title: 'разделитель значений' },
      { label: 'нет', insert: 'нет', title: 'таких значений нет', wide: true },
    ]
  }
  return [
    ...vars.map((v) => ({ label: v, insert: v })),
    { label: 'дробь', insert: '()/()', caret: 1, title: 'числитель / знаменатель', wide: true },
    { label: '( )', insert: '()', caret: 1 },
    { label: 'xⁿ', insert: '^', title: 'степень' },
    { label: '+', insert: '+' },
    { label: '−', insert: '-' },
    { label: '·', insert: '*', title: 'умножить' },
  ]
}

export function varsOf(...sources: (string | undefined)[]): string[] {
  const set = new Set<string>()
  for (const s of sources) {
    if (!s) continue
    const p = tryParse(s)
    p?.vars.forEach((v) => set.add(v))
  }
  return [...set].sort().slice(0, 5)
}

type Props = {
  value: string
  onChange: (v: string) => void
  onSubmit: () => void
  kind: AnswerKind
  vars: string[]
  disabled?: boolean
  submitLabel?: string
}

export function AnswerInput({ value, onChange, onSubmit, kind, vars, disabled, submitLabel = 'Проверить' }: Props) {
  const ref = useRef<HTMLInputElement>(null)
  const caret = useRef<number | null>(null)

  useLayoutEffect(() => {
    if (caret.current !== null && ref.current) {
      ref.current.focus()
      ref.current.setSelectionRange(caret.current, caret.current)
      caret.current = null
    }
  })

  const insert = (k: Key) => {
    const el = ref.current
    const start = el?.selectionStart ?? value.length
    const end = el?.selectionEnd ?? value.length
    const next = value.slice(0, start) + k.insert + value.slice(end)
    caret.current = start + (k.caret ?? k.insert.length)
    onChange(next)
  }

  const backspace = () => {
    const el = ref.current
    const start = el?.selectionStart ?? value.length
    const end = el?.selectionEnd ?? value.length
    if (start === end && start > 0) {
      caret.current = start - 1
      onChange(value.slice(0, start - 1) + value.slice(end))
    } else if (start !== end) {
      caret.current = start
      onChange(value.slice(0, start) + value.slice(end))
    }
  }

  let preview: React.ReactNode = null
  if (value.trim()) {
    if (kind === 'expr') {
      const tex = toTex(value)
      preview = tex ? <Tex tex={tex} display /> : <span className="muted">Пока не могу разобрать запись…</span>
    } else {
      const set = parseNumberSet(value)
      preview =
        set === null ? (
          <span className="muted">Пока не могу разобрать запись…</span>
        ) : set.length === 0 ? (
          <span>таких значений нет</span>
        ) : (
          <Tex tex={set.map((v) => String(v).replace('.', '{,}')).join(';\\ ')} />
        )
    }
  }

  return (
    <div className="answer-input">
      <div className="input-row">
        <input
          ref={ref}
          type="text"
          inputMode="text"
          autoCapitalize="off"
          autoCorrect="off"
          autoComplete="off"
          spellCheck={false}
          disabled={disabled}
          value={value}
          maxLength={120}
          placeholder={kind === 'roots' ? 'например: 3; -3' : 'например: (x+1)/(x-2)'}
          aria-label="Ответ"
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') onSubmit()
          }}
        />
        <button className="btn primary" disabled={disabled || !value.trim()} onClick={onSubmit}>
          {submitLabel}
        </button>
      </div>
      <div className="keypad" aria-label="Клавиши для ввода">
        {keysFor(kind, vars).map((k) => (
          <button key={k.label} type="button" className={`key ${k.wide ? 'wide' : ''}`} title={k.title} disabled={disabled} onClick={() => insert(k)}>
            {k.label}
          </button>
        ))}
        <button type="button" className="key" title="стереть" aria-label="Стереть" disabled={disabled} onClick={backspace}>
          ⌫
        </button>
      </div>
      <div className="preview" aria-live="polite">
        {preview ? (
          <>
            <span className="preview-label">Я понял так:</span>
            {preview}
          </>
        ) : (
          <span className="muted">
            {kind === 'expr'
              ? 'Дробь пиши через «/», числитель и знаменатель — в скобках: (x+1)/(x-2).'
              : 'Несколько значений пиши через «;». Если значений нет — напиши «нет».'}
          </span>
        )}
      </div>
    </div>
  )
}
