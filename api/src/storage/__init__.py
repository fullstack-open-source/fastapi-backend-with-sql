"""
Professional Google Cloud Storage Package
Organized storage implementations for FastAPI
All upload functions now use ProfessionalMediaStorage with organized folders
"""

# FastAPI-compatible storage classes
from .base_cloud_storage import BaseCloudStorage, ContentFile
from .media_storage import ProfessionalMediaStorage, media_storage, get_media_storage


# Wrapper functions for backward compatibility (using media_storage instance)
# These functions delegate to ProfessionalMediaStorage methods with organized folders

def upload_to_google_storage(file_data, folder: str, object_key: str, content_type: str = 'image/png') -> str:
    """Upload file data to Google Cloud Storage. Uses media_storage instance."""
    return media_storage.upload_to_google_storage(file_data, folder, object_key, content_type)

def upload_path_to_google_storage(file_path: str, folder: str, object_key: str, content_type: str = 'image/png') -> str:
    """Upload file from local path to Google Cloud Storage. Uses media_storage instance."""
    return media_storage.upload_path_to_google_storage(file_path, folder, object_key, content_type)

def upload_to_google_storage_from_string(file_data: bytes, folder: str, object_key: str, content_type: str = 'image/png') -> str:
    """Upload file data from string/bytes to Google Cloud Storage. Uses media_storage instance."""
    return media_storage.upload_to_google_storage_from_string(file_data, folder, object_key, content_type)

def upload_xlsx_to_google_storage(file_path: str, folder: str, object_key: str, content_type: str = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') -> str:
    """Upload .xlsx file to Google Cloud Storage. Uses media_storage instance."""
    return media_storage.upload_xlsx_to_google_storage(file_path, folder, object_key, content_type)

def upload_generated_media_from_url(file_data: bytes, media_type: str, extension: str, folder: str = "generated", content_type: str = None) -> str:
    """Upload generated media to Google Cloud Storage. Uses media_storage instance."""
    return media_storage.upload_generated_media_from_url(file_data, media_type, extension, folder, content_type)

def upload_image_from_url_to_gcs(file_url: str, folder: str, user_id: str) -> str:
    """Download image from URL and upload to ImageGeneration/ folder. Uses media_storage instance."""
    return media_storage.upload_image_from_url_to_gcs(file_url, folder, user_id)

def upload_video_from_url_to_gcs(video_url: str, folder: str, user_id: str) -> str:
    """Download video from URL and upload to VideoGeneration/ folder. Uses media_storage instance."""
    return media_storage.upload_video_from_url_to_gcs(video_url, folder, user_id)

def upload_audio_from_url_to_gcs(audio_url: str, folder: str, user_id: str) -> str:
    """Download audio from URL and upload to AudioGeneration/ folder. Uses media_storage instance."""
    return media_storage.upload_audio_from_url_to_gcs(audio_url, folder, user_id)

def upload_audio_bytes_to_gcs(audio_data: bytes, folder: str, user_id: str, extension: str = "mp3", content_type: str = None) -> str:
    """Upload audio bytes to AudioGeneration/ folder. Uses media_storage instance."""
    return media_storage.upload_audio_bytes_to_gcs(audio_data, folder, user_id, extension, content_type)

def delete_from_google_storage(folder: str, object_key: str) -> bool:
    """Delete file from Google Cloud Storage. Uses media_storage instance."""
    return media_storage.delete_from_google_storage(folder, object_key)

__all__ = [
    'BaseCloudStorage',
    'ContentFile',
    'ProfessionalMediaStorage',
    'media_storage',
    'get_media_storage',
    # Wrapper functions for backward compatibility
    'upload_to_google_storage',
    'upload_path_to_google_storage',
    'upload_to_google_storage_from_string',
    'upload_xlsx_to_google_storage',
    'upload_generated_media_from_url',
    'upload_image_from_url_to_gcs',
    'upload_video_from_url_to_gcs',
    'upload_audio_from_url_to_gcs',
    'upload_audio_bytes_to_gcs',
    'delete_from_google_storage'
]

