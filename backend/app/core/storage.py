import json
import os
from typing import Optional, Dict, Any
from pathlib import Path

from app.config import settings


class StorageService:
    def __init__(self):
        if settings.USE_LOCAL_STORAGE:
            # Try both /app/storage (Docker) and ./storage (local)
            self.base_path = Path("/app/storage")
            self.local_path = Path("storage")
        else:
            from google.cloud import storage
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(settings.GCS_BUCKET_NAME)
    
    def _get_file_path(self, *path_parts):
        """Get file path, trying both Docker and local paths"""
        if not settings.USE_LOCAL_STORAGE:
            return None
        
        # Try Docker path first
        docker_path = self.base_path / Path(*path_parts)
        if docker_path.exists():
            return docker_path
        
        # Try local path
        local_path = self.local_path / Path(*path_parts)
        if local_path.exists():
            return local_path
        
        return None
    
    async def get_lesson_content(
        self, 
        module_id: str, 
        lesson_number: int
    ) -> Optional[Dict[str, Any]]:
        """Retrieve lesson content from storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._get_file_path("lessons", module_id, f"lesson_{lesson_number:02d}.md")
            
            if not file_path:
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return {
                "module_id": module_id,
                "lesson_number": lesson_number,
                "content": content,
                "content_type": "markdown"
            }
        else:
            blob_path = f"lessons/{module_id}/lesson_{lesson_number:02d}.md"
            blob = self.bucket.blob(blob_path)
            
            if not blob.exists():
                return None
            
            content = blob.download_as_text()
            
            return {
                "module_id": module_id,
                "lesson_number": lesson_number,
                "content": content,
                "content_type": "markdown"
            }
    
    async def get_test_questions(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve test questions from storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._get_file_path("tests", module_id, "test_questions.json")
            
            if not file_path:
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            blob_path = f"tests/{module_id}/test_questions.json"
            blob = self.bucket.blob(blob_path)
            
            if not blob.exists():
                return None
            
            content = blob.download_as_text()
            return json.loads(content)
    
    async def get_correct_answers(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve correct answers (internal use only)"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._get_file_path("tests", module_id, "correct_answers.json")
            
            if not file_path:
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            blob_path = f"tests/{module_id}/correct_answers.json"
            blob = self.bucket.blob(blob_path)
            
            if not blob.exists():
                return None
            
            content = blob.download_as_text()
            return json.loads(content)
