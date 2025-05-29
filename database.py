from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text
from pgvector.sqlalchemy import Vector
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/movie_reviews")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class MovieReview(Base):
    __tablename__ = 'movie_reviews'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    sentiment = Column(Integer)
    embedding = Column(Vector(768))

async def get_session():
    async with async_session_maker() as session:
        yield session

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 