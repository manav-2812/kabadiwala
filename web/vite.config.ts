import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';
import fs from 'fs';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  /** Injects VITE_FIREBASE_* env vars into the FCM service worker at dev time */
  const fcmSwEnvPlugin = {
    name: 'fcm-sw-env-inject',
    configureServer(server: any) {
      server.middlewares.use((req: any, res: any, next: any) => {
        if (req.url === '/firebase-messaging-sw.js') {
          const swPath = path.resolve(process.cwd(), 'public/firebase-messaging-sw.js');
          let sw = fs.readFileSync(swPath, 'utf-8');
          sw = sw
            .replace("self.__FIREBASE_API_KEY__ || ''",             `'${env.VITE_FIREBASE_API_KEY || ''}'`)
            .replace("self.__FIREBASE_AUTH_DOMAIN__ || ''",        `'${env.VITE_FIREBASE_AUTH_DOMAIN || ''}'`)
            .replace("self.__FIREBASE_PROJECT_ID__ || ''",         `'${env.VITE_FIREBASE_PROJECT_ID || ''}'`)
            .replace("self.__FIREBASE_STORAGE_BUCKET__ || ''",     `'${env.VITE_FIREBASE_STORAGE_BUCKET || ''}'`)
            .replace("self.__FIREBASE_MESSAGING_SENDER_ID__|| ''", `'${env.VITE_FIREBASE_MESSAGING_SENDER_ID || ''}'`)
            .replace("self.__FIREBASE_APP_ID__ || ''",             `'${env.VITE_FIREBASE_APP_ID || ''}'`);
          res.setHeader('Content-Type', 'application/javascript');
          res.end(sw);
        } else {
          next();
        }
      });
    },
  };

  return {
    plugins: [
      react(),
      tailwindcss(),
      fcmSwEnvPlugin,
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.svg', 'icons/*.png'],
        manifest: {
          name: 'Kabadiwala Connect',
          short_name: 'Kabadiwala',
          description: 'Vernacular, low-literacy, offline-tolerant e-waste marketplace',
          theme_color: '#0B3D2E',
          background_color: '#F7F5EF',
          display: 'standalone',
          orientation: 'portrait',
          icons: [
            {
              src: 'favicon.svg',
              sizes: '192x192 512x512',
              type: 'image/svg+xml'
            }
          ]
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
          runtimeCaching: [
            {
              urlPattern: ({ url }) => url.pathname.startsWith('/api/materials'),
              handler: 'StaleWhileRevalidate',
              options: {
                cacheName: 'materials-cache',
                expiration: { maxAgeSeconds: 86400 * 7 }
              }
            },
            {
              urlPattern: ({ url }) => url.pathname.startsWith('/api/prices'),
              handler: 'NetworkFirst',
              options: {
                cacheName: 'prices-cache',
                expiration: { maxAgeSeconds: 86400 }
              }
            }
          ]
        }
      })
    ],
    // Conservative target for old Android WebView (Android 8-10)
    // Chrome 80 corresponds to WebView on Android ~10
    build: {
      target: 'chrome80',
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules')) {
              if (id.includes('recharts') || id.includes('d3-')) {
                return 'vendor-charts';
              }
              if (id.includes('leaflet')) {
                return 'vendor-maps';
              }
              if (id.includes('firebase')) {
                return 'vendor-firebase';
              }
              if (id.includes('@capacitor')) {
                return 'vendor-capacitor';
              }
            }
          }
        }
      }
    },
    server: {
      port: 5173,
      host: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true
        },
        '/ws': {
          target: 'ws://localhost:8000',
          ws: true
        }
      }
    }
  };
});
