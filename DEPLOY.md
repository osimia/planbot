# Деплой Telegram-бота MyPlan на VPS (Linux, systemd)

## 1. Клонирование и подготовка

```bash
git clone <YOUR_REPO_URL> myplan-bot
cd myplan-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Настройка переменных окружения

- Скопируйте `.env.example` в `.env` и заполните:
  - `BOT_TOKEN` — токен Telegram-бота
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` — данные PostgreSQL

## 3. Настройка PostgreSQL

- Создайте базу и пользователя:
```sql
CREATE DATABASE myplan;
CREATE USER myplan_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE myplan TO myplan_user;
```
- Проверьте доступность из бота (`DB_HOST=localhost` или внешний адрес)

## 4. Автозапуск через systemd

Создайте файл `/etc/systemd/system/myplan-bot.service`:

```ini
[Unit]
Description=MyPlan Telegram Bot
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/myplan-bot
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/path/to/myplan-bot/.env
ExecStart=/path/to/myplan-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

- Проверьте пути, пользователя и права доступа!
- Запустите:
```bash
sudo systemctl daemon-reload
sudo systemctl enable myplan-bot
sudo systemctl start myplan-bot
sudo systemctl status myplan-bot
```

## 5. Логи
- Смотрите логи:
```bash
journalctl -u myplan-bot -f
```

## 6. Безопасность
- Не храните секреты в открытом виде, используйте `.env` и ограничьте права.
- Используйте firewall (ufw, firewalld) и сложные пароли.

## 7. Обновление
- Для обновления:
```bash
git pull
pip install -r requirements.txt
sudo systemctl restart myplan-bot
```

---

**Подробности и советы — в README.markdown**
