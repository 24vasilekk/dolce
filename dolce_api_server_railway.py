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
            # Парсим цену - учитываем что может быть float или string
            current_price = product.get('current_price', 0)
            original_price = product.get('original_price', 0)
            
            # Если цена строка, парсим её
            if isinstance(current_price, str):
                current_price = float(current_price.replace('€', '').replace(',', '.').strip())
            if isinstance(original_price, str):
                original_price = float(original_price.replace('€', '').replace(',', '.').strip())
            
            # Конвертируем EUR в RUB (1:100)
            current_price_rub = int(current_price * 100)
            original_price_rub = int(original_price * 100) if original_price else current_price_rub
            
            # Получаем скидку
            discount = product.get('discount_percentage', 0)
            if isinstance(discount, (int, float)):
                discount_str = f"{int(discount)}%"
            else:
                discount_str = str(discount)
            
            # Получаем изображение
            image_url = ""
            if product.get('image_urls') and isinstance(product['image_urls'], list):
                image_url = product['image_urls'][0] if product['image_urls'] else ""
            else:
                image_url = product.get('image_url', '')
            
            dolce_product = {
                "id": product.get('sku', f"product_{i + 1}"),
                "name": product.get('name', 'Unknown Product'),
                "brand": self.brand_mapping.get(product.get('brand', 'Unknown'), product.get('brand', 'Unknown')),
                "price": current_price_rub,
                "originalPrice": original_price_rub,
                "discount": discount_str,
                "category": self.category_mapping.get(product.get('category', 'clothing'), 'Одежда'),
                "color": product.get('color', 'Разноцветный'),
                "sizes": product.get('available_sizes', []),
                "image": image_url,
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
                
            # Проверяем формат данных
            if isinstance(bestsecret_data, list):
                # Это прямой массив товаров от парсера
                products = bestsecret_data
            else:
                # Это объект с полем products
                products = bestsecret_data.get('products', [])
                
        else:
            print("Warning: products_database.json не найден, используем демо данные")
            products = [
                {
                    "sku": "demo_1",
                    "name": "Demo Fashion Item",
                    "brand": "Demo Brand",
                    "current_price": 99.99,
                    "original_price": 199.99,
                    "discount_percentage": "50%",
                    "category": "clothing",
                    "color": "Black",
                    "available_sizes": ["M", "L", "XL"],
                    "image_urls": ["https://via.placeholder.com/400x400"],
                }
            ]
        
        # Конвертируем в формат Dolce
        dolce_products = converter.convert_bestsecret_to_dolce(products)
        
        return dolce_products
    except Exception as e:
        print(f"Ошибка загрузки товаров: {e}")
        return []

@app.route('/')
@app.route('/dolce/')
def home():
    """Главная страница - Dolce приложение со встроенными стилями"""
    try:
        # Используем встроенную версию приложения
        with open('embedded_app.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Ошибка загрузки embedded_app.html: {e}")
        # Fallback версия
        return """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dolce Deals</title>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 50px auto; text-align: center; background: white; padding: 30px; border-radius: 12px; }
                .btn { display: inline-block; padding: 15px 30px; background: #4a90e2; color: white; text-decoration: none; border-radius: 8px; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛍️ Dolce Deals</h1>
                <p>Fashion приложение с товарами от премиальных брендов</p>
                <a href="/api/health" class="btn">📊 Health Check</a>
                <a href="/api/products" class="btn">🛍️ Посмотреть товары</a>
                <div id="products"></div>
                <script>
                    fetch('/api/products')
                        .then(r => r.json())
                        .then(products => {
                            document.getElementById('products').innerHTML = 
                                '<h3>Загружено товаров: ' + products.length + '</h3>' +
                                products.map(p => 
                                    '<div style="border:1px solid #ddd;margin:10px;padding:10px;">' +
                                    '<strong>' + p.brand + ' ' + p.name + '</strong><br>' +
                                    'Цена: ' + p.price + '₽' +
                                    '</div>'
                                ).join('');
                        })
                        .catch(e => {
                            document.getElementById('products').innerHTML = '❌ Ошибка: ' + e.message;
                        });
                </script>
            </div>
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

# Статические файлы для Railway
@app.route('/style.css')
def serve_css():
    """CSS файл"""
    return send_from_directory('.', 'style.css', mimetype='text/css')

@app.route('/app.js')
def serve_app_js():
    """Основной JS файл"""
    return send_from_directory('.', 'app.js', mimetype='application/javascript')

@app.route('/app_with_api.js') 
def serve_api_js():
    """API JS файл"""
    return send_from_directory('.', 'app_with_api.js', mimetype='application/javascript')

@app.route('/data/categories.js')
def serve_categories():
    """Категории JS"""
    return send_from_directory('./data', 'categories.js', mimetype='application/javascript')

@app.route('/manifest.json')
def serve_manifest():
    """PWA манифест"""
    return send_from_directory('.', 'manifest.json', mimetype='application/json')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Assets файлы (изображения, иконки)"""
    return send_from_directory('./assets', filename)

@app.route('/sw.js')
def serve_sw():
    """Service Worker"""
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/data/<path:filename>')
def serve_data(filename):
    """Data файлы"""
    return send_from_directory('./data', filename)

# Railway будет использовать app объект через Gunicorn