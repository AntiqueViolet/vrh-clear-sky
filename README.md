# vrh-clear-sky

## 📌 Описание
**vrh-clear-sky** — сервис для автоматического обновления данных виджета **Rosstrah**. Приложение:
- Выполняет **единоразовое обновление данных** при старте контейнера.
- Подключается к MySQL, извлекает данные о пользователях и их менеджерах.
- Сохраняет результат в целевую таблицу через **SQLAlchemy**.
- Поддерживает периодическое обновление с помощью **cron**.

---

## 🛠️ Стек технологий
- **Python 3.11+**
- **Pandas**, **SQLAlchemy**, **PyMySQL**
- **Docker & Docker Compose**
- **GitHub Actions** (CI/CD)
- **Cron** для планирования задач

---

## 📂 Структура проекта
```
├── Dockerfile             # Сборка Docker-образа
├── docker-compose.yml     # Запуск сервиса
├── docker-publish.yml     # GitHub Actions Workflow (CI/CD)
├── entrypoint.sh          # Стартовый скрипт (единоразовый запуск + cron)
├── cronjob                # Файл с расписанием cron
├── update_vidget_rosstrah.py # Основной Python-скрипт (first_update + обновление)
├── req.txt                # Python-зависимости
└── README.md
```

---

## ⚙️ Установка и запуск

### ✅ Локальный запуск
```bash
git clone <repo_url>
cd vrh-clear-sky
pip install -r req.txt

# Задаем переменные окружения
export DB_USER=user
export DB_PASSWORD=pass
export DB_HOST=host
export DB_PORT=3366
export DB_DATABASE=db
export DB_URI="mysql+pymysql://user:pass@host:3306/target_db"
export TARGET_TABLE="Vidget_Rosstrah_AgentManager"

# Единоразовое обновление
python update_vidget_rosstrah.py
```

---

### ✅ Запуск в Docker
#### 1. Сборка образа
```bash
docker build -t vrh-clear-sky:latest .
```
#### 2. Запуск через docker-compose
```bash
docker-compose up -d
```

**Пример docker-compose.yml**
```yaml
version: '3.8'
services:
  vrh-clear-sky:
    build: .
    container_name: vrh-clear-sky
    restart: always
    environment:
      DB_USER: user
      DB_PASSWORD: pass
      DB_HOST: host
      DB_PORT: 3366
      DB_DATABASE: db
      DB_URI: mysql+pymysql://user:pass@host:3306/target_db
      TARGET_TABLE: Vidget_Rosstrah_AgentManager
    volumes:
      - ./logs:/var/log
```

---

## ⏱️ Cron (периодическое обновление)
- **Единоразовое обновление** выполняется в `entrypoint.sh` при старте контейнера:
```sh
python /app/update_vidget_rosstrah.py || exit 1
```
- Затем запускается `crond`, который читает расписание из файла `cronjob`.

**Пример cronjob (ежедневное обновление в 00:00):**
```
0 0 * * * /usr/local/bin/python /app/update_vidget_rosstrah.py >> /var/log/cron.log 2>&1
```

---

## 🔒 Переменные окружения
| Переменная       | Описание                                  | Обязательна |
|-------------------|-------------------------------------------|-------------|
| `DB_USER`      | Пользователь MySQL                       | ✅          |
| `DB_PASSWORD`  | Пароль                                   | ✅          |
| `DB_HOST`      | Хост MySQL                               | ✅          |
| `DB_PORT`      | Порт MySQL (по умолчанию 3366)          | ❌          |
| `DB_DATABASE`  | База данных                              | ✅          |
| `DB_URI`          | URI подключения SQLAlchemy              | ✅          |
| `TARGET_TABLE`    | Таблица для записи данных (default: Vidget_Rosstrah_AgentManager) | ❌ |

---

## 🔄 CI/CD
Файл `.github/workflows/docker-publish.yml`:
- Сборка Docker-образа
- Публикация в Docker Hub/GitHub Container Registry
- Тегирование версии

---

## 📜 Логирование
- **cron** → `/var/log/cron.log`
- **Python** → STDOUT (`docker logs`)

---
