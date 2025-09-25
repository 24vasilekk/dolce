# 🛍️ Dolce Deals x BestSecret Integration

Премиальное fashion приложение с реальными товарами от премиальных брендов через интеграцию с BestSecret парсером.

![Integration](https://img.shields.io/badge/Integration-BestSecret%20API-blue.svg)
![Brands](https://img.shields.io/badge/Brands-Gucci%20%7C%20Off--White%20%7C%20Canada%20Goose-green.svg)
![Platform](https://img.shields.io/badge/Platform-PWA%20%7C%20Telegram%20Mini%20App-lightgrey.svg)

## 🚀 Быстрый старт

### Локальный запуск
```bash
# 1. Установить зависимости
pip install flask flask-cors requests

# 2. Запустить всю систему одной командой
python3 start_dolce_system.py

# 3. Открыть приложение
# http://localhost:8080
```

### Railway деплой
```bash
# 1. Создать репозиторий на GitHub (уже сделано)
# 2. Подключить к Railway через GitHub интеграцию
# 3. Railway автоматически развернет приложение
# 4. Настроить Telegram Bot с полученным доменом
```

## 🎯 Что работает

✅ **6 реальных товаров** от премиальных брендов  
✅ **100% извлечение размеров** (EU 35-50, XS-XXL)  
✅ **Автоконвертация цен** EUR → RUB  
✅ **API интеграция** с автосинхронизацией  
✅ **Оффлайн режим** с кэшированием  
✅ **Railway deployment** готов к продакшену  

## 📊 Примеры товаров

**Off-White Sneakers** - 27,900₽ (скидка 53%)  
**Canada Goose Down parka** - 59,900₽ (скидка 60%)  
**Gucci Ankle-boots** - 68,500₽ (скидка 42%)  
**Gucci Denim Bermuda** - 38,900₽ (скидка 60%)  

## 🔧 Архитектура интеграции

### Компоненты системы:
1. **`bestsecret_parser.py`** - Парсер с multi-strategy извлечением размеров
2. **`dolce_api_server.py`** - API конвертер BestSecret → Dolce формат
3. **`app_with_api.js`** - Обновленное Dolce приложение с API
4. **`start_dolce_system.py`** - Автоматический лаунчер всей системы

### Особенности:
- **Multi-strategy size extraction**: Интерактивные элементы + статические селекторы + парсинг описания
- **Smart data conversion**: Автоматический маппинг брендов, категорий, цветов
- **Graceful fallback**: API → localStorage → статические данные
- **Production ready**: Railway конфигурация + health checks

## 📱 Telegram Mini App

### Настройка бота:
```
1. @BotFather → /setmenubutton
2. Button text: 🛍️ Открыть магазин
3. Web App URL: https://your-railway-domain
```

### Готовые функции:
- Telegram WebApp API интеграция
- Адаптивная тема под Telegram
- Главная кнопка для навигации
- Кнопка "Назад" в модальных окнах

## 🛠️ Разработка

### Структура файлов:
```
dolce/
├── README.md                    # Документация
├── index.html                   # Главная страница приложения
├── app.js                       # Оригинальное приложение
├── app_with_api.js             # API-интегрированная версия
├── style.css                    # Стили приложения
├── bestsecret_parser.py         # BestSecret парсер
├── dolce_api_server.py         # API сервер для интеграции
├── dolce_api_server_railway.py # Production версия для Railway
├── start_dolce_system.py       # Автозапуск системы
├── railway.json                # Railway конфигурация
├── products_database.json      # BestSecret данные
├── dolce_converted_products.json # Конвертированные данные
└── requirements.txt            # Python зависимости
```

### API Endpoints:
- `GET /api/products` - Все товары в формате Dolce
- `GET /api/stats` - Статистика товаров  
- `GET /api/health` - Health check для Railway
- `GET /api/products/{id}` - Конкретный товар

## 📖 Полная документация

Смотрите дополнительные файлы:
- `RAILWAY_DEPLOY.md` - Деплой на Railway
- `TELEGRAM_DEPLOY_GUIDE.md` - Настройка Telegram Mini App
- `DOLCE_INTEGRATION.md` - Техническая документация интеграции
- `README_QUICK_START.md` - Быстрый старт для пользователей

## 🎉 Результат

**Ваше Dolce Deals приложение теперь получает реальные товары от премиальных брендов!**

- ✅ Работает локально за 30 секунд
- ✅ Деплоится на Railway одним кликом  
- ✅ Готово к Telegram Mini App интеграции
- ✅ 100% рабочая система с реальными данными

**🚀 От статических данных к реальному fashion e-commerce за один день!**