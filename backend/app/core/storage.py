import json
import os
import shutil
from typing import Optional, Dict, Any, BinaryIO, List
from pathlib import Path
from uuid import UUID

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
    
    # Course metadata methods
    async def get_course_metadata(self, course_id: UUID) -> Optional[Dict[str, Any]]:
        """Get course metadata from storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._get_file_path("courses", str(course_id), "metadata.json")
            if not file_path:
                return None
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            blob_path = f"courses/{course_id}/metadata.json"
            blob = self.bucket.blob(blob_path)
            if not blob.exists():
                return None
            content = blob.download_as_text()
            return json.loads(content)
    
    async def save_course_metadata(self, course_id: UUID, metadata: Dict[str, Any]) -> bool:
        """Save course metadata to storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._ensure_directory("courses", str(course_id), "metadata.json")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
                return True
            return False
        else:
            blob_path = f"courses/{course_id}/metadata.json"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(
                json.dumps(metadata, ensure_ascii=False, indent=2, default=str),
                content_type="application/json"
            )
            return True
    
    # Module metadata methods
    async def get_module_metadata(self, course_id: UUID, module_id: str) -> Optional[Dict[str, Any]]:
        """Get module metadata from storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._get_file_path("courses", str(course_id), "modules", module_id, "metadata.json")
            if not file_path:
                return None
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/metadata.json"
            blob = self.bucket.blob(blob_path)
            if not blob.exists():
                return None
            content = blob.download_as_text()
            return json.loads(content)
    
    async def save_module_metadata(self, course_id: UUID, module_id: str, metadata: Dict[str, Any]) -> bool:
        """Save module metadata to storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._ensure_directory("courses", str(course_id), "modules", module_id, "metadata.json")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
                return True
            return False
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/metadata.json"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(
                json.dumps(metadata, ensure_ascii=False, indent=2, default=str),
                content_type="application/json"
            )
            return True
    
    # Lesson content methods
    async def get_lesson_content(
        self, 
        course_id: UUID,
        module_id: str, 
        lesson_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve lesson content from storage (new structure)"""
        if settings.USE_LOCAL_STORAGE:
            # Try new structure first
            file_path = self._get_file_path("courses", str(course_id), "modules", module_id, "lessons", lesson_id, "content.md")
            if file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return {
                    "lesson_id": lesson_id,
                    "module_id": module_id,
                    "course_id": str(course_id),
                    "content": content,
                    "content_type": "markdown"
                }
            
            # Fallback to old structure for backward compatibility
            # Extract lesson_number from lesson_id (format: Module_01_Lesson_01 -> 01)
            try:
                lesson_number_str = lesson_id.split("_Lesson_")[-1]
                lesson_number = int(lesson_number_str)
                old_path = self._get_file_path("lessons", module_id, f"lesson_{lesson_number:02d}.md")
                if old_path:
                    with open(old_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    return {
                        "lesson_id": lesson_id,
                        "module_id": module_id,
                        "course_id": str(course_id),
                        "content": content,
                        "content_type": "markdown"
                    }
            except (ValueError, IndexError):
                pass
            
            return None
        else:
            # Try new structure first
            blob_path = f"courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/content.md"
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                content = blob.download_as_text()
                return {
                    "lesson_id": lesson_id,
                    "module_id": module_id,
                    "course_id": str(course_id),
                    "content": content,
                    "content_type": "markdown"
                }
            
            # Fallback to old structure
            try:
                lesson_number_str = lesson_id.split("_Lesson_")[-1]
                lesson_number = int(lesson_number_str)
                old_blob_path = f"lessons/{module_id}/lesson_{lesson_number:02d}.md"
                old_blob = self.bucket.blob(old_blob_path)
                if old_blob.exists():
                    content = old_blob.download_as_text()
                    return {
                        "lesson_id": lesson_id,
                        "module_id": module_id,
                        "course_id": str(course_id),
                        "content": content,
                        "content_type": "markdown"
                    }
            except (ValueError, IndexError):
                pass
            
            return None
    
    async def save_lesson_content(
        self,
        course_id: UUID,
        module_id: str,
        lesson_id: str,
        content: str,
        content_type: str = "markdown"
    ) -> bool:
        """Save lesson content to storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._ensure_directory("courses", str(course_id), "modules", module_id, "lessons", lesson_id, "content.md")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            return False
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/content.md"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(content, content_type="text/markdown")
            return True
    
    # File management methods
    async def list_lesson_files(
        self,
        course_id: UUID,
        module_id: str,
        lesson_id: str,
        file_type: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """List all files for a lesson, organized by type"""
        result = {
            "audio": [],
            "video": [],
            "images": [],
            "attachments": []
        }
        
        if settings.USE_LOCAL_STORAGE:
            lesson_files_dir = self.base_path / "courses" / str(course_id) / "modules" / module_id / "lessons" / lesson_id / "files"
            if not lesson_files_dir.exists():
                lesson_files_dir = self.local_path / "courses" / str(course_id) / "modules" / module_id / "lessons" / lesson_id / "files"
            
            if not lesson_files_dir.exists():
                return result
            
            # List files by type
            for file_type_dir in ["audio", "video", "images", "attachments"]:
                type_dir = lesson_files_dir / file_type_dir
                if type_dir.exists():
                    for file_path in type_dir.iterdir():
                        if file_path.is_file():
                            result[file_type_dir].append(file_path.name)
        else:
            prefix = f"courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/files/"
            blobs = self.bucket.list_blobs(prefix=prefix)
            for blob in blobs:
                # Extract file type from path
                path_parts = blob.name.replace(prefix, "").split("/")
                if len(path_parts) >= 2:
                    file_type_dir = path_parts[0]
                    filename = path_parts[1]
                    if file_type_dir in result:
                        result[file_type_dir].append(filename)
        
        if file_type:
            return {file_type: result.get(file_type, [])}
        return result
    
    async def save_file(
        self,
        course_id: UUID,
        module_id: str,
        lesson_id: str,
        file_type: str,
        file_content: bytes,
        filename: str,
        content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """Save a file (audio, video, image, attachment) and return the file path"""
        # Validate file type
        valid_types = ["audio", "video", "images", "attachments"]
        if file_type not in valid_types:
            raise ValueError(f"Invalid file type. Must be one of: {valid_types}")
        
        # Generate filename with lesson_id prefix
        file_ext = Path(filename).suffix
        file_base = Path(filename).stem
        new_filename = f"{lesson_id}_{file_type}_{file_base}{file_ext}"
        
        if settings.USE_LOCAL_STORAGE:
            file_path = self._ensure_directory(
                "courses", str(course_id), "modules", module_id, 
                "lessons", lesson_id, "files", file_type, new_filename
            )
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(file_content)
                return f"/api/v1/modules/{module_id}/lessons/{lesson_id}/files/{file_type}/{new_filename}"
            return None
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/files/{file_type}/{new_filename}"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(file_content, content_type=content_type)
            return blob.public_url or f"/api/v1/modules/{module_id}/lessons/{lesson_id}/files/{file_type}/{new_filename}"
    
    async def get_file(
        self,
        course_id: UUID,
        module_id: str,
        lesson_id: str,
        file_type: str,
        filename: str
    ) -> Optional[bytes]:
        """Get file content"""
        if settings.USE_LOCAL_STORAGE:
            docker_path = self.base_path / "courses" / str(course_id) / "modules" / module_id / "lessons" / lesson_id / "files" / file_type / filename
            local_path = self.local_path / "courses" / str(course_id) / "modules" / module_id / "lessons" / lesson_id / "files" / file_type / filename
            
            if docker_path.exists():
                with open(docker_path, "rb") as f:
                    return f.read()
            elif local_path.exists():
                with open(local_path, "rb") as f:
                    return f.read()
            return None
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/files/{file_type}/{filename}"
            blob = self.bucket.blob(blob_path)
            if not blob.exists():
                return None
            return blob.download_as_bytes()
    
    async def delete_file(
        self,
        course_id: UUID,
        module_id: str,
        lesson_id: str,
        file_type: str,
        filename: str
    ) -> bool:
        """Delete a file"""
        if settings.USE_LOCAL_STORAGE:
            docker_path = self.base_path / "courses" / str(course_id) / "modules" / module_id / "lessons" / lesson_id / "files" / file_type / filename
            local_path = self.local_path / "courses" / str(course_id) / "modules" / module_id / "lessons" / lesson_id / "files" / file_type / filename
            
            if docker_path.exists():
                docker_path.unlink()
                return True
            elif local_path.exists():
                local_path.unlink()
                return True
            return False
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/files/{file_type}/{filename}"
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                blob.delete()
                return True
            return False
    
    # Test methods
    async def get_test_questions(self, course_id: UUID, module_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve test questions from storage (with backward compatibility)"""
        if settings.USE_LOCAL_STORAGE:
            # Try new structure first
            file_path = self._get_file_path("courses", str(course_id), "modules", module_id, "test", "questions.json")
            if file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            
            # Fallback to old structure
            old_path = self._get_file_path("tests", module_id, "test_questions.json")
            if old_path:
                with open(old_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            
            return None
        else:
            # Try new structure first
            blob_path = f"courses/{course_id}/modules/{module_id}/test/questions.json"
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                content = blob.download_as_text()
                return json.loads(content)
            
            # Fallback to old structure
            old_blob_path = f"tests/{module_id}/test_questions.json"
            old_blob = self.bucket.blob(old_blob_path)
            if old_blob.exists():
                content = old_blob.download_as_text()
                return json.loads(content)
            
            return None
    
    async def save_test_questions(
        self,
        course_id: UUID,
        module_id: str,
        test_data: Dict[str, Any]
    ) -> bool:
        """Save test questions to storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._ensure_directory("courses", str(course_id), "modules", module_id, "test", "questions.json")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(test_data, f, ensure_ascii=False, indent=2)
                return True
            return False
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/test/questions.json"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(
                json.dumps(test_data, ensure_ascii=False, indent=2),
                content_type="application/json"
            )
            return True
    
    async def get_test_settings(self, course_id: UUID, module_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve test settings from storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._get_file_path("courses", str(course_id), "modules", module_id, "test", "settings.json")
            if not file_path:
                return None
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/test/settings.json"
            blob = self.bucket.blob(blob_path)
            if not blob.exists():
                return None
            content = blob.download_as_text()
            return json.loads(content)
    
    async def save_test_settings(
        self,
        course_id: UUID,
        module_id: str,
        settings_data: Dict[str, Any]
    ) -> bool:
        """Save test settings to storage"""
        if settings.USE_LOCAL_STORAGE:
            file_path = self._ensure_directory("courses", str(course_id), "modules", module_id, "test", "settings.json")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(settings_data, f, ensure_ascii=False, indent=2)
                return True
            return False
        else:
            blob_path = f"courses/{course_id}/modules/{module_id}/test/settings.json"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(
                json.dumps(settings_data, ensure_ascii=False, indent=2),
                content_type="application/json"
            )
            return True
    
    # Backward compatibility methods (for migration)
    async def get_correct_answers(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve correct answers (deprecated - for backward compatibility)"""
        # This method is kept for backward compatibility
        # In new structure, answers are in questions.json
        return None
