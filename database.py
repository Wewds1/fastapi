from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings

# Update to use postgresql+asyncpg for asynchronous communication
async_db_url = settings.DATABASE_URL
if async_db_url and not async_db_url.startswith("postgresql+asyncpg"):
    async_db_url = async_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    async_db_url = async_db_url

engine = create_async_engine(async_db_url, echo=True)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
