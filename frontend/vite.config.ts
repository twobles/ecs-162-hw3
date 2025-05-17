import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [svelte()],
  server: {
    watch: {
      usePolling: true,
      interval: 1000,
    },
    ...(mode === 'development' ? {
      proxy: {
        '/api': {
          target: 'http://backend:8000',
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            proxy.on('proxyReq', (_proxyReq, req, _res) => {
              console.log('Proxying request:', req.url)
            })
          }
        },
      },
    } : undefined),
  },
  test: {
    globals: true,
    enviornment: 'jsdom',
  },
}))
