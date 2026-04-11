# Запуск (Windows)

## Требования

- Python 3.10+
- PostgreSQL 14+
- Утилита psql (входит в состав PostgreSQL)

---

## PostgreSQL

### Установка

1. Скачайте PostgreSQL с https://www.postgresql.org/download/windows/
2. Запустите установщик
3. Укажите пароль для пользователя `postgres` (например, `123456`)

### Создание БД

1. Откройте **SQL Shell (psql)** или pgAdmin
2. Выполните команды:
   ```sql
   CREATE DATABASE animehako;
   ```
3. Для импорта схемы:
   ```sql
   \i anime.sql
   ```

---

## Бекенд

### Установка зависимостей

```powershell
# Создать виртуальное окружение
python -m venv venv

# Активировать
.\venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt
```


### Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://postgres:123456@localhost:5432/animehako
SECRET_KEY=your_secret_key_here
```

> **Примечание:** Замените `123456` на ваш пароль postgres.

### Запуск

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Сервер будет доступен по адресу http://127.0.0.1:8000

Документация API: http://127.0.0.1:8000/docs