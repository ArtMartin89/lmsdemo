"""
Скрипт для проверки и инициализации базы данных
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from app.config import settings
from app.db.base import Base
from app.models.module import Module
from app.models.user import User
from app.core.security import get_password_hash, verify_password


async def check_and_init():
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✓ Database connection OK")
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Tables created/verified")
        
        # Create session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            # Check and create test user
            test_user = await session.execute(
                select(User).where(User.username == "testdemo")
            )
            user_obj = test_user.scalar_one_or_none()
            
            if not user_obj:
                user = User(
                    username="testdemo",
                    email="test@example.com",
                    hashed_password=get_password_hash("demotest"),
                    is_superuser=True  # С правами администратора
                )
                session.add(user)
                await session.commit()
                print("✓ Test user created with admin rights: testdemo / demotest")
            else:
                # Update to ensure admin rights
                if not user_obj.is_superuser:
                    user_obj.is_superuser = True
                # Verify password
                if verify_password("demotest", user_obj.hashed_password):
                    await session.commit()
                    print("✓ Test user exists with admin rights: testdemo / demotest")
                else:
                    # Reset password
                    user_obj.hashed_password = get_password_hash("demotest")
                    await session.commit()
                    print("✓ Test user password reset with admin rights: testdemo / demotest")
            
            # Check and create admin user
            admin_user = await session.execute(
                select(User).where(User.username == "admin")
            )
            admin_obj = admin_user.scalar_one_or_none()
            
            if not admin_obj:
                admin = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=get_password_hash("admin"),
                    is_superuser=True
                )
                session.add(admin)
                await session.commit()
                print("✓ Admin user created: admin / admin")
            else:
                # Verify password
                if verify_password("admin", admin_obj.hashed_password):
                    print("✓ Admin user exists and password is correct: admin / admin")
                else:
                    # Reset password
                    admin_obj.hashed_password = get_password_hash("admin")
                    await session.commit()
                    print("✓ Admin user password reset: admin / admin")
            
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
                    print(f"✓ Module created: {module_data['id']}")
                else:
                    print(f"✓ Module exists: {module_data['id']}")
        
        await engine.dispose()
        print("\n✅ Database initialized successfully!")
        print("\nAvailable users:")
        print("  - testdemo / demotest (admin)")
        print("  - admin / admin (admin)")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(check_and_init())
    sys.exit(0 if success else 1)


