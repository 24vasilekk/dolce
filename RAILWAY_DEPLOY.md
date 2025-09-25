# 🚆 Деплой Dolce Deals на Railway

## 🎯 Решение проблемы локального запуска

Если локальный запуск не работает ("локальный запуск не дает работать"), Railway - идеальное решение для деплоя вашего Telegram Mini App.

## 📋 Подготовка к деплою

### 1. Создайте аккаунт Railway
- Идите на [railway.app](https://railway.app)
- Войдите через GitHub
- Подключите свой GitHub репозиторий

### 2. Загрузите проект в GitHub
```bash
cd /Users/filippakinitov/Desktop/EcommerceParser
git init
git add .
git commit -m "Initial Dolce x BestSecret integration"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dolce-deals.git
git push -u origin main
```

## 🚀 Деплой на Railway

### 1. Создайте новый проект
1. На Railway нажмите **"New Project"**
2. Выберите **"Deploy from GitHub repo"**
3. Выберите ваш репозиторий с Dolce Deals

### 2. Настройте Railway конфигурацию

Создайте файл `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python3 dolce_api_server.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. Создайте требования для Railway

Создайте `requirements.txt`:
```txt
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
selenium==4.15.2
beautifulsoup4==4.12.2
gunicorn==21.2.0
```

### 4. Обновите API сервер для Railway

Создайте `dolce_api_server_railway.py`:
```python
#!/usr/bin/env python3
"""
Railway версия Dolce API Server
"""
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Получаем порт от Railway
PORT = int(os.environ.get('PORT', 5001))

class DataConverter:
    def __init__(self):
        self.brand_mapping = {
            'Off-White': 'Off-White',
            'Canada Goose': 'Canada Goose', 
            'Gucci': 'Gucci',
            'See by Chloé': 'Chloé'
        }
        
        self.category_mapping = {
            'shoes': 'Обувь',
            'clothing': 'Одежда',
            'sneakers': 'Кроссовки',
            'boots': 'Ботинки'
        }

    def convert_bestsecret_to_dolce(self, bestsecret_products):
        """Конвертация данных BestSecret в формат Dolce"""
        dolce_products = []
        
        for product in bestsecret_products:
            dolce_product = {
                "id": product.get('id', f"product_{len(dolce_products) + 1}"),
                "name": product.get('name', 'Unknown Product'),
                "brand": self.brand_mapping.get(product.get('brand', 'Unknown'), product.get('brand', 'Unknown')),
                "price": int(float(product.get('current_price', '0').replace('€', '').replace(',', '.').strip()) * 100),
                "originalPrice": int(float(product.get('original_price', '0').replace('€', '').replace(',', '.').strip()) * 100),
                "discount": product.get('discount_percentage', '0%'),
                "category": self.category_mapping.get(product.get('category', 'clothing').lower(), 'Одежда'),
                "color": product.get('color', 'Разноцветный'),
                "sizes": product.get('available_sizes', []),
                "image": product.get('image_url', ''),
                "description": f"{product.get('brand', 'Brand')} {product.get('name', 'Product')}",
                "inStock": len(product.get('available_sizes', [])) > 0
            }
            dolce_products.append(dolce_product)
        
        return dolce_products

# Инициализация
converter = DataConverter()

def load_products():
    """Загрузка товаров из базы данных"""
    try:
        with open('products_database.json', 'r', encoding='utf-8') as f:
            bestsecret_data = json.load(f)
        
        # Конвертируем в формат Dolce
        dolce_products = converter.convert_bestsecret_to_dolce(bestsecret_data.get('products', []))
        
        return dolce_products
    except Exception as e:
        print(f"Ошибка загрузки товаров: {e}")
        return []

@app.route('/api/health')
def health_check():
    """Health check для Railway"""
    return jsonify({
        "status": "healthy",
        "service": "dolce-api",
        "version": "1.0.0"
    })

@app.route('/api/products')
def get_products():
    """Получить все товары"""
    try:
        products = load_products()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Получить статистику товаров"""
    try:
        products = load_products()
        
        stats = {
            "total_products": len(products),
            "brands": list(set(p['brand'] for p in products)),
            "categories": list(set(p['category'] for p in products)),
            "avg_price": int(sum(p['price'] for p in products) / len(products)) if products else 0,
            "in_stock": len([p for p in products if p['inStock']])
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
```

### 5. Обновите приложение для Railway

Обновите `dolce/app_with_api.js` для работы с Railway:
```javascript
// В начале файла добавьте проверку домена
const isDevelopment = window.location.hostname === 'localhost';
const railwayDomain = 'YOUR_RAILWAY_DOMAIN'; // Замените после деплоя

// Обновите apiBaseUrl
this.apiBaseUrl = isDevelopment 
    ? 'http://localhost:5001/api'
    : `https://${railwayDomain}/api`;
```

## 🔧 Настройка переменных окружения

В Railway проекте добавьте переменные:
- `FLASK_ENV=production`
- `PYTHONPATH=/app`

## 📱 Настройка для Telegram Mini App

### 1. Создайте `index.html` для Railway
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dolce Deals</title>
    
    <!-- Telegram WebApp -->
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    
    <!-- PWA метаданные -->
    <meta name="theme-color" content="#4a90e2">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    
    <!-- Стили -->
    <link rel="stylesheet" href="dolce/styles.css">
</head>
<body>
    <div id="app-container">
        <!-- Dolce Deals App будет загружен здесь -->
    </div>
    
    <!-- Скрипты -->
    <script src="dolce/app_with_api.js"></script>
    
    <script>
        // Инициализация Telegram WebApp
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();
            
            // Настройка темы
            document.body.style.backgroundColor = tg.themeParams.bg_color || '#ffffff';
        }
        
        // Запуск приложения
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof FashionApp !== 'undefined') {
                const app = new FashionApp();
                window.app = app;
            }
        });
    </script>
</body>
</html>
```

## 🚀 Деплой процесс

### 1. Запуск деплоя
После push в GitHub, Railway автоматически:
1. Обнаружит изменения
2. Соберет приложение  
3. Запустит ваш API сервер
4. Выдаст публичный URL

### 2. Получение домена
После деплоя Railway выдаст домен типа:
`https://dolce-deals-production-xxxx.up.railway.app`

### 3. Обновите приложение
```bash
# Обновите домен в app_with_api.js
sed -i 's/YOUR_RAILWAY_DOMAIN/dolce-deals-production-xxxx.up.railway.app/g' dolce/app_with_api.js

# Закоммитьте изменения
git add dolce/app_with_api.js
git commit -m "Update Railway domain"
git push
```

## 📱 Настройка Telegram Bot

### 1. Идите к @BotFather
```
/setmenubutton
@your_bot_username
Button text: 🛍️ Открыть магазин
Web App URL: https://YOUR_RAILWAY_DOMAIN
```

### 2. Настройте команды
```
/setcommands
@your_bot_username

start - 🚀 Открыть магазин Dolce Deals
shop - 🛍️ Каталог товаров
help - ❓ Помощь и поддержка
```

## 🔍 Проверка работы

### 1. Тест API
```bash
curl https://YOUR_RAILWAY_DOMAIN/api/health
curl https://YOUR_RAILWAY_DOMAIN/api/products
```

### 2. Тест в Telegram
1. Найдите ваш бот
2. Нажмите `/start`
3. Нажмите кнопку меню
4. Приложение откроется с товарами

## 🛠️ Отладка проблем

### Логи Railway
```
# В Railway консоли смотрите:
railway logs --follow
```

### Частые проблемы:
1. **500 ошибка**: Проверьте requirements.txt
2. **CORS ошибки**: Убедитесь что Flask-CORS установлен
3. **Файлы не найдены**: Загрузите products_database.json

## 📊 Мониторинг

Railway предоставляет:
- ✅ Автоматические health checks
- ✅ Метрики производительности  
- ✅ Логи в реальном времени
- ✅ Автоматические перезапуски при сбоях

## 🎉 Результат

После успешного деплоя:
- ✅ Приложение работает 24/7 на Railway
- ✅ Доступно как Telegram Mini App
- ✅ Автоматические обновления при push
- ✅ HTTPS из коробки
- ✅ Мониторинг и логи

**Ваш Dolce Deals теперь работает в продакшене!** 🚀