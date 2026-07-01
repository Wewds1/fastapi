from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings

# content_service should ideally have its own database URL in the future
# For now, we can use a different database name or a separate schema
db_url = settings.DATABASE_URL.replace("product", "content_db")

engine = create_async_engine(db_url, echo=True)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
