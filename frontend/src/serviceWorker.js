self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('van-ui-cache').then((cache) => {
      return cache.addAll(['/', '/index.html', '/styles.css', '/main.js']);
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});
