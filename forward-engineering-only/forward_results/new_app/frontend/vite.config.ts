import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Frontend convention (per README / Stack Mapping Contract row 8-9):
// src/features/{module}/{components,hooks,api,types} + src/shared for cross-feature code.
export default defineConfig({
  plugins: [react()],
  define: {
    // Read at build time from the shell env; never a hard-coded backend URL.
    __API_BASE_URL__: JSON.stringify(process.env.VITE_API_BASE_URL ?? 'http://localhost:8080'),
  },
  server: {
    port: 5173,
  },
});
