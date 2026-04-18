from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database URL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# Database engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Session factory
AsyncSessionFactory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for declarative models
class Base(DeclarativeBase):
    pass
