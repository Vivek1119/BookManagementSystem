# =============================================================================================
#                                             Database
# =============================================================================================

# inbuilt imports
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST= os.getenv("DB_HOST")
DB_PORT= os.getenv("DB_PORT")
DB_NAME= os.getenv("DB_NAME")

class Database:
    def __init__(self):
        database_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        self.engine = create_async_engine(database_url, echo=True)
        self.async_session = sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )
        self.Base = declarative_base()

    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            yield session


    async def connect_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)


db = Database()
