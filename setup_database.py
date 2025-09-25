#!/usr/bin/env python3
"""
Скрипт для настройки базы данных PostgreSQL для парсера
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Параметры подключения
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': os.getenv('DB_PORT', '5432')
}

DATABASE_NAME = os.getenv('DB_NAME', 'ecommerce_parser')

def create_database():
    """Создание базы данных"""
    try:
        # Подключаемся к PostgreSQL без указания базы данных
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Проверяем, существует ли база данных
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DATABASE_NAME,))
        if cursor.fetchone():
            logging.info(f"База данных '{DATABASE_NAME}' уже существует")
        else:
            # Создаем базу данных
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DATABASE_NAME)))
            logging.info(f"✅ База данных '{DATABASE_NAME}' создана")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logging.error(f"❌ Ошибка создания базы данных: {e}")
        return False

def create_tables():
    """Создание таблиц"""
    try:
        # Подключаемся к созданной базе данных
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DATABASE_NAME,
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        cursor = conn.cursor()
        
        # SQL для создания таблицы продуктов
        create_products_table = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            url VARCHAR(500) UNIQUE NOT NULL,
            site VARCHAR(100),
            sku VARCHAR(100) UNIQUE,
            parsed_at TIMESTAMP,
            
            -- Основная информация
            name TEXT,
            brand VARCHAR(200),
            category VARCHAR(200),
            subcategory VARCHAR(200),
            gender VARCHAR(50),
            color VARCHAR(100),
            description TEXT,
            
            -- Цены и скидки
            current_price DECIMAL(10,2),
            original_price DECIMAL(10,2),
            currency VARCHAR(10),
            discount_amount DECIMAL(10,2),
            discount_percentage DECIMAL(5,2),
            
            -- Размеры и наличие
            available_sizes TEXT[],
            out_of_stock_sizes TEXT[],
            in_stock BOOLEAN,
            stock_level VARCHAR(50),
            
            -- Изображения
            image_urls TEXT[],
            cloud_image_urls TEXT[],
            main_image_url TEXT,
            
            -- Дополнительные поля
            material TEXT,
            season VARCHAR(50),
            collection VARCHAR(200),
            tags TEXT[],
            rating DECIMAL(3,2),
            reviews_count INTEGER,
            
            -- Системные поля
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Создаем таблицу
        cursor.execute(create_products_table)
        
        # Создаем индексы для быстрого поиска
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_products_site ON products(site);",
            "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);",
            "CREATE INDEX IF NOT EXISTS idx_products_gender ON products(gender);",
            "CREATE INDEX IF NOT EXISTS idx_products_parsed_at ON products(parsed_at);",
            "CREATE INDEX IF NOT EXISTS idx_products_price ON products(current_price);",
            "CREATE INDEX IF NOT EXISTS idx_products_in_stock ON products(in_stock);",
            "CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Создаем функцию для автоматического обновления updated_at
        trigger_function = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
        cursor.execute(trigger_function)
        
        # Создаем триггер
        trigger = """
        DROP TRIGGER IF EXISTS update_products_updated_at ON products;
        CREATE TRIGGER update_products_updated_at
            BEFORE UPDATE ON products
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        cursor.execute(trigger)
        
        # Создаем таблицу для логирования парсинга
        create_parsing_log_table = """
        CREATE TABLE IF NOT EXISTS parsing_log (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(100),
            url TEXT,
            status VARCHAR(50),
            error_message TEXT,
            parsing_duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_parsing_log_table)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parsing_log_session ON parsing_log(session_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parsing_log_status ON parsing_log(status);")
        
        # Создаем таблицу для статистики
        create_stats_table = """
        CREATE TABLE IF NOT EXISTS parsing_stats (
            id SERIAL PRIMARY KEY,
            date DATE DEFAULT CURRENT_DATE,
            site VARCHAR(100),
            total_products INTEGER DEFAULT 0,
            successful_parses INTEGER DEFAULT 0,
            failed_parses INTEGER DEFAULT 0,
            avg_price DECIMAL(10,2),
            categories_parsed TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, site)
        );
        """
        cursor.execute(create_stats_table)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info("✅ Таблицы и индексы созданы успешно")
        return True
        
    except Exception as e:
        logging.error(f"❌ Ошибка создания таблиц: {e}")
        return False

def create_sample_queries():
    """Создание файла с примерами SQL запросов"""
    queries = """-- Примеры SQL запросов для анализа данных

-- 1. Общая статистика по товарам
SELECT 
    site,
    COUNT(*) as total_products,
    COUNT(DISTINCT brand) as unique_brands,
    COUNT(DISTINCT category) as unique_categories,
    AVG(current_price) as avg_price,
    MIN(current_price) as min_price,
    MAX(current_price) as max_price
FROM products 
GROUP BY site;

-- 2. Топ-10 брендов по количеству товаров
SELECT 
    brand,
    COUNT(*) as product_count,
    AVG(current_price) as avg_price,
    AVG(discount_percentage) as avg_discount
FROM products 
WHERE brand IS NOT NULL
GROUP BY brand 
ORDER BY product_count DESC 
LIMIT 10;

-- 3. Товары со скидкой больше 50%
SELECT 
    name,
    brand,
    category,
    original_price,
    current_price,
    discount_percentage,
    url
FROM products 
WHERE discount_percentage > 50 
ORDER BY discount_percentage DESC;

-- 4. Анализ по категориям
SELECT 
    category,
    gender,
    COUNT(*) as product_count,
    AVG(current_price) as avg_price,
    COUNT(CASE WHEN in_stock = true THEN 1 END) as in_stock_count
FROM products 
WHERE category IS NOT NULL
GROUP BY category, gender 
ORDER BY product_count DESC;

-- 5. Товары без изображений (нужно исправить)
SELECT 
    name,
    brand,
    url
FROM products 
WHERE cloud_image_urls IS NULL OR array_length(cloud_image_urls, 1) = 0;

-- 6. Статистика парсинга по дням
SELECT 
    DATE(parsed_at) as parse_date,
    COUNT(*) as products_parsed,
    COUNT(DISTINCT site) as sites_parsed,
    AVG(current_price) as avg_price
FROM products 
WHERE parsed_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(parsed_at) 
ORDER BY parse_date DESC;

-- 7. Поиск товаров по ключевым словам
SELECT 
    name,
    brand,
    category,
    current_price,
    url
FROM products 
WHERE 
    LOWER(name) LIKE '%bag%' OR 
    LOWER(description) LIKE '%bag%' OR
    LOWER(category) LIKE '%bag%'
ORDER BY current_price ASC;

-- 8. Товары с лучшими рейтингами
SELECT 
    name,
    brand,
    rating,
    reviews_count,
    current_price,
    url
FROM products 
WHERE rating IS NOT NULL AND reviews_count > 10
ORDER BY rating DESC, reviews_count DESC 
LIMIT 20;

-- 9. Обновление статистики
INSERT INTO parsing_stats (date, site, total_products, successful_parses)
SELECT 
    CURRENT_DATE,
    site,
    COUNT(*),
    COUNT(CASE WHEN name IS NOT NULL AND current_price IS NOT NULL THEN 1 END)
FROM products 
WHERE DATE(parsed_at) = CURRENT_DATE
GROUP BY site
ON CONFLICT (date, site) 
DO UPDATE SET 
    total_products = EXCLUDED.total_products,
    successful_parses = EXCLUDED.successful_parses;

-- 10. Очистка старых данных (старше 90 дней)
DELETE FROM products 
WHERE parsed_at < CURRENT_DATE - INTERVAL '90 days';
"""
    
    with open('/Users/filippakinitov/Desktop/EcommerceParser/sample_queries.sql', 'w', encoding='utf-8') as f:
        f.write(queries)
    
    logging.info("✅ Файл с примерами SQL запросов создан: sample_queries.sql")

def test_connection():
    """Тестирование подключения"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DATABASE_NAME,
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        cursor = conn.cursor()
        
        # Тестируем вставку данных
        test_insert = """
        INSERT INTO products (url, site, sku, name, brand, current_price, currency)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        """
        
        cursor.execute(test_insert, (
            'https://test.com/test-product',
            'TestSite',
            'TEST-001',
            'Test Product',
            'Test Brand',
            99.99,
            'EUR'
        ))
        
        # Проверяем, что данные вставились
        cursor.execute("SELECT COUNT(*) FROM products WHERE url = %s", ('https://test.com/test-product',))
        count = cursor.fetchone()[0]
        
        if count > 0:
            logging.info("✅ Тестовая запись успешно создана")
            
            # Удаляем тестовую запись
            cursor.execute("DELETE FROM products WHERE url = %s", ('https://test.com/test-product',))
            logging.info("✅ Тестовая запись удалена")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info("✅ Подключение к базе данных работает корректно")
        return True
        
    except Exception as e:
        logging.error(f"❌ Ошибка тестирования подключения: {e}")
        return False

def main():
    """Главная функция настройки"""
    print("🚀 Настройка базы данных для Enhanced Parser")
    print("=" * 50)
    
    try:
        # Создаем базу данных
        if not create_database():
            print("❌ Не удалось создать базу данных")
            sys.exit(1)
        
        # Создаем таблицы
        if not create_tables():
            print("❌ Не удалось создать таблицы")
            sys.exit(1)
        
        # Тестируем подключение
        if not test_connection():
            print("❌ Подключение не работает")
            sys.exit(1)
        
        # Создаем примеры запросов
        create_sample_queries()
        
        print("\n" + "=" * 50)
        print("✅ БАЗА ДАННЫХ УСПЕШНО НАСТРОЕНА!")
        print("=" * 50)
        print(f"📊 База данных: {DATABASE_NAME}")
        print(f"🏠 Хост: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"👤 Пользователь: {DB_CONFIG['user']}")
        print("\n📝 Созданные таблицы:")
        print("  - products (основные данные товаров)")
        print("  - parsing_log (логи парсинга)")
        print("  - parsing_stats (статистика)")
        print("\n📁 Файлы:")
        print("  - sample_queries.sql (примеры запросов)")
        print("\n🚀 Теперь можно запускать enhanced_parser.py!")
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()