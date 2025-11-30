"""
Professional Media Storage Implementation
Handles all media file uploads with proper organization and optimization
FastAPI-compatible version
Replaces storage_utils.py with organized folder-based methods
"""
import os
import mimetypes
import httpx
from uuid import uuid4
from .base_cloud_storage import BaseCloudStorage, ContentFile
from src.logger.logger import logger
import io


class ProfessionalMediaStorage(BaseCloudStorage):
    """
    Professional media storage with automatic organization and optimization
    FastAPI-compatible version
    """

    def __init__(self, bucket_name: str = None, credentials_path: str = None):
        super().__init__(bucket_name, credentials_path)
        self.media_prefix = 'media'

    def _get_media_path(self, name: str) -> str:
        """
        Generate organized media path based on file type and date
        """
        # Get file extension
        _, ext = os.path.splitext(name.lower())
        ext = ext.lstrip('.')

        # Generate organized path
        organized_path = f"{self.media_prefix}/{name}"

        return organized_path

    def _save(self, name: str, content) -> str:
        """
        Save media file with professional organization
        """
        # Generate organized path
        organized_name = self._get_media_path(name)

        # Call parent save method
        return super()._save(organized_name, content)

    def url(self, name: str) -> str:
        """
        Get public URL for file with CDN support
        """
        try:
            from Common.cdn_manager import cdn_manager
            return cdn_manager.get_media_url(name)
        except ImportError:
            # Fallback to parent implementation
            return super().url(name)

    def get_cdn_url(self, name: str) -> str:
        """
        Get CDN URL for media file
        """
        try:
            from Common.cdn_manager import cdn_manager
            return cdn_manager.get_media_url(name)
        except ImportError:
            return self.url(name)

    def _optimize_image(self, content: bytes, content_type: str) -> bytes:
        """
        Optimize image files for web delivery
        """
        try:
            from PIL import Image
            import io

            # Open image
            image = Image.open(io.BytesIO(content))

            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')

            # Resize if too large (max 1920px width)
            if image.width > 1920:
                ratio = 1920 / image.width
                new_height = int(image.height * ratio)
                image = image.resize((1920, new_height), Image.Resampling.LANCZOS)

            # Save optimized image
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()

        except ImportError:
            # PIL not available, return original content
            return content
        except Exception:
            # Error in optimization, return original content
            return content

    def _save_optimized(self, name: str, content) -> str:
        """
        Save media file with optimization
        """
        if isinstance(content, str):
            content = ContentFile(content.encode('utf-8'))

        # Get content type
        content_type = getattr(content, 'content_type', None)
        if not content_type:
            content_type, _ = mimetypes.guess_type(name)

        # Read content
        if hasattr(content, 'read'):
            content.seek(0)
            file_data = content.read()
        else:
            file_data = content

        # Optimize images
        if content_type and content_type.startswith('image/'):
            file_data = self._optimize_image(file_data, content_type)

        # Generate organized path
        organized_name = self._get_media_path(name)

        # Upload optimized content
        if self._use_spaces:
            success = self._spaces_upload(organized_name, file_data, content_type)
            if success:
                return organized_name
            else:
                raise RuntimeError("Failed to upload to DigitalOcean Spaces")
        else:
            if not self._bucket:
                raise RuntimeError("Google Cloud Storage not initialized")

            blob = self._bucket.blob(organized_name)
            blob.upload_from_string(file_data, content_type=content_type)

            # Make the blob publicly accessible
            try:
                blob.make_public()
            except Exception as e:
                # If make_public fails, try setting ACL directly
                try:
                    blob.acl.all().grant_read()
                    blob.acl.save()
                except Exception as acl_error:
                    # Log but don't fail - the file is uploaded but may not be public
                    logger.error(f"Failed to make media blob public: {e}, ACL error: {acl_error}", module="MediaStorage", label="ACL")

            return organized_name

    def generate_thumbnail(self, name: str, size: tuple = (300, 300)) -> str:
        """
        Generate thumbnail for media file
        """
        try:
            from PIL import Image
            import io

            # Get original file
            original_content = self._open(name).read()
            image = Image.open(io.BytesIO(original_content))

            # Create thumbnail
            image.thumbnail(size, Image.Resampling.LANCZOS)

            # Save thumbnail
            thumbnail_name = f"thumbnails/{name}"
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=80)
            thumbnail_content = ContentFile(output.getvalue())

            # Upload thumbnail
            return self._save(thumbnail_name, thumbnail_content)

        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}", module="MediaStorage", label="THUMBNAIL")
            return None

    def get_media_info(self, name: str) -> dict:
        """
        Get detailed information about media file
        """
        try:
            info = {
                'name': name,
                'url': self.url(name),
                'size': self.size(name),
                'exists': self.exists(name)
            }

            # Try to get image dimensions
            if name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                try:
                    from PIL import Image
                    content = self._open(name).read()
                    image = Image.open(io.BytesIO(content))
                    info['dimensions'] = {
                        'width': image.width,
                        'height': image.height
                    }
                except Exception:
                    pass

            return info

        except Exception as e:
            return {'error': str(e)}

    def list_media_files(self, prefix: str = '', limit: int = 100) -> list:
        """
        List media files with optional prefix filtering
        """
        try:
            if self._use_spaces:
                import boto3
                session = boto3.session.Session()
                client = session.client(
                    's3',
                    region_name='sgp1',
                    endpoint_url=self.spaces_server,
                    aws_access_key_id=self.spaces_access_key,
                    aws_secret_access_key=self.spaces_secret_key
                )

                response = client.list_objects_v2(
                    Bucket=self.spaces_bucket,
                    Prefix=f"{self.media_prefix}/{prefix}",
                    MaxKeys=limit
                )

                files = []
                for obj in response.get('Contents', []):
                    files.append({
                        'name': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'url': self.url(obj['Key'])
                    })

                return files
            else:
                # Google Cloud Storage implementation
                blobs = self._bucket.list_blobs(prefix=f"{self.media_prefix}/{prefix}")
                files = []
                count = 0
                for blob in blobs:
                    if count >= limit:
                        break
                    files.append({
                        'name': blob.name,
                        'size': blob.size,
                        'last_modified': blob.time_created,
                        'url': blob.public_url
                    })
                    count += 1

                return files

        except Exception as e:
            logger.error(f"Error listing media files: {e}", module="MediaStorage", label="LIST")
            return []

    # ============================================
    # Storage utility methods (replacing storage_utils.py)
    # Organized by folder type for better structure
    # ============================================

    def upload_to_google_storage(self, file_data, folder: str, object_key: str, content_type: str = 'image/png') -> str:
        """
        Upload file data to Google Cloud Storage.

        Args:
        - file_data: The file data to upload.
        - folder (str): The folder in the bucket where the file will be stored.
        - object_key (str): The key to identify the object in Google Cloud Storage.
        - content_type (str): The content type of the file. Default is 'image/png'.

        Returns:
        - str: The public URL of the uploaded file.
        """
        if not self._bucket:
            raise RuntimeError("Google Cloud Storage not initialized")

        blob = self._bucket.blob(f"{folder}/{object_key}")
        if hasattr(file_data, 'read'):
            file_data.seek(0)
            blob.upload_from_file(file_data, content_type=content_type)
        else:
            blob.upload_from_string(file_data, content_type=content_type)
        blob.make_public()
        return f"https://storage.googleapis.com/{os.environ.get('GOOGLE_STORAGE_BUCKET_NAME')}/{folder}/{object_key}"

    def upload_path_to_google_storage(self, file_path: str, folder: str, object_key: str, content_type: str = 'image/png') -> str:
        """
        Uploads a file from local path to Google Cloud Storage.

        Args:
        - file_path (str): The local path of the file to upload.
        - folder (str): The folder in the bucket where the file will be stored.
        - object_key (str): The key to identify the object in Google Cloud Storage.
        - content_type (str): The content type of the file. Default is 'image/png'.

        Returns:
        - str: The public URL of the uploaded file.
        """
        if not self._bucket:
            raise RuntimeError("Google Cloud Storage not initialized")

        blob = self._bucket.blob(f"{folder}/{object_key}")
        blob.upload_from_filename(file_path, content_type=content_type)
        blob.make_public()
        image_link = f"https://storage.googleapis.com/{os.environ.get('GOOGLE_STORAGE_BUCKET_NAME')}/{folder}/{object_key}"
        os.remove(file_path)
        return image_link

    def upload_to_google_storage_from_string(self, file_data: bytes, folder: str, object_key: str, content_type: str = 'image/png') -> str:
        """
        Uploads file data to Google Cloud Storage.

        Args:
        - file_data (bytes): The data of the file to upload.
        - folder (str): The folder in the bucket where the file will be stored.
        - object_key (str): The key to identify the object in Google Cloud Storage.
        - content_type (str): The content type of the file. Default is 'image/png'.

        Returns:
        - str: The public URL of the uploaded file.
        """
        if not self._bucket:
            raise RuntimeError("Google Cloud Storage not initialized")

        blob = self._bucket.blob(f"{folder}/{object_key}")
        blob.upload_from_string(file_data, content_type=content_type)
        blob.make_public()
        image_link = f"https://storage.googleapis.com/{os.environ.get('GOOGLE_STORAGE_BUCKET_NAME')}/{folder}/{object_key}"
        return image_link

    def upload_xlsx_to_google_storage(self, file_path: str, folder: str, object_key: str, content_type: str = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') -> str:
        """
        Uploads an .xlsx file to Google Cloud Storage.

        Args:
        - file_path (str): The local path of the .xlsx file to upload.
        - folder (str): The folder in the bucket where the file will be stored.
        - object_key (str): The key to identify the object in Google Cloud Storage.

        Returns:
        - str: The public URL of the uploaded .xlsx file.
        """
        if not self._bucket:
            raise RuntimeError("Google Cloud Storage not initialized")

        blob = self._bucket.blob(f"{folder}/{object_key}")
        blob.upload_from_string(file_path, content_type=content_type)
        blob.make_public()
        link = f"https://storage.googleapis.com/{os.environ.get('GOOGLE_STORAGE_BUCKET_NAME')}/{folder}/{object_key}"
        return link

    def upload_generated_media_from_url(self, file_data: bytes, media_type: str, extension: str, folder: str = "generated", content_type: str = None) -> str:
        """
        Uploads media file (image, audio, video) to Google Cloud Storage and returns the public URL.

        Args:
        - file_data (bytes): Binary content of the media.
        - media_type (str): One of 'image', 'audio', 'video'.
        - extension (str): File extension (e.g., 'png', 'mp3', 'mp4').
        - folder (str): Folder in the bucket.
        - content_type (str): Optional content-type override.

        Returns:
        - str: Public URL of the uploaded media.
        """
        content_types = {
            "image": f"image/{extension}",
            "audio": f"audio/{extension}",
            "video": f"video/{extension}",
            "application": f"application/{extension}",
            "text": f"text/{extension}",
        }

        if media_type not in content_types:
            raise ValueError(f"Unsupported media_type '{media_type}'.")

        object_key = f"{uuid4()}.{extension}"
        resolved_content_type = content_type or content_types.get(media_type, 'application/octet-stream')

        return self.upload_to_google_storage_from_string(
            file_data=file_data,
            folder=folder,
            object_key=object_key,
            content_type=resolved_content_type
        )

    def upload_image_from_url_to_gcs(self, file_url: str, folder: str, user_id: str) -> str:
        """
        Downloads a file from a URL and uploads it to Google Cloud Storage
        without modifying its format. Stores in ImageGeneration/ folder.

        Args:
        - file_url (str): URL of the file to download.
        - folder (str): GCS folder to store the file.
        - user_id (str): User ID for naming.

        Returns:
        - str: Public URL of the uploaded file.
        """
        try:
            # Download the file
            with httpx.stream("GET", file_url, timeout=30.0) as response:
                response.raise_for_status()
                file_data = response.read()

            # Extract file extension from URL
            extension = file_url.split("?")[0].split(".")[-1].lower()
            object_key = f"{user_id}-generated-by-{uuid4()}.{extension}"
            content_type = response.headers.get("content-type", f"application/octet-stream")

            # Upload to GCS in ImageGeneration folder
            return self.upload_to_google_storage_from_string(
                file_data=file_data,
                folder=f"ImageGeneration/{folder}",
                object_key=object_key,
                content_type=content_type
            )

        except Exception as e:
            raise RuntimeError(f"Failed to upload file from {file_url}: {e}")

    def upload_video_from_url_to_gcs(self, video_url: str, folder: str, user_id: str) -> str:
        """
        Downloads a video from a URL and uploads it to Google Cloud Storage
        without modifying its format. Stores in VideoGeneration/ folder.

        Args:
        - video_url (str): URL of the video to download.
        - folder (str): GCS folder to store the video.
        - user_id (str): User ID for naming.

        Returns:
        - str: Public URL of the uploaded video.
        """
        try:
            # Download the video
            with httpx.stream("GET", video_url, timeout=60.0) as response:
                response.raise_for_status()
                video_data = response.read()

            # Extract file extension
            extension = video_url.split("?")[0].split(".")[-1].lower()
            object_key = f"{folder}-{user_id}-generated-by-{uuid4()}.{extension}"

            # Determine content type
            content_type = response.headers.get("content-type", f"video/{extension if extension in ['mp4','webm','mov','avi'] else 'mp4'}")

            # Upload to GCS in VideoGeneration folder
            return self.upload_to_google_storage_from_string(
                file_data=video_data,
                folder=f"VideoGeneration/{folder}",
                object_key=object_key,
                content_type=content_type
            )

        except Exception as e:
            raise RuntimeError(f"Failed to upload video from {video_url}: {e}")

    def upload_audio_from_url_to_gcs(self, audio_url: str, folder: str, user_id: str) -> str:
        """
        Downloads an audio file from a URL and uploads it to Google Cloud Storage
        without modifying its format. Stores in AudioGeneration/ folder.

        Args:
        - audio_url (str): URL of the audio file.
        - folder (str): GCS folder to store the audio.
        - user_id (str): User ID for naming.

        Returns:
        - str: Public URL of the uploaded audio.
        """
        try:
            # Download the audio file
            with httpx.stream("GET", audio_url, timeout=30.0) as response:
                response.raise_for_status()
                audio_data = response.read()

            # Extract file extension
            extension = audio_url.split("?")[0].split(".")[-1].lower()
            object_key = f"{folder}-{user_id}-generated-by-{uuid4()}.{extension}"

            # Determine content type
            audio_types = {
                "mp3": "audio/mpeg",
                "wav": "audio/wav",
                "ogg": "audio/ogg",
                "m4a": "audio/mp4",
                "flac": "audio/flac"
            }
            content_type = response.headers.get("content-type") or audio_types.get(extension, "audio/mpeg")

            # Upload to GCS in AudioGeneration folder
            return self.upload_to_google_storage_from_string(
                file_data=audio_data,
                folder=f"AudioGeneration/{folder}",
                object_key=object_key,
                content_type=content_type
            )

        except Exception as e:
            raise RuntimeError(f"Failed to upload audio from {audio_url}: {e}")

    def upload_audio_bytes_to_gcs(self, audio_data: bytes, folder: str, user_id: str, extension: str = "mp3", content_type: str = None) -> str:
        """
        Uploads audio bytes directly to Google Cloud Storage. Stores in AudioGeneration/ folder.

        Args:
        - audio_data (bytes): Audio data in bytes.
        - folder (str): GCS folder to store the audio.
        - user_id (str): User ID for naming.
        - extension (str): File extension, e.g., 'mp3', 'wav'.
        - content_type (str): Optional content type. Defaults based on extension.

        Returns:
        - str: Public URL of the uploaded audio.
        """
        try:
            object_key = f"{folder}-{user_id}-generated-by-{uuid4()}.{extension}"

            # Determine content type
            audio_types = {
                "mp3": "audio/mpeg",
                "wav": "audio/wav",
                "ogg": "audio/ogg",
                "m4a": "audio/mp4",
                "flac": "audio/flac"
            }
            if not content_type:
                content_type = audio_types.get(extension.lower(), "audio/mpeg")

            # Upload to GCS in AudioGeneration folder
            return self.upload_to_google_storage_from_string(
                file_data=audio_data,
                folder=f"AudioGeneration/{folder}",
                object_key=object_key,
                content_type=content_type
            )

        except Exception as e:
            raise RuntimeError(f"Failed to upload audio: {e}")

    def delete_from_google_storage(self, folder: str, object_key: str) -> bool:
        """
        Delete a file from Google Cloud Storage.

        Args:
        - folder (str): The folder in the bucket.
        - object_key (str): The key to identify the object in Google Cloud Storage.

        Returns:
        - bool: True if successful.
        """
        if not self._bucket:
            raise RuntimeError("Google Cloud Storage not initialized")

        blob = self._bucket.blob(f"{folder}/{object_key}")
        blob.delete()
        return True


# Singleton instance for easy access
_media_storage_instance = None

def get_media_storage() -> ProfessionalMediaStorage:
    """
    Get or create singleton instance of ProfessionalMediaStorage

    Returns:
    - ProfessionalMediaStorage: Singleton instance
    """
    global _media_storage_instance
    if _media_storage_instance is None:
        _media_storage_instance = ProfessionalMediaStorage()
    return _media_storage_instance

# Create default instance for backward compatibility
media_storage = get_media_storage()
