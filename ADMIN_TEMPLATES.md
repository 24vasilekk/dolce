# 🎛️ Заготовки админ-системы для Dolce Deals

## 📊 Формат данных парсера BestSecret

```json
[
  {
    "url": "https://www.bestsecret.com/product.htm?code=...",
    "site": "BestSecret",
    "sku": "BS-20250925141444-2a488a",
    "parsed_at": "2025-09-25T14:14:44.712979",
    "name": "Sneakers",
    "brand": "Off-White", 
    "category": null,
    "subcategory": null,
    "gender": null,
    "color": "White",
    "description": "...",
    "current_price": 279.0,
    "original_price": 590.0,
    "currency": "EUR",
    "discount_amount": 311.0,
    "discount_percentage": 52.71,
    "available_sizes": ["EU 35", "EU 36", "EU 37"],
    "out_of_stock_sizes": ["EU 38", "EU 39"],
    "in_stock": true,
    "stock_level": "in_stock",
    "image_urls": ["https://picture.bestsecret.com/..."]
  }
]
```

## 🔄 Конвертация в формат Dolce

```javascript
// Формат для Dolce приложения
{
  "id": "BS-20250925141444-2a488a",
  "name": "Sneakers",
  "brand": "Off-White",
  "price": 27900,          // EUR * 100 для рублей
  "originalPrice": 59000,  // EUR * 100 для рублей  
  "discount": "53%",
  "category": "Обувь",
  "color": "White",
  "sizes": ["EU 35", "EU 36", "EU 37"],
  "image": "https://picture.bestsecret.com/...",
  "description": "Off-White Sneakers",
  "inStock": true
}
```

## 🎛️ Функции админки (заготовки)

### 1. **Импорт JSON файлов**
- Загрузка `products_database.json` от парсера
- Валидация формата данных
- Преобразование в внутренний формат
- Массовое добавление товаров

### 2. **Управление товарами**
- Просмотр списка товаров
- Фильтрация по бренду/категории  
- Редактирование товара
- Активация/деактивация
- Удаление товаров

### 3. **Категории и бренды**
- Управление списком брендов
- Создание категорий
- Маппинг данных парсера

### 4. **Статистика**
- Количество товаров по брендам
- Средние цены и скидки
- История импортов
- Топ товаров

## 🚀 Быстрая реализация

### API endpoints для админки:
```
POST /admin/import           # Импорт JSON товаров
GET  /admin/products         # Список товаров  
PUT  /admin/products/{id}    # Редактировать товар
DELETE /admin/products/{id}  # Удалить товар
GET  /admin/stats           # Статистика
```

### HTML интерфейс:
- Форма загрузки JSON
- Таблица товаров с пагинацией
- Модальные окна редактирования
- Dashboard со статистикой

## 📁 Структура файлов

```
admin/
├── templates/
│   ├── dashboard.html    # Главная страница
│   ├── products.html     # Управление товарами
│   └── import.html       # Импорт данных
├── static/
│   ├── css/admin.css     # Стили админки
│   └── js/admin.js       # JavaScript админки
└── admin_routes.py       # Flask роуты
```

## 🎯 Приоритеты

1. **Сейчас**: Исправить Railway деплой приложения
2. **Потом**: Простая админка для импорта JSON
3. **Будущее**: Полная система управления

**Основное - чтобы приложение работало и показывало товары!** 🛍️