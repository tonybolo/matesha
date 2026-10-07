import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import { VitePWA } from 'vite-plugin-pwa'
import { parse } from 'yaml'

// BASE_PATH задаёт подпапку хостинга (на GitHub Pages это /matesha/).
const base = process.env.BASE_PATH ?? '/'

// YAML-контент превращаем в JSON на этапе сборки: библиотека yaml в браузер не попадает.
const yamlContent = {
  name: 'yaml-content',
  transform(code: string, id: string) {
    if (!id.endsWith('.yaml')) return null
    return { code: `export default ${JSON.stringify(parse(code))}`, map: null }
  },
}

export default defineConfig({
  base,
  plugins: [
    yamlContent,
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/apple-touch-icon.png', 'icons/favicon-64.png'],
      manifest: {
        name: 'Матеша — алгебра 8 класса',
        short_name: 'Матеша',
        description: 'Алгебра по шагам: объяснение, проверка, тренировка.',
        lang: 'ru',
        start_url: base,
        scope: base,
        display: 'standalone',
        background_color: '#f7f8fc',
        theme_color: '#4f46e5',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: { globPatterns: ['**/*.{js,css,html,png,woff2}'] },
    }),
  ],
  build: { target: ['es2020', 'safari14', 'chrome87', 'firefox78'] },
  server: { fs: { allow: ['..'] } },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
})
