-- 🏗️ Database Schema для Dolce Deals Admin System
-- PostgreSQL Schema для управления товарами и администраторами

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание ENUM типов
CREATE TYPE product_status AS ENUM ('active', 'inactive', 'out_of_stock', 'pending');
CREATE TYPE product_gender AS ENUM ('men', 'women', 'kids', 'unisex');
CREATE TYPE admin_role AS ENUM ('super_admin', 'admin', 'moderator');
CREATE TYPE parsing_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');

-- 1. Таблица товаров
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    sku VARCHAR(100) UNIQUE NOT NULL,
    
    -- Основная информация
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(100),
    description TEXT,
    
    -- Цены и скидки
    price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    discount_percentage INTEGER DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'RUB',
    
    -- Категоризация
    category VARCHAR(100),
    subcategory VARCHAR(100),
    gender product_gender DEFAULT 'unisex',
    
    -- Характеристики (JSON для гибкости)
    sizes JSONB DEFAULT '[]',           -- ["XS", "S", "M", "L"]
    colors JSONB DEFAULT '[]',          -- ["black", "white"]
    materials JSONB DEFAULT '[]',       -- ["cotton", "polyester"]
    images JSONB DEFAULT '[]',          -- [{"url": "...", "alt": "..."}]
    attributes JSONB DEFAULT '{}',      -- Дополнительные атрибуты
    
    -- Статус и доступность
    status product_status DEFAULT 'active',
    is_featured BOOLEAN DEFAULT false,
    stock_quantity INTEGER DEFAULT 0,
    
    -- Источник данных
    source VARCHAR(50) DEFAULT 'manual',        -- 'bestsecret', 'manual', 'import'
    source_url TEXT,
    source_data JSONB DEFAULT '{}',             -- Дополнительные данные от парсера
    
    -- Статистика
    views_count INTEGER DEFAULT 0,
    favorites_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    
    -- Временные метки
    last_parsed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Таблица администраторов
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    
    -- Аутентификация
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Личная информация
    full_name VARCHAR(100),
    avatar_url TEXT,
    
    -- Права доступа
    role admin_role DEFAULT 'admin',
    permissions JSONB DEFAULT '[]',     -- ["products.edit", "parsing.run"]
    is_active BOOLEAN DEFAULT true,
    
    -- Сессии и безопасность
    last_login_at TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    
    -- API токены
    api_token VARCHAR(255) UNIQUE,
    api_token_expires_at TIMESTAMP,
    
    -- Временные метки
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Логи парсинга
CREATE TABLE parsing_logs (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    
    -- Основная информация
    source VARCHAR(50) NOT NULL,           -- 'bestsecret', 'farfetch'
    status parsing_status DEFAULT 'pending',
    
    -- Конфигурация парсинга
    settings JSONB DEFAULT '{}',           -- Настройки парсера
    filters JSONB DEFAULT '{}',            -- Примененные фильтры
    
    -- Результаты
    products_found INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_added INTEGER DEFAULT 0,
    products_failed INTEGER DEFAULT 0,
    
    -- Ошибки и предупреждения
    errors JSONB DEFAULT '[]',
    warnings JSONB DEFAULT '[]',
    
    -- Производительность
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Администратор, запустивший парсинг
    admin_id INTEGER REFERENCES admins(id),
    
    -- Дополнительные данные
    metadata JSONB DEFAULT '{}'
);

-- 4. Избранные товары пользователей (для будущего функционала)
CREATE TABLE user_favorites (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,        -- Telegram user_id или другой ID
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, product_id)
);

-- 5. Категории (для структурированного управления)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    gender product_gender,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Бренды
CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    logo_url TEXT,
    website_url TEXT,
    is_premium BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Системные настройки
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB,
    description TEXT,
    updated_by INTEGER REFERENCES admins(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для производительности
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_category ON products(category, gender);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_source ON products(source);

CREATE INDEX idx_admins_username ON admins(username);
CREATE INDEX idx_admins_email ON admins(email);
CREATE INDEX idx_admins_role ON admins(role);
CREATE INDEX idx_admins_is_active ON admins(is_active);

CREATE INDEX idx_parsing_logs_status ON parsing_logs(status);
CREATE INDEX idx_parsing_logs_source ON parsing_logs(source);
CREATE INDEX idx_parsing_logs_started_at ON parsing_logs(started_at DESC);

CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX idx_user_favorites_product_id ON user_favorites(product_id);

-- Триггеры для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON products 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admins_updated_at 
    BEFORE UPDATE ON admins 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Вставка начальных данных

-- Создание суперадмина (пароль: admin123)
INSERT INTO admins (username, email, password_hash, full_name, role) 
VALUES (
    'admin', 
    'admin@dolcedeals.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeshilaHtwhWmgOdrjM1H3.E2', -- admin123
    'System Administrator', 
    'super_admin'
);

-- Базовые категории
INSERT INTO categories (name, slug, gender, sort_order) VALUES
('Одежда', 'clothing', 'unisex', 1),
('Обувь', 'shoes', 'unisex', 2),
('Сумки', 'bags', 'unisex', 3),
('Аксессуары', 'accessories', 'unisex', 4),
('Бьюти', 'beauty', 'unisex', 5),
('Украшения', 'jewelry', 'unisex', 6);

-- Премиальные бренды
INSERT INTO brands (name, slug, is_premium, sort_order) VALUES
('Gucci', 'gucci', true, 1),
('Off-White', 'off-white', true, 2),
('Canada Goose', 'canada-goose', true, 3),
('See by Chloé', 'see-by-chloe', true, 4);

-- Системные настройки
INSERT INTO system_settings (key, value, description) VALUES
('parsing_enabled', 'true', 'Включен ли автоматический парсинг'),
('max_products_per_parse', '100', 'Максимальное количество товаров за один парсинг'),
('notification_email', '"admin@dolcedeals.com"', 'Email для уведомлений системы'),
('currency_rate_eur_rub', '100', 'Курс EUR к RUB для конвертации цен');

-- Комментарии к таблицам
COMMENT ON TABLE products IS 'Таблица товаров с поддержкой парсинга и админки';
COMMENT ON TABLE admins IS 'Администраторы системы с ролевой моделью';
COMMENT ON TABLE parsing_logs IS 'Логи работы парсеров для мониторинга';
COMMENT ON TABLE user_favorites IS 'Избранные товары пользователей';
COMMENT ON TABLE categories IS 'Иерархические категории товаров';
COMMENT ON TABLE brands IS 'Справочник брендов';
COMMENT ON TABLE system_settings IS 'Системные настройки в JSON формате';