# Third-party imports
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

# Local application imports
from src.models import model  # Import all models for SQLModel metadata

DATABASE_URL = "sqlite+aiosqlite:///data.sqlite3"

_engine: AsyncEngine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

async def create_db_and_tables():
    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

def get_engine() -> AsyncEngine:
    return _engine
