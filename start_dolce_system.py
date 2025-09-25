#!/usr/bin/env python3
"""
Dolce System Launcher - Автоматический запуск всей системы
Запускает парсер, API сервер и веб-приложение
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    print("🌟" * 50)
    print("🛍️  DOLCE DEALS - FASHION SYSTEM LAUNCHER")
    print("🌟" * 50)
    print("📋 Компоненты системы:")
    print("   1. 🕷️  BestSecret Parser - парсинг товаров")
    print("   2. 🔌 API Server - сервер данных") 
    print("   3. 🌐 Web App - приложение Dolce")
    print("   4. 💾 Database - база товаров")
    print()

def check_requirements():
    """Проверка установленных зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    try:
        import flask
        import flask_cors
        print("✅ Flask и Flask-CORS установлены")
    except ImportError:
        print("❌ Flask не установлен!")
        print("📦 Установите зависимости: pip install -r requirements_api.txt")
        return False
    
    # Проверяем наличие файлов
    required_files = [
        'bestsecret_parser.py',
        'dolce_api_server.py', 
        'dolce/index.html',
        'dolce/app.js',
        'dolce/app_with_api.js'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Отсутствует файл: {file_path}")
            return False
    
    print("✅ Все файлы найдены")
    return True

def run_parser():
    """Запуск парсера BestSecret"""
    print("\n🕷️ ЗАПУСК ПАРСЕРА BESTSECRET...")
    print("⏱️  Это может занять 2-3 минуты...")
    
    try:
        result = subprocess.run([
            sys.executable, 'bestsecret_parser.py'
        ], capture_output=True, text=True, timeout=300)  # 5 минут timeout
        
        if result.returncode == 0:
            print("✅ Парсер завершен успешно!")
            print(f"📊 Найдено товаров в логах:")
            # Ищем информацию о товарах в выводе
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'Найдено' in line and 'товар' in line:
                    print(f"   {line}")
                elif '✅' in line and ('Извлечено' in line or 'товар' in line):
                    print(f"   {line}")
            return True
        else:
            print("❌ Ошибка запуска парсера:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут парсера (>5 минут)")
        return False
    except Exception as e:
        print(f"❌ Критическая ошибка парсера: {e}")
        return False

def start_api_server():
    """Запуск API сервера в отдельном потоке"""
    def run_api():
        try:
            print("\n🔌 ЗАПУСК API СЕРВЕРА...")
            print("🌐 API будет доступно на http://localhost:5001")
            
            # Запускаем API сервер
            subprocess.run([sys.executable, 'dolce_api_server.py'])
        except Exception as e:
            print(f"❌ Ошибка API сервера: {e}")
    
    # Запускаем в отдельном потоке
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Даем время серверу запуститься
    time.sleep(3)
    
    # Проверяем работоспособность API
    try:
        import requests
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ API сервер запущен успешно!")
            return True
        else:
            print(f"⚠️ API сервер отвечает с кодом: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API сервер недоступен: {e}")
        return False

def start_web_server():
    """Запуск веб-сервера для приложения"""
    def run_web():
        try:
            print("\n🌐 ЗАПУСК ВЕБ-СЕРВЕРА...")
            print("📱 Приложение будет доступно на http://localhost:8080")
            
            # Переходим в папку dolce
            os.chdir('dolce')
            
            # Запускаем простой HTTP сервер
            subprocess.run([sys.executable, '-m', 'http.server', '8080'])
        except Exception as e:
            print(f"❌ Ошибка веб-сервера: {e}")
    
    # Запускаем в отдельном потоке  
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # Даем время серверу запуститься
    time.sleep(2)
    
    return True

def open_application():
    """Открытие приложения в браузере"""
    print("\n🚀 ОТКРЫТИЕ ПРИЛОЖЕНИЯ...")
    time.sleep(2)
    
    try:
        webbrowser.open('http://localhost:8080')
        print("✅ Приложение открыто в браузере!")
        return True
    except Exception as e:
        print(f"❌ Не удалось открыть браузер: {e}")
        print("🌐 Откройте вручную: http://localhost:8080")
        return False

def show_status():
    """Отображение статуса системы"""
    print("\n" + "🎯" * 50)
    print("📊 СТАТУС СИСТЕМЫ DOLCE DEALS")
    print("🎯" * 50)
    
    # Проверяем базу данных
    if os.path.exists('products_database.json'):
        try:
            import json
            with open('products_database.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            print(f"💾 База данных: ✅ {len(products)} товаров")
        except:
            print("💾 База данных: ❌ поврежден")
    else:
        print("💾 База данных: ❌ отсутствует")
    
    # Проверяем API
    try:
        import requests
        response = requests.get('http://localhost:5001/api/health', timeout=2)
        if response.status_code == 200:
            print("🔌 API Сервер: ✅ работает (http://localhost:5001)")
        else:
            print("🔌 API Сервер: ⚠️ ошибки")
    except:
        print("🔌 API Сервер: ❌ недоступен")
    
    # Проверяем веб-сервер
    try:
        import requests
        response = requests.get('http://localhost:8080', timeout=2)
        if response.status_code == 200:
            print("🌐 Веб-сервер: ✅ работает (http://localhost:8080)")
        else:
            print("🌐 Веб-сервер: ⚠️ ошибки")
    except:
        print("🌐 Веб-сервер: ❌ недоступен")
    
    print("\n📋 ДОСТУПНЫЕ ENDPOINTS:")
    endpoints = [
        "🏠 Приложение: http://localhost:8080",
        "📊 API товары: http://localhost:5001/api/products", 
        "📈 API статистика: http://localhost:5001/api/stats",
        "💓 API статус: http://localhost:5001/api/health"
    ]
    
    for endpoint in endpoints:
        print(f"   {endpoint}")

def main():
    print_banner()
    
    # Проверяем требования
    if not check_requirements():
        return
    
    print("🚀 НАЧИНАЕМ ЗАПУСК СИСТЕМЫ...\n")
    
    # Шаг 1: Запуск парсера для получения данных
    parser_success = run_parser()
    
    if not parser_success:
        print("\n⚠️ Парсер не запустился, но API может использовать кэшированные данные")
    
    # Шаг 2: Запуск API сервера
    api_success = start_api_server()
    
    if not api_success:
        print("❌ API сервер не запустился! Приложение будет работать с локальными данными")
    
    # Шаг 3: Запуск веб-сервера
    web_success = start_web_server()
    
    if not web_success:
        print("❌ Веб-сервер не запустился!")
        return
    
    # Шаг 4: Открытие приложения
    open_application()
    
    # Показываем статус
    show_status()
    
    print("\n" + "🎉" * 50)
    print("🎊 СИСТЕМА DOLCE DEALS ЗАПУЩЕНА!")
    print("🎉" * 50)
    print("\n📱 Приложение готово к использованию!")
    print("⭐ Особенности:")
    print("   • Реальные товары из BestSecret")
    print("   • Автоматические обновления через API") 
    print("   • Оффлайн режим с кэшированием")
    print("   • PWA поддержка")
    print("   • Telegram WebApp совместимость")
    
    print("\n🔄 Для остановки системы нажмите Ctrl+C")
    
    try:
        # Держим систему работающей
        while True:
            time.sleep(60)
            print(".", end="", flush=True)  # Показываем что система работает
    except KeyboardInterrupt:
        print("\n\n👋 Система остановлена пользователем")
        print("Спасибо за использование Dolce Deals!")

if __name__ == "__main__":
    main()