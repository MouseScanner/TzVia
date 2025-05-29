from dotenv import load_dotenv
load_dotenv()

import asyncio
import asyncpg
import os

async def check_database():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/movie_reviews")
    asyncpg_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    print(f"Проверка подключения к: {asyncpg_url}")
    
    try:
        conn = await asyncpg.connect(asyncpg_url)
        print("✅ Подключение к базе данных успешно")
        
        # Проверяем наличие расширения vector
        result = await conn.fetch("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if result:
            print("✅ Расширение pgvector установлено")
        else:
            print("❌ Расширение pgvector НЕ установлено")
            print("Попытка установки...")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ Расширение pgvector установлено")
        
        # Проверяем версию PostgreSQL
        version = await conn.fetchval("SELECT version();")
        print(f"📊 Версия PostgreSQL: {version}")
        
        await conn.close()
        print("✅ Проверка завершена успешно")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Возможные решения:")
        print("1. Убедитесь, что PostgreSQL запущен")
        print("2. Проверьте правильность данных подключения")
        print("3. Используйте PostgreSQL с поддержкой pgvector:")
        print("   docker run --name postgres-pgvector -e POSTGRES_PASSWORD=password -e POSTGRES_DB=movie_reviews -p 5432:5432 -d pgvector/pgvector:pg15")

if __name__ == "__main__":
    asyncio.run(check_database()) 