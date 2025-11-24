from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis

from app.api.v1 import auth, modules, lessons, tests, progress
from app.config import settings
from app.db.session import engine
from app.db.base import Base

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # Create tables (in production use Alembic)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")
    
    # Initialize Redis
    try:
        app.state.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    except Exception as e:
        print(f"Warning: Could not connect to Redis: {e}")
        app.state.redis = None
    
    yield
    
    # Shutdown
    if app.state.redis:
        await app.state.redis.close()

app = FastAPI(
    title="LMS Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
# Handle ALLOWED_ORIGINS as list or string
allowed_origins = settings.ALLOWED_ORIGINS
if isinstance(allowed_origins, str):
    # Split by comma if it's a comma-separated string
    allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(modules.router, prefix="/api/v1/modules", tags=["modules"])
app.include_router(lessons.router, prefix="/api/v1", tags=["lessons"])
app.include_router(tests.router, prefix="/api/v1", tags=["tests"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

