import { useEffect, useState } from 'react'

export type Tab = 'learn' | 'check' | 'train'
export type Route = { name: 'home' } | { name: 'topic'; id: string; tab: Tab; step: number }

export function parseHash(hash: string): Route {
  const [path, query = ''] = hash.replace(/^#/, '').split('?')
  const m = path.match(/^\/t\/([^/]+)(?:\/(learn|check|train))?$/)
  if (!m) return { name: 'home' }
  const params = new URLSearchParams(query)
  const step = Math.max(0, parseInt(params.get('step') ?? '0', 10) || 0)
  return { name: 'topic', id: decodeURIComponent(m[1]), tab: (m[2] as Tab) ?? 'learn', step }
}

export function hrefTopic(id: string, tab: Tab = 'learn', step?: number): string {
  return `#/t/${encodeURIComponent(id)}/${tab}${step ? `?step=${step}` : ''}`
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
