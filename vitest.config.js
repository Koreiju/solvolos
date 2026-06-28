import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['milkdown_app/ui/static/js/__tests__/**/*.test.js']
  },
})
