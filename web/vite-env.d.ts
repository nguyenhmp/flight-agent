/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.ts',
    deps: {
      inline: ['msw'], 
    },
    testEnvironment: 'jsdom',
    testEnvironmentOptions: {
      customExportConditions: [''], // Instructs Vitest with JSDOM to use the default export
    },
  },
});