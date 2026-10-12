import { useEffect, useRef, useState } from 'react'
import { cheatsheet, cubes, squares } from '../content/cheatsheet'
import { Tex } from './Tex'

function Sheet({ onClose }: { onClose: () => void }) {
  const closeRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    const prevFocus = document.activeElement as HTMLElement | null
    closeRef.current?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    document.body.classList.add('no-scroll')
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.classList.remove('no-scroll')
      prevFocus?.focus?.()
    }
  }, [onClose])

  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <div className="sheet" role="dialog" aria-modal="true" aria-label="Шпаргалка" onClick={(e) => e.stopPropagation()}>
        <header className="sheet-head">
          <h2>Шпаргалка</h2>
          <button ref={closeRef} className="btn small" onClick={onClose} aria-label="Закрыть шпаргалку">
            ✕ Закрыть
          </button>
        </header>
        <div className="sheet-body">
          {cheatsheet.map((s) => (
            <section key={s.title}>
              <h3>{s.title}</h3>
              <ul className="sheet-list">
                {s.items.map((it) => (
                  <li key={it.name}>
                    <span className="sheet-name">{it.name}</span>
                    <Tex tex={it.tex} display />
                  </li>
                ))}
              </ul>
            </section>
          ))}
          <section>
            <h3>Квадраты чисел</h3>
            <div className="num-table" role="table" aria-label="Квадраты чисел от 1 до 20">
              {squares.map(({ n, v }) => (
                <span key={n} className="num-cell">
                  <Tex tex={`${n}^2=${v}`} />
                </span>
              ))}
            </div>
          </section>
          <section>
            <h3>Кубы чисел</h3>
            <div className="num-table" role="table" aria-label="Кубы чисел от 1 до 10">
              {cubes.map(({ n, v }) => (
                <span key={n} className="num-cell">
                  <Tex tex={`${n}^3=${v}`} />
                </span>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export function CheatsheetButton() {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button className="fab" onClick={() => setOpen(true)} aria-label="Открыть шпаргалку с формулами">
        <span aria-hidden>📐</span>
        <span className="fab-label"> Шпаргалка</span>
      </button>
      {open && <Sheet onClose={() => setOpen(false)} />}
    </>
  )
}
