#!/usr/bin/env python3
"""
Railway версия Dolce API Server для деплоя на railway.app
Оптимизировано для работы в продакшене с Telegram Mini App
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
            'boots': 'Ботинки',
            'пальто': 'Одежда',
            'рубашка': 'Одежда'
        }

    def convert_bestsecret_to_dolce(self, bestsecret_products):
        """Конвертация данных BestSecret в формат Dolce"""
        dolce_products = []
        
        for i, product in enumerate(bestsecret_products):
            # Парсим цену
            current_price_str = str(product.get('current_price', '0')).replace('€', '').replace(',', '.').strip()
            original_price_str = str(product.get('original_price', '0')).replace('€', '').replace(',', '.').strip()
            
            try:
                current_price = int(float(current_price_str) * 100)  # Конвертируем EUR в RUB (1:100)
            except:
                current_price = 0
            
            try:
                original_price = int(float(original_price_str) * 100)
            except:
                original_price = current_price
            
            dolce_product = {
                "id": product.get('id', f"product_{i + 1}"),
                "name": product.get('name', 'Unknown Product'),
                "brand": self.brand_mapping.get(product.get('brand', 'Unknown'), product.get('brand', 'Unknown')),
                "price": current_price,
                "originalPrice": original_price,
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
        # Проверяем наличие файла
        if os.path.exists('products_database.json'):
            with open('products_database.json', 'r', encoding='utf-8') as f:
                bestsecret_data = json.load(f)
        else:
            print("Warning: products_database.json не найден, используем демо данные")
            bestsecret_data = {
                "products": [
                    {
                        "id": "demo_1",
                        "name": "Demo Fashion Item",
                        "brand": "Demo Brand",
                        "current_price": "99.99€",
                        "original_price": "199.99€",
                        "discount_percentage": "50%",
                        "category": "clothing",
                        "color": "Black",
                        "available_sizes": ["M", "L", "XL"],
                        "image_url": "https://via.placeholder.com/400x400",
                    }
                ]
            }
        
        # Конвертируем в формат Dolce
        dolce_products = converter.convert_bestsecret_to_dolce(bestsecret_data.get('products', []))
        
        return dolce_products
    except Exception as e:
        print(f"Ошибка загрузки товаров: {e}")
        return []

@app.route('/')
def home():
    """Главная страница - редирект на приложение"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dolce Deals</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
    </head>
    <body style="margin:0;padding:20px;font-family:Arial,sans-serif;background:#f5f5f5;">
        <div style="text-align:center;max-width:400px;margin:50px auto;">
            <h1>🛍️ Dolce Deals</h1>
            <p>Fashion приложение с товарами от премиальных брендов</p>
            <a href="/dolce/" style="background:#4a90e2;color:white;padding:15px 30px;border-radius:10px;text-decoration:none;display:inline-block;">
                Открыть приложение
            </a>
        </div>
        <script>
            // Telegram WebApp автоматический запуск
            if (window.Telegram && window.Telegram.WebApp) {
                setTimeout(() => {
                    window.location.href = '/dolce/';
                }, 1000);
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/health')
def health_check():
    """Health check для Railway"""
    products_count = len(load_products())
    return jsonify({
        "status": "healthy",
        "service": "dolce-api",
        "version": "1.0.0",
        "products_loaded": products_count,
        "railway_deployment": True
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
        
        if not products:
            return jsonify({
                "total_products": 0,
                "brands": [],
                "categories": [],
                "avg_price": 0,
                "in_stock": 0
            })
        
        stats = {
            "total_products": len(products),
            "brands": list(set(p['brand'] for p in products)),
            "categories": list(set(p['category'] for p in products)),
            "avg_price": int(sum(p['price'] for p in products) / len(products)),
            "in_stock": len([p for p in products if p['inStock']]),
            "last_updated": "Railway deployment"
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<product_id>')
def get_product(product_id):
    """Получить конкретный товар"""
    try:
        products = load_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if product:
            return jsonify(product)
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Для Railway/Gunicorn запуск через app объект
if __name__ == '__main__':
    print(f"🚀 Запуск Dolce API Server на порту {PORT}")
    print(f"📊 Загружено товаров: {len(load_products())}")
    print(f"🌐 Health check: /api/health")
    print(f"🛍️ API товары: /api/products")
    
    # Для локального тестирования
    app.run(host='0.0.0.0', port=PORT, debug=False)

# Railway будет использовать app объект через Gunicorn