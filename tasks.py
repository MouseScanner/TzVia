from celery import Celery
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from database import MovieReview, Base
from model_training import model_manager
from cache import cache_manager
import os
import sys

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/movie_reviews")

# Синхронное подключение для Celery
sync_db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("asyncpg", "psycopg2")
sync_engine = create_engine(sync_db_url)
SyncSession = sessionmaker(bind=sync_engine)

app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

# Windows-совместимые настройки
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool='solo' if sys.platform == 'win32' else 'prefork',
    worker_concurrency=1 if sys.platform == 'win32' else 4,
)

@app.task
def find_similar_reviews(input_text: str):
    try:
        # Проверяем кэш
        cached_result = cache_manager.get_cached_result(input_text)
        if cached_result:
            return cached_result
        
        # Получаем эмбеддинг
        embedding = model_manager.get_embedding(input_text)
        
        # Синхронная работа с БД
        with SyncSession() as session:
            # Используем L2 distance вместо cosine
            query = text("""
                SELECT text, sentiment, embedding <-> :embedding as distance
                FROM movie_reviews 
                ORDER BY embedding <-> :embedding
                LIMIT 3
            """)
            
            # Преобразуем в правильный формат для pgvector
            embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
            embedding_str = '[' + ','.join(map(str, embedding_list)) + ']'
            
            result = session.execute(query, {"embedding": embedding_str})
            similar_reviews = []
            
            for row in result:
                similar_reviews.append({
                    "text": row.text,
                    "sentiment": row.sentiment,
                    "distance": float(row.distance)
                })
            
            # Кэшируем результат
            cache_manager.cache_result(input_text, similar_reviews)
            return similar_reviews
            
    except Exception as e:
        return {"error": str(e)}

@app.task
def add_review_task(text: str, sentiment: int):
    try:
        # Получаем эмбеддинг
        embedding = model_manager.get_embedding(text)
        
        # Синхронная работа с БД
        with SyncSession() as session:
            review = MovieReview(
                text=text,
                sentiment=sentiment,
                embedding=embedding.tolist()
            )
            session.add(review)
            session.commit()
            return {"id": review.id, "text": text, "sentiment": sentiment}
            
    except Exception as e:
        return {"error": str(e)} 