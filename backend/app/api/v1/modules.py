from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.crud.module import get_all_modules, get_module
from app.schemas.module import ModuleResponse

router = APIRouter()


@router.get("", response_model=list[ModuleResponse])
async def list_modules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available modules"""
    modules = await get_all_modules(db)
    return modules


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module_details(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get module details"""
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return module


@router.post("/{module_id}/start", status_code=status.HTTP_200_OK)
async def start_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a module"""
    from app.services.progress_service import ProgressService
    from app.crud.module import get_module
    from app.crud.progress import get_user_progress
    
    progress_service = ProgressService(db)
    
    # Check if module exists
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check if progress already exists
    existing_progress = await get_user_progress(db, current_user.id, module_id)
    
    if existing_progress:
        return {
            "status": "already_started",
            "message": "Module already started",
            "progress_id": str(existing_progress.id)
        }
    
    # Create progress
    progress = await progress_service.create_user_progress(
        current_user.id,
        module_id,
        module.total_lessons
    )
    
    return {
        "status": "started",
        "message": "Module started successfully",
        "progress_id": str(progress.id)
    }

