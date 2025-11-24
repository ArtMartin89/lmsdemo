import json
import os
import shutil
from typing import Optional, Dict, Any, BinaryIO, List
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
    
    def _ensure_directory(self, *path_parts):
        """Ensure directory exists, trying both Docker and local paths"""
        if not settings.USE_LOCAL_STORAGE:
            return None
        
        # Try Docker path first
        docker_path = self.base_path / Path(*path_parts)
        docker_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Also ensure local path exists
        local_path = self.local_path / Path(*path_parts)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        return docker_path
    
    async def save_lesson_content(
        self,
        module_id: str,
        lesson_number: int,
        content: str,
        content_type: str = "markdown"
    ) -> bool:
        """Save lesson content to storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._ensure_directory("lessons", module_id, f"lesson_{lesson_number:02d}.md")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            return False
        else:
            blob_path = f"lessons/{module_id}/lesson_{lesson_number:02d}.md"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(content, content_type="text/markdown")
            return True
    
    async def save_file(
        self,
        module_id: str,
        lesson_number: int,
        file_content: bytes,
        filename: str,
        content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """Save a file (audio, video, image, etc.) and return the file path"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._ensure_directory("lessons", module_id, f"lesson_{lesson_number:02d}_{filename}")
            
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(file_content)
                # Return relative path for serving
                return f"/api/v1/admin/files/{module_id}/{lesson_number}/{filename}"
            return None
        else:
            blob_path = f"lessons/{module_id}/lesson_{lesson_number:02d}_{filename}"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(file_content, content_type=content_type)
            return blob.public_url or f"/api/v1/admin/files/{module_id}/{lesson_number}/{filename}"
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from content type"""
        extensions = {
            "audio/mpeg": ".mp3",
            "audio/wav": ".wav",
            "audio/ogg": ".ogg",
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
        }
        return extensions.get(content_type, "")
    
    async def get_file(
        self,
        module_id: str,
        lesson_number: int,
        filename: str
    ) -> Optional[bytes]:
        """Get file content"""
        if settings.USE_LOCAL_STORAGE:
            # Try both Docker and local paths
            docker_path = self.base_path / "lessons" / module_id / f"lesson_{lesson_number:02d}_{filename}"
            local_path = self.local_path / "lessons" / module_id / f"lesson_{lesson_number:02d}_{filename}"
            
            if docker_path.exists():
                with open(docker_path, "rb") as f:
                    return f.read()
            elif local_path.exists():
                with open(local_path, "rb") as f:
                    return f.read()
            return None
        else:
            blob_path = f"lessons/{module_id}/lesson_{lesson_number:02d}_{filename}"
            blob = self.bucket.blob(blob_path)
            if not blob.exists():
                return None
            return blob.download_as_bytes()
    
    async def list_lesson_files(
        self,
        module_id: str,
        lesson_number: int
    ) -> List[str]:
        """List all files for a lesson"""
        if settings.USE_LOCAL_STORAGE:
            # Try both Docker and local paths
            docker_dir = self.base_path / "lessons" / module_id
            local_dir = self.local_path / "lessons" / module_id
            
            lesson_dir = None
            if docker_dir.exists():
                lesson_dir = docker_dir
            elif local_dir.exists():
                lesson_dir = local_dir
            
            if not lesson_dir:
                return []
            
            files = []
            pattern = f"lesson_{lesson_number:02d}_*"
            for file_path in lesson_dir.glob(pattern):
                if file_path.is_file() and file_path.name != f"lesson_{lesson_number:02d}.md":
                    filename = file_path.name.replace(f"lesson_{lesson_number:02d}_", "")
                    files.append(filename)
            return files
        else:
            prefix = f"lessons/{module_id}/lesson_{lesson_number:02d}_"
            blobs = self.bucket.list_blobs(prefix=prefix)
            files = []
            for blob in blobs:
                if not blob.name.endswith(".md"):
                    filename = blob.name.replace(prefix, "")
                    files.append(filename)
            return files
    
    async def delete_file(
        self,
        module_id: str,
        lesson_number: int,
        filename: str
    ) -> bool:
        """Delete a file"""
        if settings.USE_LOCAL_STORAGE:
            # Try both Docker and local paths
            docker_path = self.base_path / "lessons" / module_id / f"lesson_{lesson_number:02d}_{filename}"
            local_path = self.local_path / "lessons" / module_id / f"lesson_{lesson_number:02d}_{filename}"
            
            if docker_path.exists():
                docker_path.unlink()
                return True
            elif local_path.exists():
                local_path.unlink()
                return True
            return False
        else:
            blob_path = f"lessons/{module_id}/lesson_{lesson_number:02d}_{filename}"
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                blob.delete()
                return True
            return False
