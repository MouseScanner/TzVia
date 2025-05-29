# Movie Reviews Similarity API

Сервис для поиска похожих отзывов о фильмах с использованием DistilBERT и векторного поиска.

## Технологический стек

- **FastAPI** - веб-фреймворк
- **PostgreSQL + pgvector** - база данных с векторным поиском
- **Redis + Celery** - асинхронная обработка задач
- **DistilBERT** - модель для создания векторных представлений
- **SQLAlchemy 2.0** - ORM с асинхронной поддержкой

## Установка и запуск

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Запуск всех сервисов
docker-compose up --build
```

### Вариант 2: Локальная установка

1. Установка зависимостей:
```bash
pip install -r requirements.txt
```

2. Запуск PostgreSQL с pgvector:
```bash
# Docker для PostgreSQL
docker run --name postgres-pgvector -e POSTGRES_PASSWORD=password -e POSTGRES_DB=movie_reviews -p 5432:5432 -d pgvector/pgvector:pg15
```

3. Запуск Redis:
```bash
docker run --name redis -p 6379:6379 -d redis:7-alpine
```

4. Инициализация базы данных:
```bash
python init_db.py
```

5. Запуск сервисов:
```bash
# Терминал 1: FastAPI. Порт 83 тестово используется в данном месте. 
uvicorn app:app --reload --port 83

# Терминал 2: Celery Worker
celery -A tasks worker --loglevel=info
```

## API Endpoints

### POST /add_review
Добавление нового отзыва в базу данных.

**Запрос:**
```json
{
    "text": "This movie was amazing!",
    "sentiment": 1
}
```

**Ответ:**
```json
{
    "task_id": "task-uuid"
}
```

### POST /find_similar
Поиск похожих отзывов по тексту.

**Запрос:**
```json
{
    "text": "Great movie with excellent acting"
}
```

**Ответ:**
```json
{
    "task_id": "task-uuid"
}
```

### GET /status/{task_id}
Проверка статуса выполнения задачи.

**Ответ:**
```json
{
    "task_id": "task-uuid",
    "status": "SUCCESS",
    "result": [
        {
            "text": "Similar review text",
            "sentiment": 1,
            "distance": 0.15
        }
    ]
}
```

### POST /train_model
Дообучение модели DistilBERT на датасете IMDB.

### POST /populate_database
Заполнение базы данных тестовыми данными из IMDB.

### GET /health
Проверка состояния сервиса.

## Использование

1. Запустите сервисы
2. Дообучить модель: `POST /train_model`
3. Заполнить базу данных: `POST /populate_database`
4. Использовать API для поиска похожих отзывов

## Пример использования

```bash
# Добавление отзыва
curl -X POST "http://localhost:8000/add_review" \
     -H "Content-Type: application/json" \
     -d '{"text":"This movie was amazing!", "sentiment":1}'

# Поиск похожих отзывов
curl -X POST "http://localhost:8000/find_similar" \
     -H "Content-Type: application/json" \
     -d '{"text":"Great film with excellent story"}'

# Проверка статуса задачи
curl "http://localhost:8000/status/task-id"
```

## Тестирование

```bash
pytest test_api.py
```

## Архитектура

- **app.py** - основное FastAPI приложение
- **database.py** - модели и подключение к БД
- **tasks.py** - Celery задачи
- **model_training.py** - работа с ML моделями
- **schemas.py** - Pydantic схемы
- **init_db.py** - инициализация БД

## Переменные окружения

- `DATABASE_URL` - строка подключения к PostgreSQL
- `REDIS_URL` - строка подключения к Redis 