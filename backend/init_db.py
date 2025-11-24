"""
Скрипт для инициализации базы данных с тестовыми данными
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.db.base import Base
from app.models.module import Module
from app.models.user import User
from app.core.security import get_password_hash


async def init_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create test user
        test_user = await session.execute(
            select(User).where(User.username == "testdemo")
        )
        if not test_user.scalar_one_or_none():
            user = User(
                username="testdemo",
                email="test@example.com",
                hashed_password=get_password_hash("demotest")
            )
            session.add(user)
            await session.commit()
            print("Test user created: testdemo / demotest")
        
        # Create admin user
        admin_user = await session.execute(
            select(User).where(User.username == "admin")
        )
        if not admin_user.scalar_one_or_none():
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin"),
                is_superuser=True
            )
            session.add(admin)
            await session.commit()
            print("Admin user created: admin / admin")
        
        # Create test modules
        modules_data = [
            {
                "id": "Module_01",
                "title": "Введение в Python",
                "description": "Основы языка программирования Python",
                "total_lessons": 3,
                "order_index": 1
            },
            {
                "id": "Module_02",
                "title": "Продвинутый Python",
                "description": "Продвинутые концепции Python",
                "total_lessons": 3,
                "order_index": 2
            }
        ]
        
        for module_data in modules_data:
            existing = await session.execute(
                select(Module).where(Module.id == module_data["id"])
            )
            if not existing.scalar_one_or_none():
                module = Module(**module_data)
                session.add(module)
                await session.commit()
                print(f"Module created: {module_data['id']}")
    
    await engine.dispose()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
