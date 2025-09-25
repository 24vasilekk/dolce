#!/usr/bin/env python3
"""
Тест интеграции API - проверка конвертации данных BestSecret в формат Dolce
"""

import json
import sys
import os

# Импортируем конвертер из API сервера
sys.path.append('.')
from dolce_api_server import DataConverter

def test_data_conversion():
    """Тестирование конвертации данных"""
    print("🧪 ТЕСТ КОНВЕРТАЦИИ ДАННЫХ BestSecret → Dolce")
    print("=" * 50)
    
    # Загружаем реальные данные из базы
    if not os.path.exists('products_database.json'):
        print("❌ Файл products_database.json не найден!")
        print("Запустите сначала парсер: python3 bestsecret_parser.py")
        return False
    
    with open('products_database.json', 'r', encoding='utf-8') as f:
        bestsecret_products = json.load(f)
    
    print(f"📦 Загружено {len(bestsecret_products)} товаров из BestSecret")
    
    # Создаем конвертер
    converter = DataConverter()
    
    # Конвертируем данные
    dolce_products = converter.convert_bestsecret_to_dolce(bestsecret_products)
    
    print(f"✅ Конвертировано {len(dolce_products)} товаров в формат Dolce")
    
    # Анализируем результаты конвертации
    print("\n📊 АНАЛИЗ КОНВЕРТИРОВАННЫХ ДАННЫХ:")
    print("-" * 40)
    
    # Статистика по полу
    gender_stats = {}
    category_stats = {}
    brand_stats = {}
    price_stats = []
    
    for product in dolce_products:
        # По полу
        gender = product['gender']
        gender_stats[gender] = gender_stats.get(gender, 0) + 1
        
        # По категории
        category = product['category']
        category_stats[category] = category_stats.get(category, 0) + 1
        
        # По бренду
        brand = product['brand']
        brand_stats[brand] = brand_stats.get(brand, 0) + 1
        
        # Цены
        price_stats.append(product['price'])
    
    print(f"👫 По полу:")
    for gender, count in gender_stats.items():
        print(f"   {gender}: {count}")
    
    print(f"📂 По категориям:")
    for category, count in category_stats.items():
        print(f"   {category}: {count}")
    
    print(f"🏷️ По брендам:")
    for brand, count in brand_stats.items():
        print(f"   {brand}: {count}")
    
    if price_stats:
        avg_price = sum(price_stats) / len(price_stats)
        print(f"💰 Цены:")
        print(f"   Средняя цена: {avg_price:,.0f} ₽")
        print(f"   Минимальная: {min(price_stats):,.0f} ₽")
        print(f"   Максимальная: {max(price_stats):,.0f} ₽")
    
    # Показываем примеры товаров
    print("\n🛍️ ПРИМЕРЫ ТОВАРОВ:")
    print("-" * 40)
    
    for i, product in enumerate(dolce_products[:3]):
        print(f"\n{i+1}. {product['name']} by {product['brand']}")
        print(f"   💰 {product['price']:,} ₽" + (f" (было {product.get('salePrice', product['price']):,} ₽)" if product.get('onSale') else ""))
        print(f"   👤 {product['gender']} | 📂 {product['category']} | 🏷️ {product['subcategory']}")
        print(f"   🎨 Цвета: {', '.join(product['colors'])}")
        print(f"   📏 Размеры: {', '.join(product['sizes'])}")
        print(f"   🧵 Материалы: {', '.join(product['materials'])}")
        print(f"   🔗 {product.get('source_url', 'N/A')[:50]}...")
    
    # Сохраняем конвертированные данные для тестирования
    with open('dolce_converted_products.json', 'w', encoding='utf-8') as f:
        json.dump(dolce_products, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Конвертированные данные сохранены в: dolce_converted_products.json")
    
    return True

def validate_dolce_format():
    """Проверяем что формат соответствует ожиданиям Dolce приложения"""
    print("\n🔍 ВАЛИДАЦИЯ ФОРМАТА DOLCE:")
    print("-" * 30)
    
    if not os.path.exists('dolce_converted_products.json'):
        print("❌ Конвертированные данные не найдены")
        return False
    
    with open('dolce_converted_products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    required_fields = ['id', 'name', 'brand', 'price', 'gender', 'category', 'colors', 'sizes']
    
    valid_count = 0
    for product in products:
        is_valid = True
        missing_fields = []
        
        for field in required_fields:
            if field not in product or not product[field]:
                is_valid = False
                missing_fields.append(field)
        
        if is_valid:
            valid_count += 1
        else:
            print(f"⚠️ Товар '{product.get('name', 'N/A')}' не валиден: отсутствуют поля {missing_fields}")
    
    print(f"✅ Валидных товаров: {valid_count}/{len(products)} ({valid_count/len(products)*100:.1f}%)")
    
    # Проверяем типы данных
    print("\n📋 Проверка типов данных:")
    if products:
        sample = products[0]
        checks = [
            ("ID", isinstance(sample.get('id'), int)),
            ("Название", isinstance(sample.get('name'), str) and len(sample.get('name', '')) > 0),
            ("Бренд", isinstance(sample.get('brand'), str) and len(sample.get('brand', '')) > 0),
            ("Цена", isinstance(sample.get('price'), int) and sample.get('price', 0) > 0),
            ("Цвета", isinstance(sample.get('colors'), list) and len(sample.get('colors', [])) > 0),
            ("Размеры", isinstance(sample.get('sizes'), list) and len(sample.get('sizes', [])) > 0),
        ]
        
        for check_name, is_ok in checks:
            status = "✅" if is_ok else "❌"
            print(f"   {status} {check_name}")
    
    return valid_count == len(products)

def main():
    print("🚀 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ DOLCE x BESTSECRET")
    print("🌟" * 50)
    
    # Тест 1: Конвертация данных
    conversion_success = test_data_conversion()
    
    if not conversion_success:
        print("❌ Тест конвертации провалился!")
        return
    
    # Тест 2: Валидация формата
    validation_success = validate_dolce_format()
    
    # Результат
    print("\n" + "🎯" * 50)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("🎯" * 50)
    
    if conversion_success and validation_success:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Конвертация данных работает")
        print("✅ Формат Dolce валиден")
        print("✅ API готово к запуску")
        print("\n🚀 Можно запускать полную систему:")
        print("   python3 start_dolce_system.py")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ С ИНТЕГРАЦИЕЙ:")
        if not conversion_success:
            print("   • Конвертация данных не работает")
        if not validation_success:
            print("   • Формат данных не валиден")
    
    print("🌟" * 50)

if __name__ == "__main__":
    main()