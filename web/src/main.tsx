import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { initWebViewCheck } from './lib/webviewCompat';
import { initSunlightMode } from './lib/sunlightMode';
import { initMemoryGuard } from './lib/memoryGuard';
import { initSyncEngine } from './offline/syncEngine';

// Initialize native, offline and accessibility guards
initWebViewCheck();
initSunlightMode();
initMemoryGuard();
initSyncEngine();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
