from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

DATABASE_URI = str(settings.SQLALCHEMY_DATABASE_URI).replace(
    "postgresql+psycopg", "postgresql+asyncpg"
)

engine = create_async_engine(DATABASE_URI, echo=False, future=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
