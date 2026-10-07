import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { loadState, saveState, type State } from './progress'

type Ctx = { state: State; update: (fn: (s: State) => State) => void }
const ProgressContext = createContext<Ctx | null>(null)

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<State>(() => loadState())
  useEffect(() => saveState(state), [state])
  const update = useCallback((fn: (s: State) => State) => setState((s) => fn(s)), [])
  const value = useMemo(() => ({ state, update }), [state, update])
  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>
}

export function useProgress(): Ctx {
  const ctx = useContext(ProgressContext)
  if (!ctx) throw new Error('ProgressProvider отсутствует')
  return ctx
}
