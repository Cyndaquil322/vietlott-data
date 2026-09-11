// Vietlott Hub Service Worker v2.1 - Network-First for Fresh Data
const CACHE_NAME = 'vietlott-hub-v2.1';
const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png',
  './assets/css/styles.css',
  './assets/js/core.js',
  './assets/js/common_analytics.js',
  './assets/js/advanced_quant.js',
  './assets/js/consensus_ensemble.js',
  './assets/js/notebook_bao7.js'
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => {
          if (k !== CACHE_NAME) {
            console.log('[ServiceWorker] Purging stale cache:', k);
            return caches.delete(k);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Network-First Strategy for HTML Navigation & JSON Data
// Ensures user always gets the freshest lottery results whenever online,
// while gracefully falling back to cache when offline.
self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = req.url;
  const isNavigation = req.mode === 'navigate' || req.destination === 'document' || url.endsWith('/') || url.endsWith('index.html');
  const isJsonData = url.includes('.json');

  if (isNavigation || isJsonData) {
    // Network-First with Cache Fallback
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(req, clone));
          }
          return res;
        })
        .catch(() => caches.match(req, { ignoreSearch: true }))
    );
  } else {
    // Stale-While-Revalidate for static assets (CSS, JS, icons)
    e.respondWith(
      caches.match(req).then((cached) => {
        const fetchPromise = fetch(req)
          .then((networkRes) => {
            if (networkRes && networkRes.ok) {
              const clone = networkRes.clone();
              caches.open(CACHE_NAME).then((c) => c.put(req, clone));
            }
            return networkRes;
          })
          .catch(() => cached);
        return cached || fetchPromise;
      })
    );
  }
});
