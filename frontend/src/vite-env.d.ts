/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Public base URL of the deployed API. Leave empty for same-origin proxy. */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
