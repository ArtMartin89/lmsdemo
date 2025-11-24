"""
Скрипт для пересоздания таблиц базы данных
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings
from app.db.base import Base

# Import all models to ensure they are registered with Base
from app.models.user import User
from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.progress import UserProgress
from app.models.test import TestResult


async def recreate_tables():
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        
        # Drop all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("✓ All tables dropped")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ All tables created")
        
        await engine.dispose()
        print("\n✅ Tables recreated successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(recreate_tables())
    sys.exit(0 if success else 1)

