/// <reference types="vitest" /> // Keep this line
import { defineConfig, UserConfig } from 'vite'; // Import UserConfig
import react from '@vitejs/plugin-react';
import type { InlineConfig } from 'vitest'; // Import Vitest's config type

// Combine the types
interface VitestConfigExport extends UserConfig {
  test: InlineConfig;
}

export default defineConfig({
  plugins: [react()],
  test: { // Vitest configuration options
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.ts', 
    deps: {
      inline: ['msw'], 
    },
  },
} as VitestConfigExport ); // Cast the config object to the combined type