# 🚀 Как залить Dolce Deals на сервер для Telegram Mini App

## 📱 Быстрый старт (5 минут)

### 1. Купите сервер и домен
- **Сервер**: DigitalOcean, Beget, Timeweb (от $5/месяц)
- **Домен**: reg.ru, namecheap.com (от $10/год)
- **Минимум**: 1GB RAM, Ubuntu 20.04

### 2. Подключитесь к серверу
```bash
ssh root@YOUR_SERVER_IP
```

### 3. Запустите автоустановку
```bash
# Скачайте и запустите скрипт
wget https://raw.githubusercontent.com/24vasilekk/dolce/main/QUICK_DEPLOY.sh
chmod +x QUICK_DEPLOY.sh
./QUICK_DEPLOY.sh

# Введите ваш домен когда спросит
```

### 4. Загрузите файлы проекта
```bash
# С вашего компьютера:
scp -r /Users/filippakinitov/Desktop/EcommerceParser/* root@YOUR_DOMAIN:/var/www/dolce-app/
```

### 5. Обновите настройки
```bash
# На сервере:
cd /var/www/dolce-app
sed -i 's/localhost:5001/YOUR_DOMAIN/g' dolce/app_with_api.js
systemctl start dolce-api
```

### 6. Получите SSL сертификат
```bash
certbot --nginx -d YOUR_DOMAIN
```

### 7. Настройте Telegram Bot
1. Идите к @BotFather
2. Выберите ваш бот
3. `/setmenubutton`
4. `Web App URL: https://YOUR_DOMAIN`

## ✅ Готово!
Ваше приложение работает на `https://YOUR_DOMAIN` и доступно в Telegram!

---

## 📚 Подробная инструкция

Смотрите файл `TELEGRAM_DEPLOY_GUIDE.md` для детальных шагов.

## 🔧 Управление после деплоя

### Проверить статус:
```bash
/var/www/dolce-app/status.sh
```

### Перезапустить API:
```bash
systemctl restart dolce-api
```

### Посмотреть логи:
```bash
tail -f /var/log/dolce/api.log
tail -f /var/log/dolce/parser.log
```

### Обновить товары:
```bash
/var/www/dolce-app/run_parser.sh
```

## 📞 Поддержка

Если что-то не работает:
1. Проверьте логи: `/var/log/dolce/`
2. Проверьте сервисы: `systemctl status dolce-api nginx`
3. Проверьте домен: `curl https://YOUR_DOMAIN/api/health`

## 🎯 Что получится

✅ Приложение работает 24/7  
✅ Товары обновляются каждые 6 часов  
✅ SSL сертификат для безопасности  
✅ Автоматические бэкапы  
✅ Мониторинг и логи  
✅ Интеграция с Telegram  

**Ваш магазин теперь в Telegram!** 🎉