/// <reference types="vite/client" />

// Injected by vite.config.ts `define` (and mirrored in jest.config.cjs `globals`
// for tests) instead of import.meta.env, so the same source compiles under both
// Vite's ESM build and ts-jest's CommonJS transform without special-casing.
declare const __API_BASE_URL__: string;
