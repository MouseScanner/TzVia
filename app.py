from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session, create_tables, MovieReview
from schemas import ReviewCreate, ReviewResponse, SimilarityRequest, TaskResponse, TaskStatusResponse
from tasks import find_similar_reviews, add_review_task, app as celery_app
from model_training import model_manager
from cache import cache_manager
import logging
import asyncpg
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Movie Reviews Similarity API", version="1.0.0")

async def init_pgvector():
    """Инициализация расширения pgvector"""
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/movie_reviews")
    # Преобразуем URL для asyncpg
    asyncpg_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = await asyncpg.connect(asyncpg_url)
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        logger.info("pgvector extension created successfully")
        await conn.close()
    except Exception as e:
        logger.error(f"Error creating pgvector extension: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    # Сначала инициализируем pgvector
    await init_pgvector()
    # Затем создаем таблицы
    await create_tables()
    logger.info("Database tables created")

@app.post("/add_review", response_model=TaskResponse)
async def add_review(review: ReviewCreate):
    try:
        task = add_review_task.delay(review.text, review.sentiment)
        return TaskResponse(task_id=task.id)
    except Exception as e:
        logger.error(f"Error adding review: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/find_similar", response_model=TaskResponse)
async def find_similar(request: SimilarityRequest):
    try:
        task = find_similar_reviews.delay(request.text)
        return TaskResponse(task_id=task.id)
    except Exception as e:
        logger.error(f"Error finding similar reviews: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = TaskStatusResponse(
                task_id=task_id,
                status='PENDING',
                result=None
            )
        elif task_result.state == 'SUCCESS':
            response = TaskStatusResponse(
                task_id=task_id,
                status='SUCCESS',
                result=task_result.result
            )
        else:
            response = TaskStatusResponse(
                task_id=task_id,
                status=task_result.state,
                result=str(task_result.info)
            )
        
        return response
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/train_model")
async def train_model():
    try:
        model_manager.train_model()
        return {"message": "Model training completed"}
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail="Model training failed")

@app.post("/populate_database")
async def populate_database():
    try:
        await model_manager.populate_database()
        return {"message": "Database populated with IMDB data"}
    except Exception as e:
        logger.error(f"Error populating database: {e}")
        raise HTTPException(status_code=500, detail="Database population failed")

@app.delete("/cache")
async def clear_cache():
    try:
        cache_manager.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Cache clearing failed") 