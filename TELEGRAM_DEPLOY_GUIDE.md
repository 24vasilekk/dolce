# 📱 Деплой Dolce Deals как Telegram Mini App

## 🎯 Цель
Развернуть ваше приложение на сервере, чтобы оно работало 24/7 как Telegram Mini App в вашем боте.

## 📋 Что понадобится

### 🖥️ **Сервер**
- **VPS/VDS** (рекомендую: DigitalOcean, Beget, Timeweb)
- **Ubuntu 20.04+** или другая Linux система
- **Минимум**: 1GB RAM, 1 CPU, 10GB диск
- **Домен** для HTTPS (обязательно для Telegram!)

### 🔑 **Telegram**
- **Telegram Bot Token** от @BotFather
- **Доступ к настройкам бота** для установки Web App

## 🚀 Пошаговая инструкция

### 1️⃣ **Подготовка сервера**

#### Подключение к серверу:
```bash
ssh root@YOUR_SERVER_IP
```

#### Установка зависимостей:
```bash
# Обновляем систему
apt update && apt upgrade -y

# Устанавливаем Python и Git
apt install python3 python3-pip git nginx certbot python3-certbot-nginx -y

# Устанавливаем Node.js для фронтенда (опционально)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs
```

### 2️⃣ **Загрузка проекта на сервер**

```bash
# Создаем папку для проекта
mkdir /var/www/dolce-app
cd /var/www/dolce-app

# Загружаем ваш проект (несколько способов):

# СПОСОБ 1: Git (если загрузили в репозиторий)
git clone https://github.com/24vasilekk/dolce.git .

# СПОСОБ 2: SCP с локального компьютера
# scp -r /Users/filippakinitov/Desktop/EcommerceParser/* root@YOUR_SERVER_IP:/var/www/dolce-app/

# СПОСОБ 3: Создание архива и загрузка
# На локальном компьютере:
# tar -czf dolce-app.tar.gz EcommerceParser/
# scp dolce-app.tar.gz root@YOUR_SERVER_IP:/var/www/dolce-app/
# tar -xzf dolce-app.tar.gz
```

### 3️⃣ **Настройка Python окружения**

```bash
cd /var/www/dolce-app

# Устанавливаем зависимости
pip3 install flask flask-cors gunicorn requests selenium beautifulsoup4

# Устанавливаем Chrome для парсера (если нужно)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt update && apt install google-chrome-stable -y

# Устанавливаем ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
```

### 4️⃣ **Настройка домена и HTTPS**

#### Настройка Nginx:
```bash
# Создаем конфигурацию для сайта
cat > /etc/nginx/sites-available/dolce-app << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN.com;  # Замените на ваш домен
    
    location / {
        root /var/www/dolce-app/dolce;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Заголовки для Telegram WebApp
        add_header X-Frame-Options ALLOWALL;
        add_header Access-Control-Allow-Origin *;
    }
    
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Активируем сайт
ln -s /etc/nginx/sites-available/dolce-app /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

#### Установка SSL сертификата:
```bash
# Получаем SSL сертификат от Let's Encrypt
certbot --nginx -d YOUR_DOMAIN.com

# Автоматическое обновление сертификата
crontab -e
# Добавьте строку: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 5️⃣ **Настройка автозапуска API**

#### Создаем systemd сервис:
```bash
cat > /etc/systemd/system/dolce-api.service << 'EOF'
[Unit]
Description=Dolce API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/dolce-app
Environment=PYTHONPATH=/var/www/dolce-app
ExecStart=/usr/bin/python3 dolce_api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Запускаем сервис
systemctl daemon-reload
systemctl enable dolce-api
systemctl start dolce-api

# Проверяем статус
systemctl status dolce-api
```

### 6️⃣ **Настройка автоматического парсинга**

#### Создаем cron задачу для регулярного обновления товаров:
```bash
# Создаем скрипт для парсинга
cat > /var/www/dolce-app/run_parser.sh << 'EOF'
#!/bin/bash
cd /var/www/dolce-app
export DISPLAY=:99
python3 bestsecret_parser.py >> /var/log/dolce-parser.log 2>&1
EOF

chmod +x /var/www/dolce-app/run_parser.sh

# Добавляем в crontab (запуск каждые 6 часов)
crontab -e
# Добавьте строку: 0 */6 * * * /var/www/dolce-app/run_parser.sh
```

### 7️⃣ **Адаптация приложения для сервера**

#### Обновите URL API в приложении:
```bash
# Отредактируйте dolce/app_with_api.js
sed -i 's/localhost:5001/YOUR_DOMAIN.com/g' /var/www/dolce-app/dolce/app_with_api.js
```

#### Создайте production версию API сервера:
```bash
cat > /var/www/dolce-app/dolce_api_server_prod.py << 'EOF'
#!/usr/bin/env python3
"""
Production версия Dolce API Server для сервера
"""
import sys
sys.path.append('/var/www/dolce-app')

from dolce_api_server import app
import logging

# Настройка логирования для production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dolce-api.log'),
        logging.StreamHandler()
    ]
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
EOF

chmod +x /var/www/dolce-app/dolce_api_server_prod.py

# Обновляем systemd сервис
sed -i 's/dolce_api_server.py/dolce_api_server_prod.py/g' /etc/systemd/system/dolce-api.service
systemctl daemon-reload
systemctl restart dolce-api
```

### 8️⃣ **Настройка Telegram Bot**

#### Создание/настройка бота:
1. Идите к @BotFather в Telegram
2. Создайте нового бота или используйте существующего:
   ```
   /newbot
   Dolce Deals Bot
   dolce_deals_bot (или любое доступное имя)
   ```

#### Настройка Web App:
```
/setmenubutton
@your_bot_username
Выберите ваш бот
Button text: 🛍️ Открыть магазин
Web App URL: https://YOUR_DOMAIN.com
```

#### Дополнительные команды:
```
/setcommands
@your_bot_username

start - 🚀 Запустить магазин
shop - 🛍️ Открыть каталог товаров  
help - ❓ Помощь и поддержка
```

### 9️⃣ **Мониторинг и логи**

#### Настройка мониторинга:
```bash
# Просмотр логов API
tail -f /var/log/dolce-api.log

# Просмотр логов парсера
tail -f /var/log/dolce-parser.log

# Просмотр логов Nginx
tail -f /var/nginx/access.log

# Проверка статуса сервисов
systemctl status dolce-api nginx
```

#### Создание monitoring скрипта:
```bash
cat > /var/www/dolce-app/monitor.sh << 'EOF'
#!/bin/bash
echo "=== Dolce App Status ===" 
date
echo

echo "API Service:"
systemctl is-active dolce-api

echo "API Health Check:"
curl -s http://localhost:5001/api/health | python3 -m json.tool

echo "Nginx Status:"
systemctl is-active nginx

echo "Disk Space:"
df -h /var/www/dolce-app

echo "Memory Usage:"
free -h
EOF

chmod +x /var/www/dolce-app/monitor.sh

# Добавляем в crontab для ежедневного мониторинга
crontab -e
# Добавьте: 0 9 * * * /var/www/dolce-app/monitor.sh >> /var/log/dolce-monitor.log
```

## 🔧 Конфигурация для Telegram WebApp

### Обновите HTML для Telegram:
```bash
cat > /var/www/dolce-app/dolce/telegram_integration.js << 'EOF'
// Telegram WebApp интеграция
if (window.Telegram && window.Telegram.WebApp) {
    const tg = window.Telegram.WebApp;
    
    // Инициализация Telegram WebApp
    tg.ready();
    tg.expand();
    
    // Настройка темы
    document.body.style.backgroundColor = tg.themeParams.bg_color || '#ffffff';
    
    // Настройка главной кнопки
    tg.MainButton.setText('🛍️ В каталог');
    tg.MainButton.show();
    
    tg.MainButton.onClick(() => {
        if (window.app) {
            window.app.switchTab('home');
        }
    });
    
    // Обработка кнопки "Назад"
    tg.BackButton.onClick(() => {
        if (window.app && window.app.currentModal) {
            window.app.closeAllModals();
        } else {
            tg.close();
        }
    });
    
    // Отправка событий в Telegram
    document.addEventListener('DOMContentLoaded', () => {
        // Показываем кнопку "Назад" в модальных окнах
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                const modals = document.querySelectorAll('.modal:not(.hidden)');
                if (modals.length > 0) {
                    tg.BackButton.show();
                } else {
                    tg.BackButton.hide();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class']
        });
    });
}
EOF
```

### Добавьте интеграцию в HTML:
```bash
# Добавляем скрипт в index.html перед закрывающим </body>
sed -i '/<\/body>/i\    <script src="telegram_integration.js"><\/script>' /var/www/dolce-app/dolce/index.html
```

## ✅ Финальная проверка

### 1. Проверьте доступность:
```bash
curl https://YOUR_DOMAIN.com
curl https://YOUR_DOMAIN.com/api/health
```

### 2. Тест в Telegram:
1. Найдите ваш бот в Telegram
2. Нажмите `/start`  
3. Нажмите кнопку меню внизу "🛍️ Открыть магазин"
4. Приложение должно открыться с товарами

### 3. Проверьте автообновление:
```bash
# Проверьте что cron задачи работают
crontab -l
tail -f /var/log/dolce-parser.log
```

## 🔒 Безопасность

### Настройка файрвола:
```bash
ufw enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw status
```

### Настройка бэкапов:
```bash
cat > /root/backup_dolce.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /root/backups/dolce_backup_$DATE.tar.gz /var/www/dolce-app/
find /root/backups/ -name "dolce_backup_*.tar.gz" -mtime +7 -delete
EOF

mkdir -p /root/backups
chmod +x /root/backup_dolce.sh

# Автоматический бэкап каждый день
crontab -e
# Добавьте: 0 2 * * * /root/backup_dolce.sh
```

## 📞 Поддержка и отладка

### Частые проблемы:

**Приложение не загружается:**
```bash
# Проверьте логи Nginx
tail -f /var/nginx/error.log
systemctl status nginx
```

**API не работает:**
```bash
systemctl status dolce-api
tail -f /var/log/dolce-api.log
```

**SSL проблемы:**
```bash
certbot certificates
nginx -t
```

**Товары не обновляются:**
```bash
tail -f /var/log/dolce-parser.log
/var/www/dolce-app/run_parser.sh  # Ручной запуск
```

## 🎉 Готово!

После выполнения всех шагов у вас будет:

✅ **Рабочее приложение** на `https://YOUR_DOMAIN.com`  
✅ **API автоматически работает** 24/7  
✅ **Товары автообновляются** каждые 6 часов  
✅ **Telegram Bot** с Web App  
✅ **SSL сертификат** для безопасности  
✅ **Мониторинг и логи** для отладки  
✅ **Автоматические бэкапы** данных  

**Ваш Dolce Deals теперь работает как полноценный Telegram Mini App!** 🎊