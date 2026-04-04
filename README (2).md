# AnimeHako — Техническое Задание (MVP)

## 1. Описание проекта

**AnimeHako** — каталог аниме с личными списками и обзорами. Пет-проект для изучения fullstack-разработки.

### Компоненты

- **Бекенд** — монолитный REST API
- **Фронтенд** — веб-приложение
- **Мобильное приложение** — отдельно от фронтенда

### Функционал

| Функция | Описание |
|---------|----------|
| Каталог аниме | Главная страница со списком аниме |
| Карточка аниме | Описание, жанры, теги, оценка, обзоры, скриншоты |
| Авторизация | Регистрация и вход |
| Личный кабинет | Профиль и списки аниме |
| Списки просмотра | Просмотренное / Брошено / Смотрю / Запланировано |
| Любимое | Отметить аниме как любимое |
| Обзоры | Только просмотр обзоров |

---

## 2. Архитектура

### Стек технологий

**Бекенд:**
- Python + FastAPI
- PostgreSQL
- JWT для авторизации

**Фронтенд:**
- React
- Shadcn UI
- Zustand
- TanStack Query

**Мобильное приложение:**
- React Native

### Схема работы

```
Веб/Мобильное приложение → REST API → PostgreSQL
                                    ↓
                            Внешний API аниме
```

- Все данные хранятся в PostgreSQL
- Картинки (постеры, скриншоты) — URL из внешнего API
- Синхронизация с внешним API — по запросу или вручную

---

## 3. Бекенд

### API Эндпоинты

#### Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Вход |

#### Аниме

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/anime` | Список аниме (пагинация, фильтры) |
| GET | `/api/v1/anime/:id` | Детали аниме |
| GET | `/api/v1/anime/:id/screenshots` | Скриншоты |
| GET | `/api/v1/anime/:id/reviews` | Обзоры |
| GET | `/api/v1/genres` | Список жанров |
| GET | `/api/v1/tags` | Список тегов |

#### Пользователь (требуется авторизация)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/user/me` | Профиль |
| PATCH | `/api/v1/user/me` | Обновить профиль |
| GET | `/api/v1/user/anime` | Мой список аниме |
| POST | `/api/v1/user/anime` | Добавить в список |
| PATCH | `/api/v1/user/anime/:animeId` | Обновить статус |
| DELETE | `/api/v1/user/anime/:animeId` | Удалить из списка |
| POST | `/api/v1/user/favorites/:animeId` | Добавить в любимое |
| DELETE | `/api/v1/user/favorites/:animeId` | Убрать из любимого |

#### Обзоры

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/anime/:id/reviews` | Получить обзоры аниме |
| GET | `/api/v1/reviews/:id` | Получить конкретный обзор |

### Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Bad Request — неверные данные |
| 401 | Unauthorized — не авторизован |
| 404 | Not Found — не найдено |
| 500 | Internal Server Error |

### Форматы данных

#### Регистрация / Вход

```json
// Запрос
{
  "email": "user@example.com",
  "username": "animefan",
  "password": "hashed_password"
}

// Ответ
{
  "token": "jwt_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "animefan",
    "avatar": null
  }
}
```

> **Примечание:** Пароль передаётся в открытом виде (HTTPS) и хешируется на сервере с использованием bcrypt.

#### Список аниме

```json
{
  "data": [
    {
      "id": 1,
      "title": "Название аниме",
      "titleEn": "Anime Title",
      "poster": "https://example.com/poster.jpg",
      "rating": 8.5,
      "year": 2024,
      "episodes": 12,
      "genres": ["Экшен", "Фэнтези"]
    }
  ],
  "page": 1,
  "totalPages": 10,
  "total": 200
}
```

#### Детали аниме

```json
{
  "id": 1,
  "title": "Название аниме",
  "titleEn": "Anime Title",
  "titleJp": "アニメタイトル",
  "poster": "https://example.com/poster.jpg",
  "cover": "https://example.com/cover.jpg",
  "description": "Описание аниме...",
  "rating": 8.5,
  "year": 2024,
  "season": "winter",
  "status": "ongoing",
  "episodes": 12,
  "duration": 24,
  "studio": "Studio Name",
  "genres": ["Экшен", "Фэнтези"],
  "tags": ["Исекай", "Магия"]
}
```

#### Аниме в списке пользователя

```json
{
  "animeId": 1,
  "status": "watching",
  "score": 8,
  "episodesWatched": 5,
  "isFavorite": true
}
```

#### Обзор

```json
{
  "id": 1,
  "animeId": 1,
  "authorName": "Автор обзора",
  "title": "Заголовок",
  "content": "Текст обзора...",
  "score": 9,
  "createdAt": "2026-03-05T10:00:00Z"
}
```

### Параметры запроса

#### GET /api/v1/anime

| Параметр | Описание |
|----------|----------|
| `page` | Номер страницы |
| `search` | Поиск по названию |
| `genres` | Фильтр по жанрам (через запятую) |
| `year` | Фильтр по году |
| `sort` | Сортировка: rating, year, created |

#### GET /api/v1/user/anime

| Параметр | Описание |
|----------|----------|
| `status` | Фильтр: watching, completed, dropped, planned |

---

## 4. База данных

### Таблицы

#### users

| Поле | Тип |
|------|-----|
| id | SERIAL PRIMARY KEY |
| email | VARCHAR(255) UNIQUE |
| username | VARCHAR(50) UNIQUE |
| password_hash | VARCHAR(255) |
| avatar | VARCHAR(500) |
| created_at | TIMESTAMP |

#### anime

| Поле | Тип |
|------|-----|
| id | SERIAL PRIMARY KEY |
| title | VARCHAR(255) |
| title_en | VARCHAR(255) |
| title_jp | VARCHAR(255) |
| poster | VARCHAR(500) |
| cover | VARCHAR(500) |
| description | TEXT |
| rating | DECIMAL(3,1) |
| year | INT |
| season | VARCHAR(20) |
| status | VARCHAR(20) |
| episodes | INT |
| duration | INT |
| studio | VARCHAR(255) |
| created_at | TIMESTAMP |

**Индексы:** `idx_anime_rating`, `idx_anime_year`

| Поле | Тип |
|------|-----|
| id | SERIAL PRIMARY KEY |
| user_id | INT REFERENCES users |
| anime_id | INT REFERENCES anime |
| status | VARCHAR(20) |
| score | INT |
| episodes_watched | INT |
| is_favorite | BOOLEAN DEFAULT false |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

**Индексы:** `idx_user_anime_user_id`, `idx_user_anime_status`

**Уникальность:** (user_id, anime_id)

#### reviews

*Обзоры импортируются из внешнего источника или добавляются администратором. Пользователи могут только просматривать обзоры.*

| Поле | Тип |
|------|-----|
| id | SERIAL PRIMARY KEY |
| anime_id | INT REFERENCES anime |
| author_name | VARCHAR(255) |
| title | VARCHAR(255) |
| content | TEXT |
| score | INT |
| external_id | VARCHAR(100) |
| created_at | TIMESTAMP |

#### screenshots

| Поле | Тип |
|------|-----|
| id | SERIAL PRIMARY KEY |
| anime_id | INT REFERENCES anime |
| url | VARCHAR(500) |

#### genres

| Поле | Тип |
|------|-----|
| id | SERIAL PRIMARY KEY |
| name | VARCHAR(100) UNIQUE |
| slug | VARCHAR(100) UNIQUE |

#### tags

| Поле | Тип |
|------|-----|
| id | SERIAL PRIMARY KEY |
| name | VARCHAR(100) UNIQUE |
| slug | VARCHAR(100) UNIQUE |

#### anime_genres

| Поле | Тип |
|------|-----|
| anime_id | INT REFERENCES anime |
| genre_id | INT REFERENCES genres |

#### anime_tags

| Поле | Тип |
|------|-----|
| anime_id | INT REFERENCES anime |
| tag_id | INT REFERENCES tags |

---

## 5. Фронтенд

### Страницы

| Маршрут | Страница |
|---------|----------|
| `/` | Главная — каталог аниме |
| `/anime/:id` | Карточка аниме |
| `/login` | Вход |
| `/register` | Регистрация |
| `/profile` | Личный кабинет |
| `/profile/anime` | Мой список |
| `/profile/favorites` | Любимое |

### Компоненты (поверх Shadcn UI)

**Аниме:**
- `AnimeCard` — карточка с постером и рейтингом
- `AnimeGrid` — сетка карточек
- `AnimeScreenshots` — галерея скриншотов
- `GenreBadge` — бейдж жанра
- `RatingDisplay` — рейтинг звёздами

**Пользователь:**
- `UserAvatar` — аватар
- `StatusSelect` — выбор статуса аниме
- `FavoriteButton` — кнопка любимого

**Формы:**
- `LoginForm` — форма входа
- `RegisterForm` — форма регистрации

### Функциональность страниц

#### Главная
- Сетка аниме с пагинацией
- Фильтры: поиск, жанры, год
- Сортировка: по рейтингу, году

#### Карточка аниме
- Постер, обложка, описание
- Информация: год, студия, эпизоды
- Жанры и теги (кликабельные)
- Скриншоты (галерея)
- Обзоры (только просмотр)
- Кнопки: добавить в список, в любимое

#### Личный кабинет
- Профиль: аватар, имя, email
- Статистика: сколько просмотрено
- Табы: Смотрю / Просмотренное / Брошено / Запланировано

---

## 6. Мобильное приложение

### Экраны

| Экран | Описание |
|-------|----------|
| Home | Каталог с каруселями |
| Search | Поиск |
| AnimeDetail | Карточка аниме |
| Profile | Личный кабинет |
| Login / Register | Авторизация |

### Навигация

TabBar: Главная | Поиск | Профиль

### Особенности

- Горизонтальные карусели на главной
- Бесконечная прокрутка списков
- Pull-to-refresh
- Галерея скриншотов с зумом

---

## 7. Интеграция с внешним API

### Подход

- Создать простой сервис-адаптер
- При запросе аниме проверять наличие в БД
- Если нет — загрузить из внешнего API и сохранить
- Картинки хранить как URL (не загружать локально)

### Пример адаптера

```typescript
interface AnimeProvider {
  getAnime(id: string): Promise<AnimeData>;
  searchAnime(query: string): Promise<AnimeData[]>;
  getGenres(): Promise<Genre[]>;
}
```

### Провайдеры на выбор

- Shikimori API
- Kitsu API
- Jikan API (MyAnimeList)

---