// vite.config.js
import { resolve } from 'path';

export default {
  build: {
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'index.html'),
        login: resolve(__dirname, 'login.html'),
        landing: resolve(__dirname, 'landing.html'),
        dashboard: resolve(__dirname, 'dashboard.html'),
        ml: resolve(__dirname, 'ml.html'),
      }
    }
  }
}
