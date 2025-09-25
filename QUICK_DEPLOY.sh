#!/bin/bash
# 🚀 Быстрый деплой Dolce Deals на сервер

echo "🌟 НАЧИНАЕМ ДЕПЛОЙ DOLCE DEALS НА СЕРВЕР"
echo "========================================="

# Проверяем что скрипт запущен на сервере
if [[ $EUID -ne 0 ]]; then
   echo "❌ Запустите скрипт с правами root: sudo $0" 
   exit 1
fi

# Запрашиваем домен
read -p "🌐 Введите ваш домен (example.com): " DOMAIN
if [[ -z "$DOMAIN" ]]; then
    echo "❌ Домен не может быть пустым!"
    exit 1
fi

# Создаем папки
echo "📁 Создаем структуру проекта..."
mkdir -p /var/www/dolce-app
mkdir -p /var/log/dolce
mkdir -p /root/backups

# Обновляем систему
echo "🔄 Обновляем систему..."
apt update && apt upgrade -y

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
apt install python3 python3-pip git nginx certbot python3-certbot-nginx curl unzip -y

# Python пакеты
pip3 install flask flask-cors gunicorn requests selenium beautifulsoup4

# Chrome для парсинга
echo "🌐 Устанавливаем Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt update && apt install google-chrome-stable -y

# ChromeDriver
echo "🔧 Устанавливаем ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Nginx конфигурация
echo "🔧 Настраиваем Nginx..."
cat > /etc/nginx/sites-available/dolce-app << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location / {
        root /var/www/dolce-app/dolce;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        add_header X-Frame-Options ALLOWALL;
        add_header Access-Control-Allow-Origin *;
    }
    
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/dolce-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Systemd сервис для API
echo "⚙️ Настраиваем systemd сервис..."
cat > /etc/systemd/system/dolce-api.service << EOF
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
StandardOutput=append:/var/log/dolce/api.log
StandardError=append:/var/log/dolce/api.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dolce-api

# Создаем скрипт для парсинга
echo "🕷️ Настраиваем автопарсинг..."
cat > /var/www/dolce-app/run_parser.sh << 'EOF'
#!/bin/bash
cd /var/www/dolce-app
export DISPLAY=:99
python3 bestsecret_parser.py >> /var/log/dolce/parser.log 2>&1
EOF

chmod +x /var/www/dolce-app/run_parser.sh

# Настраиваем cron
echo "⏰ Настраиваем автоматические задачи..."
(crontab -l 2>/dev/null; echo "0 */6 * * * /var/www/dolce-app/run_parser.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * tar -czf /root/backups/dolce_\$(date +%Y%m%d).tar.gz /var/www/dolce-app/") | crontab -

# Настраиваем файрвол
echo "🔒 Настраиваем безопасность..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'

# Создаем скрипт мониторинга
cat > /var/www/dolce-app/status.sh << 'EOF'
#!/bin/bash
echo "=== DOLCE APP STATUS ==="
date
echo
echo "Services:"
echo "API: $(systemctl is-active dolce-api)"
echo "Nginx: $(systemctl is-active nginx)"
echo
echo "API Health:"
curl -s http://localhost:5001/api/health 2>/dev/null | python3 -c "import sys,json; print('✅ OK' if json.load(sys.stdin).get('status')=='healthy' else '❌ Error')" 2>/dev/null || echo "❌ API не отвечает"
echo
echo "Disk Usage:"
df -h /var/www/dolce-app | tail -1
echo
echo "Last Parser Run:"
if [[ -f /var/log/dolce/parser.log ]]; then
    tail -1 /var/log/dolce/parser.log
else
    echo "Парсер еще не запускался"
fi
EOF

chmod +x /var/www/dolce-app/status.sh

echo ""
echo "✅ СЕРВЕР НАСТРОЕН!"
echo "=================="
echo ""
echo "📋 ЧТО ДАЛЬШЕ:"
echo "1. Загрузите ваши файлы в /var/www/dolce-app/"
echo "   scp -r EcommerceParser/* root@$DOMAIN:/var/www/dolce-app/"
echo ""
echo "2. Обновите URL в приложении:"
echo "   sed -i 's/localhost:5001/$DOMAIN/g' /var/www/dolce-app/dolce/app_with_api.js"
echo ""
echo "3. Запустите сервисы:"
echo "   systemctl start dolce-api"
echo ""
echo "4. Получите SSL сертификат:"
echo "   certbot --nginx -d $DOMAIN"
echo ""
echo "5. Настройте Telegram Bot:"
echo "   - Идите к @BotFather"
echo "   - /setmenubutton"
echo "   - Web App URL: https://$DOMAIN"
echo ""
echo "🔍 ПРОВЕРКА СТАТУСА:"
echo "   /var/www/dolce-app/status.sh"
echo ""
echo "📂 ВАЖНЫЕ ФАЙЛЫ:"
echo "   Логи API: /var/log/dolce/api.log"
echo "   Логи парсера: /var/log/dolce/parser.log"
echo "   Конфиг Nginx: /etc/nginx/sites-available/dolce-app"
echo "   Systemd сервис: /etc/systemd/system/dolce-api.service"
echo ""
echo "🎉 ГОТОВО К РАБОТЕ!"