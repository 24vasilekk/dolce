// Dolce Deals Fashion App - Версия с API интеграцией
class FashionAppWithAPI extends FashionApp {
    constructor() {
        super();
        // Определяем базовый URL API в зависимости от окружения
        this.apiBaseUrl = window.location.hostname === 'localhost' 
            ? 'http://localhost:5001/api'
            : `${window.location.protocol}//${window.location.host}/api`;
        this.fallbackToLocalData = true;
        this.lastSyncTime = null;
    }

    // Переопределяем метод загрузки товаров для работы с API
    async loadProducts() {
        try {
            console.log('🔄 Загрузка товаров из API...');
            
            // Пробуем загрузить из API
            const apiProducts = await this.loadFromAPI();
            if (apiProducts && apiProducts.length > 0) {
                this.products = apiProducts;
                this.lastSyncTime = new Date().toISOString();
                console.log(`✅ Загружено ${this.products.length} товаров из API`);
                
                // Сохраняем в localStorage как кэш
                this.cacheProducts(this.products);
                return;
            }
            
            // Если API недоступно, пробуем кэш
            if (this.fallbackToLocalData) {
                console.log('⚠️ API недоступно, загружаем из кэша...');
                const cachedProducts = this.loadFromCache();
                
                if (cachedProducts && cachedProducts.length > 0) {
                    this.products = cachedProducts;
                    console.log(`📦 Загружено ${this.products.length} товаров из кэша`);
                    this.showOfflineNotification();
                    return;
                }
            }
            
            // Если ничего не помогло, загружаем статичный JSON
            console.log('📄 Загрузка товаров из статичного JSON...');
            await this.loadFromStaticJSON();
            
        } catch (error) {
            console.error('❌ Критическая ошибка загрузки товаров:', error);
            // В крайнем случае используем тестовые данные
            this.products = this.getExampleProducts();
        }
    }

    async loadFromAPI() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/products`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Timeout для API запроса
                signal: AbortSignal.timeout(10000) // 10 секунд
            });

            if (!response.ok) {
                throw new Error(`API ошибка: ${response.status} ${response.statusText}`);
            }

            const products = await response.json();
            
            // Валидируем структуру данных
            if (Array.isArray(products) && products.length > 0) {
                return this.validateAndProcessProducts(products);
            }
            
            return null;
        } catch (error) {
            console.error('Ошибка загрузки из API:', error);
            return null;
        }
    }

    validateAndProcessProducts(products) {
        return products.filter(product => {
            // Проверяем обязательные поля
            return product.id && 
                   product.name && 
                   product.brand && 
                   product.price && 
                   product.gender && 
                   product.category;
        }).map(product => {
            // Обеспечиваем совместимость с форматом приложения
            return {
                ...product,
                colors: product.colors || ['black'],
                sizes: product.sizes || ['M'],
                materials: product.materials || ['Текстиль'],
                onSale: product.onSale || false,
                description: product.description || ''
            };
        });
    }

    async loadFromStaticJSON() {
        try {
            const response = await fetch('data/products.json');
            if (!response.ok) {
                throw new Error('Не удалось загрузить товары из JSON');
            }
            this.products = await response.json();
            console.log('📄 Загружено товаров из JSON:', this.products.length);
        } catch (error) {
            console.error('Ошибка загрузки из JSON:', error);
            this.products = this.getExampleProducts();
        }
    }

    // Кэширование товаров в localStorage
    cacheProducts(products) {
        try {
            const cacheData = {
                products: products,
                timestamp: new Date().toISOString(),
                version: '1.0.0'
            };
            localStorage.setItem('dolce_products_cache', JSON.stringify(cacheData));
        } catch (error) {
            console.error('Ошибка сохранения кэша:', error);
        }
    }

    loadFromCache() {
        try {
            const cached = localStorage.getItem('dolce_products_cache');
            if (!cached) return null;

            const cacheData = JSON.parse(cached);
            
            // Проверяем возраст кэша (не старше 24 часов)
            const cacheAge = new Date() - new Date(cacheData.timestamp);
            const maxAge = 24 * 60 * 60 * 1000; // 24 часа в миллисекундах
            
            if (cacheAge > maxAge) {
                console.log('🕐 Кэш устарел, очищаем');
                localStorage.removeItem('dolce_products_cache');
                return null;
            }

            return cacheData.products;
        } catch (error) {
            console.error('Ошибка загрузки кэша:', error);
            return null;
        }
    }

    // API методы для различных операций
    async getProductsByGender(gender) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/products?gender=${gender}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error(`Ошибка получения товаров для ${gender}:`, error);
        }
        
        // Fallback к локальным данным
        return this.products.filter(p => p.gender === gender);
    }

    async getProductsByCategory(category) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/products?category=${category}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error(`Ошибка получения товаров категории ${category}:`, error);
        }
        
        // Fallback к локальным данным
        return this.products.filter(p => p.category === category);
    }

    async getAPIStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/stats`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Ошибка получения статистики:', error);
        }
        
        return null;
    }

    // Уведомления для пользователя
    showOfflineNotification() {
        const notification = document.createElement('div');
        notification.className = 'offline-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span>📶 Режим оффлайн</span>
                <small>Показаны кэшированные товары</small>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматически скрываем уведомление через 3 секунды
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    showSyncNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'sync-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span>🔄 ${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 2000);
    }

    // Метод для принудительной синхронизации
    async forceSyncFromAPI() {
        this.showSyncNotification('Синхронизация товаров...');
        
        try {
            const apiProducts = await this.loadFromAPI();
            if (apiProducts && apiProducts.length > 0) {
                this.products = apiProducts;
                this.filteredProducts = [...this.products];
                this.lastSyncTime = new Date().toISOString();
                this.cacheProducts(this.products);
                
                // Обновляем отображение
                this.applyFilters();
                this.showSyncNotification('✅ Товары обновлены!');
                
                return true;
            } else {
                this.showSyncNotification('⚠️ API недоступно');
                return false;
            }
        } catch (error) {
            console.error('Ошибка принудительной синхронизации:', error);
            this.showSyncNotification('❌ Ошибка синхронизации');
            return false;
        }
    }

    // Переопределяем setup для добавления новых функций
    setupEventListeners() {
        // Вызываем родительский метод
        super.setupEventListeners();
        
        // Добавляем обработчик для кнопки синхронизации
        const syncBtn = document.getElementById('syncButton');
        if (syncBtn) {
            syncBtn.addEventListener('click', () => this.forceSyncFromAPI());
        }
        
        // Автоматическая синхронизация при восстановлении соединения
        window.addEventListener('online', () => {
            console.log('🌐 Соединение восстановлено');
            setTimeout(() => this.forceSyncFromAPI(), 1000);
        });
        
        window.addEventListener('offline', () => {
            console.log('📵 Соединение потеряно');
            this.showOfflineNotification();
        });
    }

    // Метод для отображения статистики API
    async displayAPIStats() {
        const stats = await this.getAPIStats();
        if (!stats) return;

        const statsContainer = document.getElementById('apiStats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="api-stats">
                    <h3>📊 Статистика товаров</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-number">${stats.total_products}</span>
                            <span class="stat-label">Всего товаров</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${stats.with_discount}</span>
                            <span class="stat-label">Со скидкой</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${Math.round(stats.avg_price / 100)} ₽</span>
                            <span class="stat-label">Средняя цена</span>
                        </div>
                    </div>
                    <div class="gender-stats">
                        ${Object.entries(stats.by_gender).map(([gender, count]) => 
                            `<span class="gender-stat">${this.getGenderName(gender)}: ${count}</span>`
                        ).join(' • ')}
                    </div>
                    <div class="sync-info">
                        <small>Последнее обновление: ${this.formatSyncTime()}</small>
                    </div>
                </div>
            `;
        }
    }

    getGenderName(gender) {
        const names = {
            'men': 'Мужское',
            'women': 'Женское', 
            'kids': 'Детское'
        };
        return names[gender] || gender;
    }

    formatSyncTime() {
        if (!this.lastSyncTime) return 'Никогда';
        
        const syncDate = new Date(this.lastSyncTime);
        const now = new Date();
        const diffMs = now - syncDate;
        const diffMins = Math.round(diffMs / (1000 * 60));
        
        if (diffMins < 1) return 'Только что';
        if (diffMins < 60) return `${diffMins} мин назад`;
        
        const diffHours = Math.round(diffMins / 60);
        if (diffHours < 24) return `${diffHours} ч назад`;
        
        return syncDate.toLocaleDateString();
    }

    // Переопределяем init для показа статистики
    async init() {
        await super.init();
        
        // Показываем статистику API если доступна
        setTimeout(() => this.displayAPIStats(), 1000);
    }
}

// Создаем глобальный экземпляр приложения с API
let app;

// Инициализация при загрузке документа
document.addEventListener('DOMContentLoaded', () => {
    try {
        app = new FashionAppWithAPI();
        console.log('🚀 Dolce Deals Fashion App с API запущено!');
    } catch (error) {
        console.error('❌ Ошибка запуска приложения:', error);
        // Fallback к обычной версии
        app = new FashionApp();
    }
});

// Экспортируем для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FashionAppWithAPI;
}