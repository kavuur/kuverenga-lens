/* Kuverenga Lens service worker: keeps the whole app (including the OCR engine) on the phone so it works offline */
const CACHE = 'kuverenga-lens-v3';
const FILES = [
  './',
  'index.html',
  'css/style.css',
  'js/app.js',
  'js/syllables.js',
  'manifest.webmanifest',
  'icons/logo.svg',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/icon-maskable-512.png',
  'fonts/OpenDyslexic-Regular.woff',
  'fonts/OpenDyslexic-Bold.woff',
  'vendor/tesseract/tesseract.min.js',
  'vendor/tesseract/worker.min.js',
  'vendor/tesseract/tesseract-core-lstm.wasm.js',
  'vendor/tesseract/tesseract-core-simd-lstm.wasm.js',
  'vendor/lang/eng.traineddata.gz'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then((hit) => hit || fetch(e.request).then((res) => {
      // also keep the handwriting reader's library files (from the jsDelivr CDN) for offline use;
      // the model itself is cached by transformers.js in its own cache
      const url = new URL(e.request.url);
      if (res.ok && (url.origin === location.origin || url.hostname === 'cdn.jsdelivr.net')) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
      }
      return res;
    }))
  );
});
