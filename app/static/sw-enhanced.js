// Service Worker Enhanced - AgTech Portugal v2.0
const CACHE_NAME = 'agtech-v2.0.0';
const CACHE_VERSION = '2.0.0';

// Assets críticos para cache
const CRITICAL_ASSETS = [
  '/',
  '/static/css/design-system-v2.css',
  '/static/css/components.css',
  '/static/js/theme-manager.js',
  '/static/js/loading-manager.js',
  '/static/js/notification-system.js',
  '/static/js/main.js',
  '/static/manifest.json',
  '/static/favicon.ico'
];

// Assets de fontes e ícones
const FONT_ASSETS = [
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Rotas que devem ser sempre buscadas da rede
const NETWORK_FIRST_ROUTES = [
  '/api/',
  '/auth/',
  '/dashboard/data',
  '/cultures/data',
  '/agent/chat'
];

// Rotas que podem ser servidas do cache
const CACHE_FIRST_ROUTES = [
  '/static/',
  '/dashboard',
  '/cultures',
  '/reports'
];

// Install Event
self.addEventListener('install', event => {
  console.log('[SW] Installing service worker v' + CACHE_VERSION);
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Caching critical assets');
        return cache.addAll(CRITICAL_ASSETS);
      })
      .then(() => {
        console.log('[SW] Critical assets cached successfully');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('[SW] Failed to cache critical assets:', error);
      })
  );
});

// Activate Event
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker v' + CACHE_VERSION);
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Service worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch Event
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and other protocols
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  event.respondWith(handleFetch(request));
});

async function handleFetch(request) {
  const url = new URL(request.url);
  const pathname = url.pathname;
  
  try {
    // Network first for API and dynamic routes
    if (NETWORK_FIRST_ROUTES.some(route => pathname.startsWith(route))) {
      return await networkFirst(request);
    }
    
    // Cache first for static assets and pages
    if (CACHE_FIRST_ROUTES.some(route => pathname.startsWith(route))) {
      return await cacheFirst(request);
    }
    
    // Stale while revalidate for other requests
    return await staleWhileRevalidate(request);
    
  } catch (error) {
    console.error('[SW] Fetch error:', error);
    return await handleOffline(request);
  }
}

// Network First Strategy
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Cache First Strategy
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    throw error;
  }
}

// Stale While Revalidate Strategy
async function staleWhileRevalidate(request) {
  const cachedResponse = await caches.match(request);
  
  const fetchPromise = fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      const cache = caches.open(CACHE_NAME);
      cache.then(c => c.put(request, networkResponse.clone()));
    }
    return networkResponse;
  }).catch(error => {
    console.warn('[SW] Network fetch failed:', error);
    return cachedResponse;
  });
  
  return cachedResponse || fetchPromise;
}

// Handle Offline Scenarios
async function handleOffline(request) {
  const url = new URL(request.url);
  
  // Return offline page for navigation requests
  if (request.mode === 'navigate') {
    const offlinePage = await caches.match('/offline.html');
    if (offlinePage) {
      return offlinePage;
    }
  }
  
  // Return cached version if available
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Return generic offline response
  return new Response(
    JSON.stringify({
      error: 'Offline',
      message: 'Você está offline. Verifique sua conexão com a internet.'
    }),
    {
      status: 503,
      statusText: 'Service Unavailable',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
}

// Background Sync
self.addEventListener('sync', event => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  try {
    // Sync pending data when back online
    const pendingData = await getStoredData('pending-sync');
    
    if (pendingData && pendingData.length > 0) {
      for (const item of pendingData) {
        try {
          await fetch(item.url, {
            method: item.method,
            headers: item.headers,
            body: item.body
          });
          
          // Remove from pending after successful sync
          await removeFromPendingSync(item.id);
        } catch (error) {
          console.error('[SW] Failed to sync item:', error);
        }
      }
    }
  } catch (error) {
    console.error('[SW] Background sync failed:', error);
  }
}

// Push Notifications
self.addEventListener('push', event => {
  console.log('[SW] Push received');
  
  const options = {
    body: 'Você tem novas atualizações no AgTech Portugal',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/badge-72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Ver Detalhes',
        icon: '/static/icons/action-explore.png'
      },
      {
        action: 'close',
        title: 'Fechar',
        icon: '/static/icons/action-close.png'
      }
    ]
  };
  
  if (event.data) {
    const payload = event.data.json();
    options.body = payload.body || options.body;
    options.title = payload.title || 'AgTech Portugal';
  }
  
  event.waitUntil(
    self.registration.showNotification('AgTech Portugal', options)
  );
});

// Notification Click
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification click received');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  } else if (event.action === 'close') {
    // Just close the notification
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.matchAll().then(clientList => {
        if (clientList.length > 0) {
          return clientList[0].focus();
        }
        return clients.openWindow('/');
      })
    );
  }
});

// Message handling
self.addEventListener('message', event => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_VERSION });
  }
});

// Utility functions
async function getStoredData(key) {
  try {
    const cache = await caches.open('data-cache');
    const response = await cache.match(key);
    if (response) {
      return await response.json();
    }
  } catch (error) {
    console.error('[SW] Failed to get stored data:', error);
  }
  return null;
}

async function removeFromPendingSync(id) {
  try {
    const pendingData = await getStoredData('pending-sync') || [];
    const updatedData = pendingData.filter(item => item.id !== id);
    
    const cache = await caches.open('data-cache');
    await cache.put('pending-sync', new Response(JSON.stringify(updatedData)));
  } catch (error) {
    console.error('[SW] Failed to remove from pending sync:', error);
  }
}

// Performance monitoring
self.addEventListener('fetch', event => {
  const start = performance.now();
  
  event.respondWith(
    handleFetch(event.request).then(response => {
      const duration = performance.now() - start;
      
      // Log slow requests
      if (duration > 1000) {
        console.warn(`[SW] Slow request: ${event.request.url} took ${duration}ms`);
      }
      
      return response;
    })
  );
});

console.log('[SW] Service Worker v' + CACHE_VERSION + ' loaded');

