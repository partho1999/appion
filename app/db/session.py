from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # type: ignore  # Ignore linter error if package is installed
from sqlalchemy.orm import sessionmaker  # type: ignore
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 