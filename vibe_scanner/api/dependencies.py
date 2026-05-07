from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import AsyncSessionLocal

async def get_db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as session:
        yield session
