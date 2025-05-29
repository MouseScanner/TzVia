import asyncio
import asyncpg
import os

async def init_database():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/movie_reviews")
    # Преобразуем URL для asyncpg
    asyncpg_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    print(f"Connecting to: {asyncpg_url}")
    
    try:
        conn = await asyncpg.connect(asyncpg_url)
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("pgvector extension created successfully")
        await conn.close()
    except Exception as e:
        print(f"Error creating pgvector extension: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database()) 