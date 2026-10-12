import { useEffect, useState } from 'react'

export type Tab = 'learn' | 'check' | 'train'
export type Route = { name: 'home' } | { name: 'exam' } | { name: 'topic'; id: string; tab: Tab; step: number; group?: string }

export function parseHash(hash: string): Route {
  const [path, query = ''] = hash.replace(/^#/, '').split('?')
  if (path === '/exam') return { name: 'exam' }
  const m = path.match(/^\/t\/([^/]+)(?:\/(learn|check|train))?$/)
  if (!m) return { name: 'home' }
  const params = new URLSearchParams(query)
  const step = Math.max(0, parseInt(params.get('step') ?? '0', 10) || 0)
  const group = params.get('group') ?? undefined
  return { name: 'topic', id: decodeURIComponent(m[1]), tab: (m[2] as Tab) ?? 'learn', step, group }
}

export function hrefTopic(id: string, tab: Tab = 'learn', step?: number, group?: string): string {
  const query = [step ? `step=${step}` : '', group ? `group=${encodeURIComponent(group)}` : ''].filter(Boolean).join('&')
  return `#/t/${encodeURIComponent(id)}/${tab}${query ? `?${query}` : ''}`
}

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(() => parseHash(window.location.hash))
  useEffect(() => {
    const on = () => setRoute(parseHash(window.location.hash))
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return route
}

export function go(hash: string): void {
  window.location.hash = hash
  window.scrollTo({ top: 0 })
}
