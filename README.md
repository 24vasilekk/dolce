# 🛍️ E-commerce Parser v2.0

Мощный парсер для извлечения данных о товарах с популярных e-commerce сайтов.

![Parser Preview](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Sites](https://img.shields.io/badge/Sites-8-green.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)

## 🚀 Быстрый старт

### macOS/Linux
```bash
./run_parser.sh
```

### Windows
```cmd
run_parser.bat
```

### Python
```bash
python run_parser.py
```

## 🌟 Поддерживаемые сайты

| Сайт | Тип | Особенности |
|------|-----|-------------|
| **BestSecret** | Luxury Outlet | Массовый парсинг |
| **Antonioli** | Designer Fashion | Размеры, цвета |
| **FARFETCH** | Luxury Marketplace | Высокое разрешение изображений |
| **NET-A-PORTER** | Women's Luxury | Только женская одежда |
| **MR PORTER** | Men's Luxury | Только мужская одежда |
| **YOOX** | Fashion Store | Поддержка скидок |
| **MATCHESFASHION** | Luxury Fashion | Полная информация |
| **24S** | Luxury Platform | Мультиязычность |

## 📋 Возможности

✅ **Парсинг товаров**: название, бренд, цены, размеры, изображения  
✅ **Экспорт данных**: CSV, Excel, JSON  
✅ **Графический интерфейс**: удобное управление  
✅ **Массовый парсинг**: обход каталогов  
✅ **Облачные изображения**: автозагрузка в Cloudinary  
✅ **Прогресс-бар**: отслеживание процесса  
✅ **Конфигурация**: настройка через config.json  

## 🛠️ Установка

Парсер автоматически установит все зависимости при первом запуске:

- selenium (веб-автоматизация)
- beautifulsoup4 (парсинг HTML)
- pandas (обработка данных)
- cloudinary (загрузка изображений)
- aiohttp (асинхронные запросы)

## 📁 Структура проекта

```
EcommerceParser/
├── 🐍 dolceparser_improved.py    # Основной парсер
├── 🐍 dolceparser_original.py    # Оригинальная версия
├── ⚡ run_parser.py              # Python launcher
├── ⚡ run_parser.sh              # Shell launcher
├── ⚙️ config.json               # Конфигурация
├── 📦 requirements.txt          # Зависимости
├── 📖 README.md                 # Документация
└── 📝 HOW_TO_ADD_SITES.md       # Руководство по добавлению сайтов
```

## 🎮 Использование

1. **Запустите парсер** любым удобным способом
2. **Откройте браузер** через интерфейс  
3. **Выберите сайт** из списка
4. **Перейдите** на страницу товара/каталога
5. **Настройте параметры** парсинга
6. **Начните парсинг** и следите за прогрессом
7. **Экспортируйте** результаты

## ⚙️ Настройка

### Cloudinary (изображения)
1. Зарегистрируйтесь на [cloudinary.com](https://cloudinary.com/)
2. Получите API ключи
3. Обновите `config.json`

### ChromeDriver
Автоматически устанавливается через:
```bash
brew install --cask chromedriver  # macOS
```

## 🔧 Добавление сайтов

Смотрите детальное руководство в файле `HOW_TO_ADD_SITES.md`

Кратко:
1. Создайте класс парсера
2. Реализуйте методы извлечения
3. Добавьте в главный класс
4. Обновите GUI

## 🐛 Решение проблем

### ChromeDriver несовместим
```bash
brew upgrade --cask chromedriver
```

### Ошибки зависимостей
```bash
pip install -r requirements.txt --force-reinstall
```

### Проблемы Cloudinary
Проверьте API ключи в `config.json`

## 📊 Экспорт данных

Парсер сохраняет следующие поля:

| Поле | Описание | Пример |
|------|----------|--------|
| sku | Уникальный артикул | FF-20231212143022-a1b2c3 |
| name | Название товара | Wool Blend Coat |
| brand | Бренд | Tom Ford |
| category | Категория | Outerwear |
| color | Цвет | Black |
| gender | Пол | Мужской/Женский |
| old_price | Старая цена | 2500 |
| new_price | Текущая цена | 1800 |
| sizes | Размеры | S, M, L, XL |
| images | URL изображений | https://cloudinary... |
| url | Ссылка на товар | https://site.com/item |

## 📝 Лицензия

Проект создан для образовательных целей. Соблюдайте Terms of Service сайтов.

---

**E-commerce Parser v2.0** - ваш инструмент для парсинга luxury fashion! ✨

**Архитектура**: Модульная, легко расширяемая  
**Производительность**: Асинхронная обработка изображений  
**Удобство**: Графический интерфейс и автозапуск  
**Надежность**: Обработка ошибок и повторные попытки  