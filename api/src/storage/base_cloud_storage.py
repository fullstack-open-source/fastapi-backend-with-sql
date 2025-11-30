"""
Base Google Cloud Storage Configuration
Professional implementation for Google Cloud Storage only
FastAPI-compatible version
"""
import os
import mimetypes
import threading
from typing import Optional, Union
from io import BytesIO

# Centralized logger import for best performance
try:
    from src.logger.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("storage")

# Try to import required libraries
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

# Global GCS client cache to prevent multiple initializations
_gcs_client_cache = {}
_gcs_client_lock = threading.Lock()


class ContentFile:
    """
    FastAPI-compatible file-like object wrapper
    Replaces Django's ContentFile for FastAPI projects
    """
    def __init__(self, content: Union[bytes, str], name: str = None, content_type: str = None):
        if isinstance(content, str):
            content = content.encode('utf-8')
        self.file = BytesIO(content)
        self.name = name
        self.content_type = content_type
        self.size = len(content)

    def read(self, size: int = -1) -> bytes:
        """Read content from file"""
        return self.file.read(size)

    def seek(self, pos: int, whence: int = 0) -> int:
        """Seek to position in file"""
        return self.file.seek(pos, whence)

    def tell(self) -> int:
        """Get current position in file"""
        return self.file.tell()

    def close(self):
        """Close the file"""
        self.file.close()


class BaseCloudStorage:
    """
    Base class for Google Cloud Storage implementations
    FastAPI-compatible version - no Django dependencies
    Handles Google Cloud Storage only
    """

    def __init__(self, bucket_name: str = None, credentials_path: str = None):

        # Set your Google Cloud credentials
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        CREDENTIALS_PATH = os.path.join(BASE_DIR, "./../../credentials/google-backend-master.json")
        self.bucket_name = bucket_name or os.environ.get('GOOGLE_STORAGE_BUCKET_NAME', 'media-bucket')
        self.credentials_path = CREDENTIALS_PATH

        # Force Google Cloud Storage only - disable DigitalOcean Spaces
        self.spaces_bucket = None
        self.spaces_access_key = None
        self.spaces_secret_key = None
        self.spaces_server = None

        self._client = None
        self._bucket = None
        self._use_spaces = False  # Force GCS only

        if GOOGLE_CLOUD_AVAILABLE:
            self._initialize_gcs_client()
        else:
            raise RuntimeError("Google Cloud Storage library not available. Please install google-cloud-storage.")

    def _initialize_gcs_client(self):
        """Initialize Google Cloud Storage client with singleton pattern"""
        # Create a cache key based on bucket name and credentials path
        cache_key = f"{self.bucket_name}:{self.credentials_path or 'default'}"

        # Check if client is already cached
        with _gcs_client_lock:
            if cache_key in _gcs_client_cache:
                cached_client, cached_bucket = _gcs_client_cache[cache_key]
                self._client = cached_client
                self._bucket = cached_bucket
                return  # Use cached client, no logging needed

        # Initialize new client only if not cached
        try:
            # Set environment variable for Google Cloud credentials
            if self.credentials_path and os.path.exists(self.credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self._client = storage.Client(credentials=credentials)
            else:
                # Try to use environment variable
                if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                    creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
                    if os.path.exists(creds_path):
                        credentials = service_account.Credentials.from_service_account_file(creds_path)
                        self._client = storage.Client(credentials=credentials)
                    else:
                        if not hasattr(self.__class__, '_logged_env_error'):
                            logger.warning("Environment GOOGLE_APPLICATION_CREDENTIALS path not found, trying default authentication...", module="GCS", label="AUTH")
                            self.__class__._logged_env_error = True
                        self._client = storage.Client()
                else:
                    if not hasattr(self.__class__, '_logged_no_credentials'):
                        logger.warning("No credentials file found, trying default authentication...", module="GCS", label="AUTH")
                        self.__class__._logged_no_credentials = True
                    self._client = storage.Client()

            self._bucket = self._client.bucket(self.bucket_name)

            # Cache the client and bucket
            with _gcs_client_lock:
                _gcs_client_cache[cache_key] = (self._client, self._bucket)

        except Exception as e:
            if not hasattr(self.__class__, '_logged_error'):
                logger.error(f"Failed to initialize Google Cloud Storage: {e}", module="GCS", label="ERROR")
                self.__class__._logged_error = True
            self._client = None
            self._bucket = None

    def _get_spaces_url(self, name: str) -> str:
        """Get DigitalOcean Spaces URL for file"""
        return f"{self.spaces_server}/{self.spaces_bucket}/{name}"

    def _spaces_upload(self, name: str, content: bytes, content_type: str = None) -> bool:
        """Upload file to DigitalOcean Spaces"""
        if not BOTO3_AVAILABLE:
            return False

        try:
            session = boto3.session.Session()
            client = session.client(
                's3',
                region_name='sgp1',
                endpoint_url=self.spaces_server,
                aws_access_key_id=self.spaces_access_key,
                aws_secret_access_key=self.spaces_secret_key
            )

            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            client.put_object(
                Bucket=self.spaces_bucket,
                Key=name,
                Body=content,
                **extra_args
            )
            return True
        except Exception as e:
            logger.error(f"Error uploading to DigitalOcean Spaces: {e}", module="GCS", label="UPLOAD")
            return False

    def _spaces_download(self, name: str) -> Optional[bytes]:
        """Download file from DigitalOcean Spaces"""
        if not BOTO3_AVAILABLE:
            return None

        try:
            session = boto3.session.Session()
            client = session.client(
                's3',
                region_name='sgp1',
                endpoint_url=self.spaces_server,
                aws_access_key_id=self.spaces_access_key,
                aws_secret_access_key=self.spaces_secret_key
            )

            response = client.get_object(Bucket=self.spaces_bucket, Key=name)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error downloading from DigitalOcean Spaces: {e}", module="GCS", label="DOWNLOAD")
            return None

    def _spaces_exists(self, name: str) -> bool:
        """Check if file exists in DigitalOcean Spaces"""
        if not BOTO3_AVAILABLE:
            return False

        try:
            session = boto3.session.Session()
            client = session.client(
                's3',
                region_name='sgp1',
                endpoint_url=self.spaces_server,
                aws_access_key_id=self.spaces_access_key,
                aws_secret_access_key=self.spaces_secret_key
            )

            client.head_object(Bucket=self.spaces_bucket, Key=name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            return False
        except Exception:
            return False

    def _spaces_delete(self, name: str) -> bool:
        """Delete file from DigitalOcean Spaces"""
        if not BOTO3_AVAILABLE:
            return False

        try:
            session = boto3.session.Session()
            client = session.client(
                's3',
                region_name='sgp1',
                endpoint_url=self.spaces_server,
                aws_access_key_id=self.spaces_access_key,
                aws_secret_access_key=self.spaces_secret_key
            )

            client.delete_object(Bucket=self.spaces_bucket, Key=name)
            return True
        except Exception as e:
            logger.error(f"Error deleting from DigitalOcean Spaces: {e}", module="GCS", label="DELETE")
            return False

    def _save(self, name: str, content) -> str:
        """Save file to storage"""
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

        if self._use_spaces:
            success = self._spaces_upload(name, file_data, content_type)
            if success:
                return name
            else:
                raise RuntimeError("Failed to upload to DigitalOcean Spaces")
        else:
            if not self._bucket:
                raise RuntimeError("Google Cloud Storage not initialized")

            blob = self._bucket.blob(name)
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
                    logger.error(f"Failed to make blob public: {e}, ACL error: {acl_error}", module="GCS", label="ACL")

            return name

    def _open(self, name: str, mode: str = 'rb'):
        """Open file from storage"""
        if self._use_spaces:
            file_data = self._spaces_download(name)
            if file_data is None:
                raise FileNotFoundError(f"File {name} not found in DigitalOcean Spaces")
            return ContentFile(file_data)
        else:
            if not self._bucket:
                raise RuntimeError("Google Cloud Storage not initialized")

            blob = self._bucket.blob(name)
            if not blob.exists():
                raise FileNotFoundError(f"File {name} not found in Google Cloud Storage")

            file_data = blob.download_as_bytes()
            return ContentFile(file_data)

    def exists(self, name: str) -> bool:
        """Check if file exists"""
        if self._use_spaces:
            return self._spaces_exists(name)
        else:
            if not self._bucket:
                return False
            blob = self._bucket.blob(name)
            return blob.exists()

    def url(self, name: str) -> str:
        """Get public URL for file"""
        if self._use_spaces:
            return self._get_spaces_url(name)
        else:
            if not self._bucket:
                raise RuntimeError("Google Cloud Storage not initialized")
            blob = self._bucket.blob(name)
            return blob.public_url

    def delete(self, name: str):
        """Delete file from storage"""
        if self._use_spaces:
            self._spaces_delete(name)
        else:
            if not self._bucket:
                raise RuntimeError("Google Cloud Storage not initialized")
            blob = self._bucket.blob(name)
            blob.delete()

    def size(self, name: str) -> int:
        """Get file size"""
        if self._use_spaces:
            try:
                session = boto3.session.Session()
                client = session.client(
                    's3',
                    region_name='sgp1',
                    endpoint_url=self.spaces_server,
                    aws_access_key_id=self.spaces_access_key,
                    aws_secret_access_key=self.spaces_secret_key
                )
                response = client.head_object(Bucket=self.spaces_bucket, Key=name)
                return response['ContentLength']
            except Exception:
                return 0
        else:
            if not self._bucket:
                return 0
            blob = self._bucket.blob(name)
            blob.reload()
            return blob.size

    def get_available_name(self, name: str, max_length: int = None) -> str:
        """Get available name for file"""
        try:
            if self.exists(name):
                name_parts = name.rsplit('.', 1)
                if len(name_parts) == 2:
                    base_name, extension = name_parts
                    counter = 1
                    while True:
                        new_name = f"{base_name}_{counter}.{extension}"
                        if not self.exists(new_name):
                            return new_name
                        counter += 1
                else:
                    counter = 1
                    while True:
                        new_name = f"{name}_{counter}"
                        if not self.exists(new_name):
                            return new_name
                        counter += 1
        except Exception as e:
            # If we don't have read permissions (e.g., storage.objects.get permission denied),
            # just return the original name and let the upload proceed
            # This allows uploads to work even without read permissions
            error_msg = str(e).lower()
            if 'storage.objects.get' in error_msg or 'permission' in error_msg or '403' in error_msg:
                # No read permissions - return original name and let upload proceed
                # The file will be overwritten if it exists, or created if it doesn't
                return name
            else:
                # Some other error - re-raise it
                raise
        return name
