// Service Worker para AgroTech Portugal
const CACHE_NAME = 'agrotech-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/main.css',
  '/static/css/design-system-v2.css',
  '/static/css/components.css',
  '/static/css/mobile-first.css',
  '/static/css/portugal-design-system.css',
  '/static/css/dashboard-portugal.css',
  '/static/js/main.js',
  '/static/js/charts.js',
  '/static/js/theme-switcher.js',
  '/static/images/logo.png',
  '/static/favicon.ico',
  'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
];

// Instalar Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// Ativar e limpar caches antigos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Estratégia de cache: stale-while-revalidate
self.addEventListener('fetch', event => {
  // Ignorar requisições não GET e requisições a APIs
  if (event.request.method !== 'GET' || 
      event.request.url.includes('/api/') || 
      event.request.url.includes('/auth/')) {
    return;
  }

  event.respondWith(
    caches.open(CACHE_NAME).then(cache => {
      return cache.match(event.request).then(cachedResponse => {
        const fetchPromise = fetch(event.request)
          .then(networkResponse => {
            // Armazenar no cache apenas se for uma resposta válida
            if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })
          .catch(error => {
            console.log('Fetch falhou; retornando resposta do cache', error);
            // Se não houver resposta da rede, retorna o que temos no cache ou o fallback
            return cachedResponse;
          });
          
        // Retorna o cache primeiro, depois atualiza com a rede
        return cachedResponse || fetchPromise;
      });
    })
  );
});

// Interceptar mensagens do cliente
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
