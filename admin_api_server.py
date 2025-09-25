#!/usr/bin/env python3
"""
🎛️ Dolce Deals - Admin API Server
Расширенный API сервер с админ-панелью для управления товарами
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
import bcrypt

# Инициализация Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Конфигурация базы данных
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://admin:password@localhost:5432/dolcedeals')

class DatabaseManager:
    """Менеджер базы данных PostgreSQL"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
    
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.connection = psycopg2.connect(
                self.db_url,
                cursor_factory=RealDictCursor
            )
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return False
    
    def execute_query(self, query: str, params=None) -> List[Dict]:
        """Выполнение SELECT запроса"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            return []
    
    def execute_command(self, query: str, params=None) -> bool:
        """Выполнение INSERT/UPDATE/DELETE команды"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return True
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")
            if self.connection:
                self.connection.rollback()
            return False

# Глобальный менеджер БД
db = DatabaseManager(DATABASE_URL)

# Резервная система для случая отсутствия PostgreSQL
def load_products_from_json() -> List[Dict]:
    """Загрузка товаров из JSON файла (резервная система)"""
    try:
        with open('products_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Если это прямой массив товаров
            if isinstance(data, list):
                return data
            # Если это объект с полем products
            return data.get('products', [])
    except Exception as e:
        print(f"❌ Ошибка загрузки JSON: {e}")
        return []

def save_products_to_json(products: List[Dict]) -> bool:
    """Сохранение товаров в JSON файл"""
    try:
        with open('products_database.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения JSON: {e}")
        return False

# Декораторы для аутентификации
def require_auth(f):
    """Декоратор для требования аутентификации"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Токен не предоставлен'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.current_admin = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Токен истек'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Недействительный токен'}), 401
        
        return f(*args, **kwargs)
    return decorated

def require_role(required_role: str):
    """Декоратор для проверки роли администратора"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            admin_role = request.current_admin.get('role', 'admin')
            
            roles_hierarchy = {
                'super_admin': 3,
                'admin': 2,
                'moderator': 1
            }
            
            if roles_hierarchy.get(admin_role, 0) < roles_hierarchy.get(required_role, 0):
                return jsonify({'error': 'Недостаточно прав доступа'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# =============================================================================
# ПУБЛИЧНОЕ API (для Dolce приложения)
# =============================================================================

@app.route('/api/health')
def health_check():
    """Health check для Railway и мониторинга"""
    # Проверяем подключение к БД
    db_status = "connected" if db.connect() else "disconnected"
    
    # Считаем товары
    if db_status == "connected":
        products = db.execute_query("SELECT COUNT(*) as count FROM products WHERE status = 'active'")
        products_count = products[0]['count'] if products else 0
    else:
        # Используем JSON как резерв
        products = load_products_from_json()
        products_count = len(products)
    
    return jsonify({
        "status": "healthy",
        "service": "dolce-admin-api",
        "version": "2.0.0",
        "database": db_status,
        "products_loaded": products_count,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/products')
def get_products():
    """Получить все активные товары для приложения"""
    try:
        # Пытаемся загрузить из PostgreSQL
        if db.connect():
            products = db.execute_query("""
                SELECT id, sku, name, brand, price, original_price, discount_percentage,
                       category, gender, sizes, colors, images, description, 
                       views_count, favorites_count, created_at
                FROM products 
                WHERE status = 'active'
                ORDER BY created_at DESC
            """)
            
            # Конвертируем в формат Dolce приложения
            dolce_products = []
            for product in products:
                dolce_product = {
                    "id": product['id'],
                    "name": product['name'],
                    "brand": product['brand'],
                    "price": int(product['price']) if product['price'] else 0,
                    "originalPrice": int(product['original_price']) if product['original_price'] else 0,
                    "discount": f"{product['discount_percentage']}%" if product['discount_percentage'] else "0%",
                    "category": product['category'] or "Одежда",
                    "color": product['colors'][0] if product['colors'] else "Разноцветный",
                    "sizes": product['sizes'] or [],
                    "image": product['images'][0]['url'] if product['images'] else "",
                    "description": product['description'] or f"{product['brand']} {product['name']}",
                    "inStock": len(product['sizes'] or []) > 0
                }
                dolce_products.append(dolce_product)
            
            return jsonify(dolce_products)
        
        else:
            # Резервная загрузка из JSON
            products = load_products_from_json()
            return jsonify(convert_bestsecret_to_dolce(products))
            
    except Exception as e:
        print(f"❌ Ошибка получения товаров: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Получить конкретный товар"""
    try:
        if db.connect():
            products = db.execute_query(
                "SELECT * FROM products WHERE id = %s AND status = 'active'",
                (product_id,)
            )
            if products:
                return jsonify(products[0])
        
        return jsonify({"error": "Товар не найден"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Статистика для приложения"""
    try:
        if db.connect():
            stats = db.execute_query("""
                SELECT 
                    COUNT(*) as total_products,
                    COUNT(DISTINCT brand) as total_brands,
                    COUNT(DISTINCT category) as total_categories,
                    AVG(price) as avg_price,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as in_stock
                FROM products
            """)
            
            brands = db.execute_query("SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL")
            categories = db.execute_query("SELECT DISTINCT category FROM products WHERE category IS NOT NULL")
            
            return jsonify({
                "total_products": int(stats[0]['total_products']),
                "brands": [b['brand'] for b in brands],
                "categories": [c['category'] for c in categories],
                "avg_price": int(stats[0]['avg_price']) if stats[0]['avg_price'] else 0,
                "in_stock": int(stats[0]['in_stock'])
            })
        
        else:
            # Резервная статистика из JSON
            products = load_products_from_json()
            return jsonify({
                "total_products": len(products),
                "brands": list(set(p.get('brand', 'Unknown') for p in products)),
                "categories": list(set(p.get('category', 'clothing') for p in products)),
                "avg_price": 50000,  # Примерная средняя цена
                "in_stock": len(products)
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# АДМИН API (требует аутентификации)
# =============================================================================

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Аутентификация администратора"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Необходимо указать логин и пароль'}), 400
        
        # Временная аутентификация без БД (для демо)
        if username == 'admin' and password == 'admin123':
            token = jwt.encode({
                'username': username,
                'role': 'super_admin',
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'token': token,
                'user': {
                    'username': username,
                    'role': 'super_admin',
                    'full_name': 'System Administrator'
                }
            })
        
        return jsonify({'error': 'Неверные учетные данные'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/dashboard')
@require_auth
def admin_dashboard():
    """Данные для админ дашборда"""
    try:
        if db.connect():
            # Статистика товаров
            products_stats = db.execute_query("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active,
                    COUNT(CASE WHEN status = 'inactive' THEN 1 END) as inactive,
                    COUNT(CASE WHEN created_at >= CURRENT_DATE THEN 1 END) as today
                FROM products
            """)[0]
            
            # Последние логи парсинга
            parsing_logs = db.execute_query("""
                SELECT source, status, products_found, started_at, completed_at
                FROM parsing_logs 
                ORDER BY started_at DESC 
                LIMIT 10
            """)
            
            # Топ брендов
            top_brands = db.execute_query("""
                SELECT brand, COUNT(*) as count
                FROM products 
                WHERE brand IS NOT NULL
                GROUP BY brand 
                ORDER BY count DESC 
                LIMIT 10
            """)
        else:
            # Демо данные
            products_stats = {"total": 6, "active": 6, "inactive": 0, "today": 0}
            parsing_logs = []
            top_brands = [
                {"brand": "Gucci", "count": 2},
                {"brand": "Off-White", "count": 1},
                {"brand": "Canada Goose", "count": 1}
            ]
        
        return jsonify({
            "products_stats": products_stats,
            "parsing_logs": parsing_logs,
            "top_brands": top_brands,
            "system_info": {
                "database": "connected" if db.connection else "json_fallback",
                "version": "2.0.0"
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/products')
@require_auth  
def admin_get_products():
    """Получить все товары для админки"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        if db.connect():
            products = db.execute_query(f"""
                SELECT * FROM products 
                ORDER BY created_at DESC 
                LIMIT {limit} OFFSET {offset}
            """)
            
            total = db.execute_query("SELECT COUNT(*) as count FROM products")[0]['count']
        else:
            # Резерв из JSON
            all_products = load_products_from_json()
            products = all_products[offset:offset+limit]
            total = len(all_products)
        
        return jsonify({
            "products": products,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/products', methods=['POST'])
@require_auth
def admin_create_product():
    """Создать новый товар"""
    try:
        data = request.get_json()
        
        # Валидация обязательных полей
        required_fields = ['name', 'brand', 'price', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Поле {field} обязательно'}), 400
        
        if db.connect():
            # Вставка в PostgreSQL
            query = """
                INSERT INTO products (sku, name, brand, price, original_price, 
                                    category, gender, sizes, colors, description, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            sku = f"ADMIN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            success = db.execute_command(query, (
                sku,
                data['name'],
                data['brand'], 
                data['price'],
                data.get('original_price'),
                data['category'],
                data.get('gender', 'unisex'),
                json.dumps(data.get('sizes', [])),
                json.dumps(data.get('colors', [])),
                data.get('description', ''),
                'admin'
            ))
            
            if success:
                return jsonify({'message': 'Товар создан успешно'}), 201
            else:
                return jsonify({'error': 'Ошибка создания товара'}), 500
        
        else:
            return jsonify({'error': 'База данных недоступна'}), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Резервная функция конвертации (для совместимости)
def convert_bestsecret_to_dolce(bestsecret_products: List[Dict]) -> List[Dict]:
    """Конвертация BestSecret товаров в формат Dolce"""
    dolce_products = []
    
    for i, product in enumerate(bestsecret_products):
        # Парсим цену
        current_price_str = str(product.get('current_price', '0')).replace('€', '').replace(',', '.').strip()
        original_price_str = str(product.get('original_price', '0')).replace('€', '').replace(',', '.').strip()
        
        try:
            current_price = int(float(current_price_str) * 100)
        except:
            current_price = 0
        
        try:
            original_price = int(float(original_price_str) * 100)
        except:
            original_price = current_price
        
        dolce_product = {
            "id": product.get('id', f"product_{i + 1}"),
            "name": product.get('name', 'Unknown Product'),
            "brand": product.get('brand', 'Unknown'),
            "price": current_price,
            "originalPrice": original_price,
            "discount": product.get('discount_percentage', '0%'),
            "category": product.get('category', 'Одежда'),
            "color": product.get('color', 'Разноцветный'),
            "sizes": product.get('available_sizes', []),
            "image": product.get('image_url', ''),
            "description": f"{product.get('brand', 'Brand')} {product.get('name', 'Product')}",
            "inStock": len(product.get('available_sizes', [])) > 0
        }
        dolce_products.append(dolce_product)
    
    return dolce_products

# =============================================================================
# АДМИН-ПАНЕЛЬ UI (базовый HTML интерфейс)
# =============================================================================

@app.route('/admin')
@app.route('/admin/')
def admin_panel():
    """Главная страница админ-панели"""
    return render_template_string(ADMIN_PANEL_HTML)

# Базовый HTML для админ-панели
ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dolce Deals - Админ-панель</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .login-form { background: white; padding: 30px; border-radius: 8px; max-width: 400px; margin: 100px auto; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { color: #333; margin-bottom: 10px; }
        .card .number { font-size: 2em; font-weight: bold; color: #007bff; }
        #loginSection { display: block; }
        #adminSection { display: none; }
        .error { color: #dc3545; margin-top: 10px; }
        .success { color: #28a745; margin-top: 10px; }
    </style>
</head>
<body>
    <!-- Форма входа -->
    <div id="loginSection">
        <div class="login-form">
            <h2>Вход в админ-панель</h2>
            <form id="loginForm">
                <div class="form-group">
                    <label>Логин:</label>
                    <input type="text" id="username" value="admin" required>
                </div>
                <div class="form-group">
                    <label>Пароль:</label>
                    <input type="password" id="password" value="admin123" required>
                </div>
                <button type="submit" class="btn">Войти</button>
                <div id="loginError" class="error"></div>
            </form>
        </div>
    </div>

    <!-- Админ-панель -->
    <div id="adminSection">
        <div class="container">
            <div class="header">
                <h1>🛍️ Dolce Deals - Админ-панель</h1>
                <p>Система управления товарами и парсингом</p>
                <button onclick="logout()" class="btn" style="float: right; background: #dc3545;">Выйти</button>
            </div>

            <div class="dashboard" id="dashboard">
                <div class="card">
                    <h3>Всего товаров</h3>
                    <div class="number" id="totalProducts">-</div>
                </div>
                <div class="card">
                    <h3>Активных товаров</h3>
                    <div class="number" id="activeProducts">-</div>
                </div>
                <div class="card">
                    <h3>Брендов</h3>
                    <div class="number" id="totalBrands">-</div>
                </div>
                <div class="card">
                    <h3>Категорий</h3>
                    <div class="number" id="totalCategories">-</div>
                </div>
            </div>

            <div class="card">
                <h3>🚀 Быстрые действия</h3>
                <button class="btn" onclick="loadProducts()">Загрузить товары</button>
                <button class="btn" onclick="runParser()" style="background: #28a745;">Запустить парсер</button>
                <button class="btn" onclick="exportData()" style="background: #17a2b8;">Экспорт данных</button>
            </div>

            <div class="card">
                <h3>📊 Товары</h3>
                <div id="productsTable">Загрузка...</div>
            </div>
        </div>
    </div>

    <script>
        let authToken = localStorage.getItem('adminToken');

        // Проверка авторизации при загрузке
        if (authToken) {
            showAdminPanel();
        }

        // Вход в систему
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/admin/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    authToken = data.token;
                    localStorage.setItem('adminToken', authToken);
                    showAdminPanel();
                } else {
                    document.getElementById('loginError').textContent = data.error;
                }
            } catch (error) {
                document.getElementById('loginError').textContent = 'Ошибка подключения';
            }
        });

        function showAdminPanel() {
            document.getElementById('loginSection').style.display = 'none';
            document.getElementById('adminSection').style.display = 'block';
            loadDashboard();
        }

        function logout() {
            localStorage.removeItem('adminToken');
            authToken = null;
            document.getElementById('loginSection').style.display = 'block';
            document.getElementById('adminSection').style.display = 'none';
        }

        async function loadDashboard() {
            try {
                const response = await fetch('/admin/dashboard', {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('totalProducts').textContent = data.products_stats.total;
                    document.getElementById('activeProducts').textContent = data.products_stats.active;
                    document.getElementById('totalBrands').textContent = data.top_brands.length;
                    document.getElementById('totalCategories').textContent = '6';
                }
            } catch (error) {
                console.error('Ошибка загрузки дашборда:', error);
            }
        }

        async function loadProducts() {
            try {
                const response = await fetch('/admin/products', {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    let html = '<table border="1" style="width:100%"><tr><th>ID</th><th>Название</th><th>Бренд</th><th>Цена</th><th>Статус</th></tr>';
                    data.products.forEach(product => {
                        html += `<tr>
                            <td>${product.id || product.sku}</td>
                            <td>${product.name}</td>
                            <td>${product.brand}</td>
                            <td>${product.price}₽</td>
                            <td>${product.status || 'active'}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    document.getElementById('productsTable').innerHTML = html;
                }
            } catch (error) {
                document.getElementById('productsTable').innerHTML = 'Ошибка загрузки товаров';
            }
        }

        function runParser() {
            alert('🚀 Функция парсера будет добавлена в следующей версии!');
        }

        function exportData() {
            alert('📊 Функция экспорта будет добавлена в следующей версии!');
        }
    </script>
</body>
</html>
"""

# =============================================================================
# СТАТИЧЕСКИЕ ФАЙЛЫ И DOLCE ПРИЛОЖЕНИЕ
# =============================================================================

@app.route('/')
def serve_dolce_app():
    """Главная страница - Dolce приложение"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return """
        <h1>🛍️ Dolce Deals</h1>
        <p>Приложение временно недоступно</p>
        <a href="/admin">Перейти в админ-панель</a>
        """

@app.route('/<path:filename>')
def serve_static(filename):
    """Статические файлы"""
    return send_from_directory('.', filename)

# =============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================================================

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5001))
    
    print("🚀 Запуск Dolce Admin API Server")
    print(f"📊 Порт: {PORT}")
    print(f"🔗 Приложение: http://localhost:{PORT}/")
    print(f"🎛️ Админ-панель: http://localhost:{PORT}/admin")
    print(f"🔧 API: http://localhost:{PORT}/api/health")
    print()
    print("🔑 Вход в админку:")
    print("   Логин: admin")
    print("   Пароль: admin123")
    
    # Пытаемся подключиться к БД
    if db.connect():
        print("✅ PostgreSQL подключена")
    else:
        print("⚠️ PostgreSQL недоступна, используется JSON резерв")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)