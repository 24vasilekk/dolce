#!/usr/bin/env python3
"""
Quick test script for navigation improvements
"""

import re
from bestsecret_parser import BestSecretParser

def test_navigation():
    print("🧪 Тестирование навигации...")
    
    # Загружаем данные из .env
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            env_content = f.read()
            email_match = re.search(r'BESTSECRET_EMAIL=(.+)', env_content)
            password_match = re.search(r'BESTSECRET_PASSWORD=(.+)', env_content)
            
            EMAIL = email_match.group(1) if email_match else None
            PASSWORD = password_match.group(1) if password_match else None
    except:
        EMAIL = "akinitovfilipp@gmail.com"
        PASSWORD = "Kaluga40"
    
    parser = BestSecretParser(EMAIL, PASSWORD)
    
    try:
        # Инициализация
        if not parser.initialize_driver():
            print("❌ Не удалось запустить браузер")
            return
        
        # Авторизация
        if not parser.login():
            print("❌ Ошибка авторизации")
            return
        
        # Тестируем навигацию к каждой категории
        categories_to_test = ["Женское", "Мужское", "Детское"]
        
        for category in categories_to_test:
            print(f"\n🎯 Тестируем навигацию к: {category}")
            success = parser.navigate_to_category(category)
            if success:
                print(f"✅ {category} - навигация успешна")
                
                # Попробуем найти товары в этой категории
                product_links = parser.get_product_links(1)  # Только 1 товар для теста
                print(f"   📦 Найдено товаров: {len(product_links)}")
            else:
                print(f"❌ {category} - навигация не удалась")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        parser.cleanup()

if __name__ == "__main__":
    test_navigation()