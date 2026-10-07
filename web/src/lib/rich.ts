export type Segment =
  | { kind: 'text'; text: string }
  | { kind: 'bold'; text: string }
  | { kind: 'math'; tex: string; display: boolean }

/** Разбор строки с $формулами$ и **жирным**. Формулы внутри жирного не поддерживаются. */
export function parseRich(src: string): Segment[] {
  const out: Segment[] = []
  const re = /\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g
  let last = 0
  let m: RegExpExecArray | null
  const pushText = (s: string) => {
    if (!s) return
    const parts = s.split(/\*\*(.+?)\*\*/g)
    parts.forEach((p, i) => {
      if (!p) return
      out.push(i % 2 === 1 ? { kind: 'bold', text: p } : { kind: 'text', text: p })
    })
  }
  while ((m = re.exec(src))) {
    pushText(src.slice(last, m.index))
    if (m[1] !== undefined) out.push({ kind: 'math', tex: m[1].trim(), display: true })
    else out.push({ kind: 'math', tex: m[2].trim(), display: false })
    last = m.index + m[0].length
  }
  pushText(src.slice(last))
  return out
}

export function mathOf(src: string): string[] {
  return parseRich(src)
    .filter((s): s is Extract<Segment, { kind: 'math' }> => s.kind === 'math')
    .map((s) => s.tex)
}
