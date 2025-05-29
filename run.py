import asyncio
import uvicorn
from database import create_tables
from model_training import model_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_system():
    logger.info("Создание таблиц базы данных...")
    await create_tables()
    
    logger.info("Дообучение модели...")
    model_manager.train_model()
    
    logger.info("Заполнение базы данных...")
    await model_manager.populate_database()
    
    logger.info("Инициализация завершена!")

def main():
    logger.info("Запуск инициализации системы...")
    asyncio.run(initialize_system())
    
    logger.info("Запуск FastAPI сервера...")
    uvicorn.run("app:app", host="0.0.0.0", port=83, reload=True)

if __name__ == "__main__":
    main() 