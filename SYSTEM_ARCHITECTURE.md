# 🏗️ Dolce Deals - Архитектура системы с админкой

## 🎯 Общая архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │    Admin Panel   │    │  BestSecret     │
│   Mini App      │    │   (Web Admin)    │    │   Parser        │
│                 │    │                  │    │                 │
│  - Каталог      │    │ - Управление     │    │ - Парсинг       │
│  - Поиск        │    │ - Мониторинг     │    │ - Размеры       │
│  - Избранное    │    │ - Статистика     │    │ - Изображения   │
└─────────┬───────┘    └──────────┬───────┘    └─────────┬───────┘
          │                       │                      │
          │                       │                      │
          └───────────────────────┼──────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      Flask API Server     │
                    │                           │
                    │ /api/* - Public API       │
                    │ /admin/* - Admin API      │
                    │ /parser/* - Parser API    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     PostgreSQL DB        │
                    │                          │
                    │ - products               │
                    │ - admins                │
                    │ - parsing_logs          │
                    │ - user_favorites        │
                    └──────────────────────────┘
```

## 📊 Структура базы данных

### **Таблица: products**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(100),
    price DECIMAL(10,2),
    original_price DECIMAL(10,2),
    discount_percentage INTEGER,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    gender ENUM('men', 'women', 'kids', 'unisex'),
    sizes JSONB DEFAULT '[]',
    colors JSONB DEFAULT '[]',
    materials JSONB DEFAULT '[]',
    images JSONB DEFAULT '[]',
    description TEXT,
    status ENUM('active', 'inactive', 'out_of_stock') DEFAULT 'active',
    source VARCHAR(50) DEFAULT 'manual',
    source_url TEXT,
    last_parsed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    views_count INTEGER DEFAULT 0,
    favorites_count INTEGER DEFAULT 0
);
```

### **Таблица: admins**
```sql
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('super_admin', 'admin', 'moderator') DEFAULT 'admin',
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Таблица: parsing_logs**
```sql
CREATE TABLE parsing_logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50),
    status ENUM('running', 'completed', 'failed'),
    products_found INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_added INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]',
    settings JSONB DEFAULT '{}',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    admin_id INTEGER REFERENCES admins(id)
);
```

## 🎛️ Админ-панель функции

### **📈 Dashboard**
- Общая статистика товаров
- График продаж/просмотров 
- Последние логи парсинга
- Быстрые действия

### **🛍️ Управление товарами**
- Список всех товаров с фильтрами
- Редактирование товара
- Массовые операции
- Импорт/экспорт
- Управление категориями

### **🕷️ Парсинг**
- Запуск парсеров
- Настройка источников
- Мониторинг процесса
- История парсинга
- Автоматическое расписание

### **📊 Аналитика**
- Топ товаров
- Статистика по брендам
- Анализ цен и скидок
- Отчеты

### **⚙️ Настройки**
- Управление администраторами
- Настройки парсеров
- API токены
- Уведомления

## 🔧 API Endpoints

### **Публичное API (для приложения):**
```
GET  /api/products                 # Все товары
GET  /api/products/{id}           # Конкретный товар
GET  /api/categories              # Категории
GET  /api/brands                  # Бренды
GET  /api/stats                   # Статистика
POST /api/favorites/{product_id}  # Добавить в избранное
```

### **Админ API:**
```
POST /admin/login                 # Авторизация
GET  /admin/dashboard            # Данные дашборда
GET  /admin/products             # Управление товарами
POST /admin/products             # Создать товар
PUT  /admin/products/{id}        # Обновить товар
DELETE /admin/products/{id}      # Удалить товар
POST /admin/parsing/start        # Запустить парсер
GET  /admin/parsing/logs         # Логи парсинга
GET  /admin/analytics           # Аналитика
```

## 🚀 Развертывание

### **Development (локально):**
```bash
# База данных
docker-compose up -d postgres

# API сервер
python admin_api_server.py

# Админка (фронтенд)
cd admin-panel && npm run dev

# Dolce приложение
python start_dolce_system.py
```

### **Production (Railway):**
```bash
# Автоматический деплой через GitHub
# PostgreSQL плагин Railway
# Environment variables
```

## 📱 Мобильные приложения

### **Telegram Mini App:**
- Основное приложение для пользователей
- Каталог товаров
- Избранное
- Поиск и фильтры

### **Admin Mobile (опционально):**
- Мобильная версия админки
- Push уведомления о парсинге
- Быстрое управление товарами

## 🔐 Безопасность

### **Аутентификация:**
- JWT токены для админов
- Rate limiting для API
- HTTPS только

### **Авторизация:**
- Роли: super_admin, admin, moderator
- Права доступа на уровне API
- Логирование всех действий

## 🎯 Этапы разработки

### **Этап 1: База данных и миграции**
### **Этап 2: Расширенный API сервер**
### **Этап 3: Админ-панель (бэкенд)**
### **Этап 4: Админ-панель (фронтенд)**
### **Этап 5: Интеграция парсера**
### **Этап 6: Деплой и тестирование**

---

**🎉 Результат: Полноценная e-commerce платформа с админкой!**