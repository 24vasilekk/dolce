#!/usr/bin/env python3
"""
Dolce API Server - API сервер для интеграции BestSecret парсера с Dolce приложением
Конвертирует данные парсера в формат, совместимый с Dolce Deals Fashion App
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import uuid

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataConverter:
    """Конвертер данных из формата BestSecret в формат Dolce"""
    
    # Маппинг брендов для корректного отображения
    BRAND_MAPPING = {
        "Off-White": "Off-White",
        "Canada Goose": "Canada Goose", 
        "Gucci": "Gucci",
        "See by Chloé": "See by Chloé",
        "Stone Island": "Stone Island",
        "Hugo Boss": "Hugo Boss",
        "Diesel": "Diesel",
        "Ralph Lauren": "Ralph Lauren"
    }
    
    # Маппинг категорий
    CATEGORY_MAPPING = {
        "Sneakers": {"category": "shoes", "subcategory": "Кроссовки и кеды"},
        "Down parka": {"category": "clothing", "subcategory": "Верхняя одежда"},
        "Ankle-boots": {"category": "shoes", "subcategory": "Ботинки"},
        "Ankle boots": {"category": "shoes", "subcategory": "Ботинки"},
        "Denim Bermuda": {"category": "clothing", "subcategory": "Шорты"},
        "Denim shirt": {"category": "clothing", "subcategory": "Рубашки"}
    }
    
    # Маппинг цветов
    COLOR_MAPPING = {
        "White": "white",
        "Black": "black", 
        "Blue": "blue",
        "Midnight Blue": "blue",
        "Grey": "grey",
        "Gray": "grey",
        "Red": "red",
        "Green": "green",
        "Yellow": "yellow",
        "Pink": "pink",
        "Brown": "brown",
        "Navy": "blue",
        "Beige": "beige"
    }
    
    def __init__(self):
        self.product_id_counter = 1000  # Начинаем с 1000 чтобы не конфликтовать с существующими ID
    
    def convert_bestsecret_to_dolce(self, bestsecret_products: List[Dict]) -> List[Dict]:
        """Конвертирует продукты BestSecret в формат Dolce"""
        dolce_products = []
        
        for product in bestsecret_products:
            try:
                dolce_product = self._convert_single_product(product)
                if dolce_product:
                    dolce_products.append(dolce_product)
            except Exception as e:
                logger.error(f"Ошибка конвертации товара {product.get('name', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Конвертировано {len(dolce_products)} товаров из {len(bestsecret_products)}")
        return dolce_products
    
    def _convert_single_product(self, product: Dict) -> Optional[Dict]:
        """Конвертирует один товар"""
        if not product.get('name') or not product.get('brand'):
            return None
        
        # Определяем пол из URL или используем дефолт
        gender = self._extract_gender(product)
        
        # Определяем категорию и подкатегорию
        category_info = self._extract_category(product)
        
        # Конвертируем цены из евро в рубли (примерный курс 100 руб за евро)
        rub_price = int(product.get('current_price', 0) * 100) if product.get('current_price') else 0
        rub_original_price = int(product.get('original_price', 0) * 100) if product.get('original_price') else None
        
        # Генерируем уникальный ID
        unique_id = self.product_id_counter
        self.product_id_counter += 1
        
        dolce_product = {
            "id": unique_id,
            "name": product['name'],
            "brand": self.BRAND_MAPPING.get(product['brand'], product['brand']),
            "price": rub_price,
            "image": self._get_best_image(product),
            "gender": gender,
            "category": category_info['category'],
            "subcategory": category_info['subcategory'],
            "colors": self._extract_colors(product),
            "sizes": self._extract_sizes(product),
            "materials": self._extract_materials(product),
            "description": self._clean_description(product.get('description', '')),
            "source": "BestSecret",
            "source_url": product.get('url', ''),
            "parsed_at": product.get('parsed_at', datetime.now().isoformat())
        }
        
        # Добавляем скидку если есть
        if rub_original_price and rub_original_price > rub_price:
            dolce_product["salePrice"] = rub_price
            dolce_product["price"] = rub_original_price
            dolce_product["onSale"] = True
        else:
            dolce_product["onSale"] = False
        
        return dolce_product
    
    def _extract_gender(self, product: Dict) -> str:
        """Определяет пол из данных товара"""
        url = product.get('url', '').lower()
        name = product.get('name', '').lower()
        description = product.get('description', '').lower()
        
        # Проверяем по URL
        if 'male' in url and 'female' not in url:
            return 'men'
        elif 'female' in url:
            return 'women'
        elif 'kids' in url or 'child' in url:
            return 'kids'
        
        # Проверяем по названию и описанию
        text = f"{name} {description}"
        
        # Мужские индикаторы
        men_indicators = ['men', 'man', 'male', 'мужск', 'для мужчин']
        if any(indicator in text for indicator in men_indicators):
            return 'men'
        
        # Женские индикаторы  
        women_indicators = ['women', 'woman', 'female', 'ladies', 'женск', 'для женщин']
        if any(indicator in text for indicator in women_indicators):
            return 'women'
            
        # Детские индикаторы
        kids_indicators = ['kids', 'child', 'children', 'baby', 'детск', 'для детей']
        if any(indicator in text for indicator in kids_indicators):
            return 'kids'
        
        # По умолчанию возвращаем мужское
        return 'men'
    
    def _extract_category(self, product: Dict) -> Dict[str, str]:
        """Определяет категорию и подкатегорию товара"""
        name = product.get('name', '')
        
        # Проверяем по названию товара
        for key, category_info in self.CATEGORY_MAPPING.items():
            if key.lower() in name.lower():
                return category_info
        
        # Если не нашли в маппинге, определяем по ключевым словам
        name_lower = name.lower()
        
        # Обувь
        shoe_keywords = ['sneakers', 'boots', 'shoes', 'кроссовки', 'ботинки', 'туфли', 'сандалии']
        if any(keyword in name_lower for keyword in shoe_keywords):
            if 'sneaker' in name_lower or 'кроссовки' in name_lower:
                return {"category": "shoes", "subcategory": "Кроссовки и кеды"}
            elif 'boot' in name_lower or 'ботинки' in name_lower:
                return {"category": "shoes", "subcategory": "Ботинки"}
            else:
                return {"category": "shoes", "subcategory": "Туфли"}
        
        # Одежда
        clothing_keywords = ['shirt', 'parka', 'jacket', 'pants', 'jeans', 'рубашка', 'куртка', 'брюки']
        if any(keyword in name_lower for keyword in clothing_keywords):
            if 'shirt' in name_lower or 'рубашка' in name_lower:
                return {"category": "clothing", "subcategory": "Рубашки"}
            elif 'parka' in name_lower or 'jacket' in name_lower or 'куртка' in name_lower:
                return {"category": "clothing", "subcategory": "Верхняя одежда"}
            elif 'pants' in name_lower or 'jeans' in name_lower or 'брюки' in name_lower:
                return {"category": "clothing", "subcategory": "Брюки"}
            else:
                return {"category": "clothing", "subcategory": "Одежда"}
        
        # По умолчанию
        return {"category": "clothing", "subcategory": "Одежда"}
    
    def _extract_colors(self, product: Dict) -> List[str]:
        """Извлекает цвета товара"""
        colors = []
        
        # Проверяем поле color
        if product.get('color'):
            color = product['color']
            mapped_color = self.COLOR_MAPPING.get(color, color.lower())
            colors.append(mapped_color)
        
        # Ищем цвета в описании
        description = product.get('description', '').lower()
        for original_color, mapped_color in self.COLOR_MAPPING.items():
            if original_color.lower() in description:
                if mapped_color not in colors:
                    colors.append(mapped_color)
        
        return colors if colors else ["black"]  # По умолчанию черный
    
    def _extract_sizes(self, product: Dict) -> List[str]:
        """Извлекает размеры товара"""
        sizes = []
        
        # Доступные размеры
        if product.get('available_sizes'):
            for size in product['available_sizes']:
                # Очищаем размер от префикса EU
                clean_size = size.replace('EU ', '').strip()
                sizes.append(clean_size)
        
        # Недоступные размеры (добавляем для полноты информации)
        if product.get('out_of_stock_sizes') and not sizes:
            for size in product['out_of_stock_sizes']:
                clean_size = size.replace('EU ', '').strip()
                sizes.append(clean_size)
        
        return sizes if sizes else ["M"]  # По умолчанию M
    
    def _extract_materials(self, product: Dict) -> List[str]:
        """Извлекает материалы из описания"""
        materials = []
        description = product.get('description', '').lower()
        
        # Словарь материалов
        material_keywords = {
            'cotton': 'Хлопок',
            'polyester': 'Полиэстер', 
            'leather': 'Кожа',
            'denim': 'Деним',
            'wool': 'Шерсть',
            'silk': 'Шелк',
            'synthetic': 'Синтетика',
            'polyamide': 'Полиамид',
            'duck down': 'Пух',
            'duck feathers': 'Перо',
            'textile': 'Текстиль'
        }
        
        for keyword, material in material_keywords.items():
            if keyword in description:
                if material not in materials:
                    materials.append(material)
        
        return materials if materials else ["Текстиль"]
    
    def _get_best_image(self, product: Dict) -> str:
        """Выбирает лучшее изображение товара"""
        image_urls = product.get('image_urls', [])
        
        if image_urls:
            # Возвращаем первое изображение
            return image_urls[0]
        
        # Фолбэк изображения по категориям
        name = product.get('name', '').lower()
        if 'sneaker' in name or 'boot' in name:
            return "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop"
        elif 'shirt' in name:
            return "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&h=400&fit=crop"
        elif 'parka' in name or 'jacket' in name:
            return "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400&h=400&fit=crop"
        else:
            return "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=400&fit=crop"
    
    def _clean_description(self, description: str) -> str:
        """Очищает описание товара"""
        if not description:
            return ""
        
        # Удаляем технический текст и оставляем только полезную информацию
        lines = description.split('\n')
        clean_lines = []
        
        skip_phrases = [
            'add to cart', 'select your size', 'prices include vat', 
            'free returns', 'secure payment', 'information on product safety'
        ]
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Минимальная длина
                line_lower = line.lower()
                if not any(phrase in line_lower for phrase in skip_phrases):
                    clean_lines.append(line)
        
        result = ' '.join(clean_lines[:3])  # Первые 3 релевантные строки
        return result[:200] + "..." if len(result) > 200 else result  # Ограничиваем длину

# Глобальный конвертер
converter = DataConverter()

@app.route('/api/products', methods=['GET'])
def get_products():
    """API для получения товаров в формате Dolce"""
    try:
        # Загружаем данные из базы BestSecret парсера
        database_file = 'products_database.json'
        
        if not os.path.exists(database_file):
            return jsonify({
                "error": "База данных товаров не найдена",
                "message": "Запустите парсер BestSecret для создания базы данных"
            }), 404
        
        with open(database_file, 'r', encoding='utf-8') as f:
            bestsecret_products = json.load(f)
        
        # Конвертируем в формат Dolce
        dolce_products = converter.convert_bestsecret_to_dolce(bestsecret_products)
        
        # Поддерживаем параметры фильтрации
        gender = request.args.get('gender')
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)
        
        # Применяем фильтры
        filtered_products = dolce_products
        
        if gender:
            filtered_products = [p for p in filtered_products if p['gender'] == gender]
        
        if category:
            filtered_products = [p for p in filtered_products if p['category'] == category]
        
        if limit:
            filtered_products = filtered_products[:limit]
        
        logger.info(f"API запрос: найдено {len(filtered_products)} товаров (gender={gender}, category={category}, limit={limit})")
        
        return jsonify(filtered_products)
        
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера", "details": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """API для получения конкретного товара"""
    try:
        products = get_products().get_json()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({"error": "Товар не найден"}), 404
        
        return jsonify(product)
        
    except Exception as e:
        logger.error(f"Ошибка получения товара {product_id}: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API для получения статистики базы данных"""
    try:
        with open('products_database.json', 'r', encoding='utf-8') as f:
            bestsecret_products = json.load(f)
        
        dolce_products = converter.convert_bestsecret_to_dolce(bestsecret_products)
        
        # Подсчитываем статистику
        stats = {
            "total_products": len(dolce_products),
            "by_gender": {},
            "by_category": {},
            "by_brand": {},
            "with_discount": 0,
            "avg_price": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        total_price = 0
        for product in dolce_products:
            # По полу
            gender = product['gender']
            stats["by_gender"][gender] = stats["by_gender"].get(gender, 0) + 1
            
            # По категории
            category = product['category']
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # По бренду
            brand = product['brand']
            stats["by_brand"][brand] = stats["by_brand"].get(brand, 0) + 1
            
            # Скидки
            if product.get('onSale'):
                stats["with_discount"] += 1
            
            # Средняя цена
            total_price += product['price']
        
        if len(dolce_products) > 0:
            stats["avg_price"] = round(total_price / len(dolce_products))
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка здоровья API"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    logger.info("🚀 Запуск Dolce API Server...")
    logger.info("📡 API будет доступно по адресу: http://localhost:5000")
    logger.info("📋 Endpoints:")
    logger.info("   GET /api/products - Список всех товаров")  
    logger.info("   GET /api/products?gender=men - Товары для мужчин")
    logger.info("   GET /api/products?category=shoes - Обувь")
    logger.info("   GET /api/products/<id> - Конкретный товар")
    logger.info("   GET /api/stats - Статистика базы данных")
    logger.info("   GET /api/health - Проверка работоспособности")
    
    app.run(host='0.0.0.0', port=5001, debug=True)