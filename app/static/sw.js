// Service Worker para AgroTech - Agente Agrícola
// Versão: 2.0 - CACHE BUSTING ATIVO
// Funcionalidades: Cache versioning automático, invalidação forçada

const CACHE_VERSION = Date.now(); // Timestamp dinâmico para cache busting
const CACHE_NAME = `agrotech-v2-${CACHE_VERSION}`;

// Lista de recursos essenciais para cache (apenas recursos que sabemos que existem)
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/js/alerts-manager.js',
    '/static/js/dashboard-auto-refresh.js',
    '/static/favicon.ico'
    // Removido app.js e style.css que podem não existir
];

// Instalação do Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker: Instalando v2.0 com cache busting...', CACHE_VERSION);
    
    // FORÇA ATIVAÇÃO IMEDIATA - Skip waiting
    self.skipWaiting();
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Service Worker: Cache aberto', CACHE_NAME);
                
                // Cache recursos um por um para evitar falha total
                return Promise.allSettled(
                    urlsToCache.map(url => {
                        return cache.add(url).catch(error => {
                            console.warn('Service Worker: Falha ao cachear:', url, error);
                            return null; // Continue mesmo se um recurso falhar
                        });
                    })
                );
            })
            .then((results) => {
                console.log('Service Worker: Cache concluído com', results.filter(r => r.status === 'fulfilled').length, 'sucessos');
            })
            .catch(error => {
                console.error('Service Worker: Erro geral no cache:', error);
                // NÃO FALHA - continua a instalação mesmo com erros de cache
            })
    );
});

// Ativação do Service Worker
self.addEventListener('activate', event => {
    console.log('Service Worker: Ativando v2.0 com limpeza forçada...', CACHE_VERSION);
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    // REMOVE TODOS os caches anteriores - força invalidação completa
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Removendo cache antigo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker: Ativado e assumindo controle FORÇADO');
            // FORÇA controle imediato de todas as abas
            return self.clients.claim();
        })
    );
});

// Interceptar requisições
self.addEventListener('fetch', event => {
    // Apenas interceptar requisições GET
    if (event.request.method !== 'GET') {
        return;
    }

    const url = new URL(event.request.url);
    
    // CORREÇÃO CSP: Não interceptar recursos externos que violam CSP
    // Permitir apenas recursos do próprio domínio e APIs autorizadas
    if (url.origin !== self.location.origin && 
        !url.hostname.includes('openweathermap.org')) {
        // Deixar o browser lidar com recursos externos
        return;
    }

    // Evitar cache de APIs dinâmicas, autenticação E WIZARD
    if (event.request.url.includes('/api/') || 
        event.request.url.includes('/auth/') ||
        event.request.url.includes('clima') ||
        event.request.url.includes('login') ||
        event.request.url.includes('register') ||
        event.request.url.includes('wizard') ||
        event.request.url.includes('cultures/wizard')) {
        // BYPASS COMPLETO para wizard e APIs dinâmicas
        console.log('Service Worker: BYPASS para:', event.request.url);
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Retorna do cache se existir
                if (response) {
                    return response;
                }

                // Senão, busca na rede
                return fetch(event.request).then(response => {
                    // Verifica se a resposta é válida
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clona a resposta
                    const responseToCache = response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                }).catch(() => {
                    // Em caso de erro de rede, retornar do cache se disponível
                    return caches.match(event.request);
                });
            })
            .catch(() => {
                // Fallback para página offline (opcional)
                if (event.request.destination === 'document') {
                    return caches.match('/');
                }
            })
    );
});

// Manipular notificações push (futuro)
self.addEventListener('push', event => {
    console.log('Service Worker: Notificação push recebida');
    
    const options = {
        body: event.data ? event.data.text() : 'Nova atualização disponível',
        icon: '/static/favicon.ico',
        badge: '/static/icons/badge.png',
        tag: 'agrotech-notification',
        requireInteraction: false,
        actions: [
            {
                action: 'view',
                title: 'Ver detalhes'
            },
            {
                action: 'dismiss',
                title: 'Dispensar'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('AgroTech - Agente Agrícola', options)
    );
});

// Manipular cliques em notificações
self.addEventListener('notificationclick', event => {
    console.log('Service Worker: Clique em notificação:', event.action);
    
    event.notification.close();

    if (event.action === 'view') {
        // Abrir a aplicação
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
