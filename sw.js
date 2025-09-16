// Dolce Deals Service Worker
const CACHE_NAME = 'dolce-deals-v1.0.0';
const STATIC_CACHE = 'dolce-deals-static-v1.0.0';
const DYNAMIC_CACHE = 'dolce-deals-dynamic-v1.0.0';
const IMAGE_CACHE = 'dolce-deals-images-v1.0.0';

// Статические файлы для кэширования
const STATIC_FILES = [
    '/',
    '/index.html',
    '/style.css',
    '/app.js',
    '/data/categories.js',
    '/data/products.json',
    '/manifest.json'
];

// Внешние ресурсы
const EXTERNAL_RESOURCES = [
    'https://images.unsplash.com/'
];

// Установка Service Worker
self.addEventListener('install', event => {
    console.log('[SW] Installing...');
    
    event.waitUntil(
        Promise.all([
            // Кэширование статических файлов
            caches.open(STATIC_CACHE).then(cache => {
                console.log('[SW] Caching static files');
                return cache.addAll(STATIC_FILES);
            }),
            
            // Пропустить ожидание
            self.skipWaiting()
        ])
    );
});

// Активация Service Worker
self.addEventListener('activate', event => {
    console.log('[SW] Activating...');
    
    event.waitUntil(
        Promise.all([
            // Очистка старых кэшей
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== IMAGE_CACHE) {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            
            // Принятие управления всеми клиентами
            self.clients.claim()
        ])
    );
});

// Обработка запросов
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Пропуск не-GET запросов
    if (request.method !== 'GET') {
        return;
    }
    
    // Обработка разных типов запросов
    if (isStaticAsset(url)) {
        event.respondWith(handleStaticAsset(request));
    } else if (isImage(url)) {
        event.respondWith(handleImage(request));
    } else if (isAPI(url)) {
        event.respondWith(handleAPI(request));
    } else {
        event.respondWith(handleDynamic(request));
    }
});

// Проверка статических ресурсов
function isStaticAsset(url) {
    return STATIC_FILES.includes(url.pathname) || 
           url.pathname.endsWith('.css') || 
           url.pathname.endsWith('.js') ||
           url.pathname.endsWith('.json');
}

// Проверка изображений
function isImage(url) {
    return url.pathname.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i) ||
           EXTERNAL_RESOURCES.some(domain => url.hostname.includes(domain));
}

// Проверка API запросов
function isAPI(url) {
    return url.pathname.startsWith('/api/');
}

// Обработка статических ресурсов - Cache First
async function handleStaticAsset(request) {
    try {
        const cache = await caches.open(STATIC_CACHE);
        const cached = await cache.match(request);
        
        if (cached) {
            return cached;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            await cache.put(request, networkResponse.clone());
        }
        return networkResponse;
        
    } catch (error) {
        console.error('[SW] Static asset error:', error);
        
        // Возвращаем кэшированную версию при ошибке сети
        const cache = await caches.open(STATIC_CACHE);
        const cached = await cache.match(request);
        if (cached) {
            return cached;
        }
        
        // Возвращаем офлайн страницу для HTML запросов
        if (request.destination === 'document') {
            return createOfflinePage();
        }
        
        throw error;
    }
}

// Обработка изображений - Stale While Revalidate
async function handleImage(request) {
    try {
        const cache = await caches.open(IMAGE_CACHE);
        const cached = await cache.match(request);
        
        // Возвращаем кэш и обновляем в фоне
        if (cached) {
            // Обновление в фоне
            updateImageInBackground(request, cache);
            return cached;
        }
        
        // Если нет в кэше, загружаем из сети
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            await cache.put(request, networkResponse.clone());
        }
        return networkResponse;
        
    } catch (error) {
        console.error('[SW] Image error:', error);
        return createImageFallback();
    }
}

// Обновление изображения в фоне
async function updateImageInBackground(request, cache) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            await cache.put(request, response);
        }
    } catch (error) {
        console.warn('[SW] Background image update failed:', error);
    }
}

// Обработка API запросов - Network First
async function handleAPI(request) {
    try {
        const networkResponse = await fetchWithTimeout(request, 5000);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.warn('[SW] API network failed:', error);
        
        const cache = await caches.open(DYNAMIC_CACHE);
        const cached = await cache.match(request);
        
        if (cached) {
            return cached;
        }
        
        throw error;
    }
}

// Обработка динамических запросов - Network First
async function handleDynamic(request) {
    try {
        const networkResponse = await fetchWithTimeout(request, 3000);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.warn('[SW] Dynamic request failed:', error);
        
        const cache = await caches.open(DYNAMIC_CACHE);
        const cached = await cache.match(request);
        
        if (cached) {
            return cached;
        }
        
        // Для навигационных запросов возвращаем офлайн страницу
        if (request.destination === 'document') {
            return createOfflinePage();
        }
        
        throw error;
    }
}

// Fetch с таймаутом
async function fetchWithTimeout(request, timeout = 5000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(request, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

// Создание офлайн страницы
function createOfflinePage() {
    const html = `
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dolce Deals - Офлайн</title>
        <style>
            body {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #ffffff 0%, #f8f8f8 100%);
                color: #333;
                text-align: center;
                padding: 2rem;
            }
            .offline-icon {
                font-size: 4rem;
                margin-bottom: 2rem;
                opacity: 0.7;
            }
            .offline-title {
                font-size: 2rem;
                font-weight: 300;
                margin-bottom: 1rem;
                letter-spacing: 1px;
            }
            .offline-message {
                font-size: 1.1rem;
                color: #666;
                margin-bottom: 2rem;
                max-width: 400px;
                line-height: 1.5;
            }
            .retry-btn {
                background: #000;
                color: white;
                border: none;
                padding: 1rem 2rem;
                font-size: 1rem;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-weight: 500;
            }
            .retry-btn:hover {
                background: #333;
                transform: translateY(-2px);
            }
            .offline-features {
                margin-top: 3rem;
                padding: 2rem;
                background: rgba(255,255,255,0.8);
                border-radius: 12px;
                max-width: 500px;
            }
            .feature {
                margin: 1rem 0;
                font-size: 0.9rem;
                color: #555;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
        </style>
    </head>
    <body>
        <div class="offline-icon">📱</div>
        <h1 class="offline-title">DOLCE DEALS</h1>
        <p class="offline-message">
            Вы находитесь в автономном режиме, но можете продолжить просматривать кэшированные товары.
        </p>
        <button class="retry-btn" onclick="window.location.reload()">
            Попробовать снова
        </button>
        <div class="offline-features">
            <div class="feature">
                <span>✨</span>
                <span>Кэшированные товары доступны</span>
            </div>
            <div class="feature">
                <span>💕</span>
                <span>Избранное сохранено локально</span>
            </div>
            <div class="feature">
                <span>🔄</span>
                <span>Изменения синхронизируются при подключении</span>
            </div>
        </div>
    </body>
    </html>
    `;
    
    return new Response(html, {
        headers: { 'Content-Type': 'text/html' }
    });
}

// Создание заглушки для изображений
function createImageFallback() {
    const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
        <rect width="400" height="400" fill="#f5f5f5"/>
        <rect x="50" y="150" width="300" height="200" fill="none" stroke="#ddd" stroke-width="2" rx="8"/>
        <circle cx="120" cy="200" r="25" fill="#ddd"/>
        <polygon points="160,280 200,240 240,260 280,220 320,280" fill="#ddd"/>
        <text x="200" y="320" text-anchor="middle" fill="#999" font-family="Arial, sans-serif" font-size="14">
            Изображение недоступно
        </text>
        <text x="200" y="340" text-anchor="middle" fill="#ccc" font-family="Arial, sans-serif" font-size="12">
            Dolce Deals
        </text>
    </svg>
    `;
    
    return new Response(svg, {
        headers: { 'Content-Type': 'image/svg+xml' }
    });
}

// Push уведомления
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    
    let notificationData = {
        title: 'Dolce Deals',
        body: 'Новые товары в каталоге!',
        icon: '/icon-192x192.png',
        badge: '/icon-96x96.png',
        tag: 'dolce-deals-notification',
        data: {
            url: '/'
        }
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = { ...notificationData, ...data };
        } catch (error) {
            notificationData.body = event.data.text();
        }
    }
    
    event.waitUntil(
        self.registration.showNotification(notificationData.title, notificationData)
    );
});

// Обработка кликов по уведомлениям
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification clicked');
    
    event.notification.close();
    
    const urlToOpen = event.notification.data?.url || '/';
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(clientList => {
                // Проверяем, открыто ли уже приложение
                for (const client of clientList) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // Открываем новое окно
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// Background Sync
self.addEventListener('sync', event => {
    console.log('[SW] Background sync:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

// Синхронизация данных в фоне
async function doBackgroundSync() {
    try {
        console.log('[SW] Performing background sync...');
        // Здесь можно синхронизировать избранное, корзину и другие данные
        
        // Пример: отправка аналитики
        await syncAnalytics();
        
        console.log('[SW] Background sync completed');
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
        throw error;
    }
}

// Синхронизация аналитики
async function syncAnalytics() {
    // Получаем данные из IndexedDB или localStorage
    const analyticsData = await getAnalyticsData();
    
    if (analyticsData && analyticsData.length > 0) {
        try {
            await fetch('/api/analytics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(analyticsData)
            });
            
            // Очищаем отправленные данные
            await clearAnalyticsData();
            
        } catch (error) {
            console.warn('[SW] Analytics sync failed:', error);
        }
    }
}

// Получение данных аналитики (заглушка)
async function getAnalyticsData() {
    // В реальном приложении здесь будет работа с IndexedDB
    return [];
}

// Очистка данных аналитики (заглушка)
async function clearAnalyticsData() {
    // В реальном приложении здесь будет очистка IndexedDB
}

// Обработка сообщений от клиента
self.addEventListener('message', event => {
    console.log('[SW] Message received:', event.data);
    
    const { type, data } = event.data || {};
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_VERSION':
            event.ports[0]?.postMessage({ version: CACHE_NAME });
            break;
            
        case 'CLEAR_CACHE':
            event.waitUntil(clearAllCaches());
            break;
            
        case 'FORCE_UPDATE':
            event.waitUntil(forceUpdate());
            break;
            
        default:
            console.warn('[SW] Unknown message type:', type);
    }
});

// Очистка всех кэшей
async function clearAllCaches() {
    try {
        const cacheNames = await caches.keys();
        await Promise.all(
            cacheNames.map(name => caches.delete(name))
        );
        console.log('[SW] All caches cleared');
    } catch (error) {
        console.error('[SW] Failed to clear caches:', error);
    }
}

// Принудительное обновление
async function forceUpdate() {
    try {
        await clearAllCaches();
        await self.registration.update();
        console.log('[SW] Force update completed');
    } catch (error) {
        console.error('[SW] Force update failed:', error);
    }
}

// Обработка ошибок
self.addEventListener('error', event => {
    console.error('[SW] Error:', event.error);
});

self.addEventListener('unhandledrejection', event => {
    console.error('[SW] Unhandled rejection:', event.reason);
    event.preventDefault();
});

console.log('[SW] Service Worker v1.0.0 loaded');