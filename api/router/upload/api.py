

from fastapi import Depends, APIRouter, UploadFile, File, Response, HTTPException
from src.response.error import ERROR
from src.response.success import SUCCESS
from src.multilingual.multilingual import normalize_language
from src.storage import upload_to_google_storage_from_string
from src.middleware.permission_middleware import check_permission
from urllib.parse import unquote, urlparse
from src.authenticate.models import User
from src.cache.cache import cache
from uuid import uuid4
import os
import httpx


router = APIRouter()

@router.post("/upload-media")
async def upload_file(
    url: str = None,
    file: UploadFile = File(None),
    current_user: User = Depends(check_permission("add_upload"))
):
    """
    Upload media file.

    Required Permission: add_upload
    Upload a media file either from URL or direct file upload to Google Cloud Storage.
    """
    if not (url or file):
        raise HTTPException(
                status_code=500,
                detail=ERROR.build("MEDIA_FILE_OR_URL", details={"user_id": current_user.uid}, language=normalize_language(getattr(current_user, 'language', None)) if current_user else None)
            )

    try:
        if url:
            # Download file from URL
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                file_data = response.content
                # Try to get extension from URL or response headers
                extension = url.split("?")[0].split(".")[-1].lower()
                if not extension or "/" in extension:
                    extension = response.headers.get("content-type", "bin").split("/")[-1]
                content_type = response.headers.get("content-type", "application/octet-stream")
            object_key = f"{current_user.uid}-|-{uuid4()}.{extension}"
        else:
            # File upload
            file_data = await file.read()
            extension = file.filename.split(".")[-1].lower()
            content_type = file.content_type or "application/octet-stream"
            object_key = f"{current_user.uid}-|-{uuid4()}.{extension}"

        # Upload to GCS
        folder = "media/users"
        public_url = upload_to_google_storage_from_string(
            file_data=file_data,
            folder=folder,
            object_key=object_key,
            content_type=content_type
        )
        return SUCCESS.response(
            data={"url": public_url},
            message="File uploaded successfully",
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        raise HTTPException(
                status_code=500,
                detail=ERROR.build("MEDIA_UPLOADING_PROCESSING_ERROR", details={"user_id": current_user.uid}, exception=e, language=normalize_language(getattr(current_user, 'language', None)) if current_user else None)
            )

@router.delete("/delete-media")
async def delete_file(
    url: str = "",
    current_user: User = Depends(check_permission("delete_upload"))
):
    """
    Delete media file.

    Required Permission: delete_upload
    Delete a media file from Google Cloud Storage.
    """
    try:
        if not url:
            return Response(status_code=400, content="No URL provided.")

        # Get the configured bucket name from environment
        bucket_name = os.environ.get('GOOGLE_STORAGE_BUCKET_NAME')
        if not bucket_name:
            return Response(status_code=500, content="Bucket name not configured.")

        # Decode and parse the URL
        decoded_url = unquote(url)
        parsed_url = urlparse(decoded_url)

        # Validate domain
        if "storage.googleapis.com" not in parsed_url.netloc:
            return Response(status_code=400, content="Invalid GCS URL.")

        # Example path: /BACKEND-bucket/folder/filename.png
        path_parts = parsed_url.path.lstrip("/").split("/", 1)

        if len(path_parts) != 2:
            return Response(status_code=400, content="Invalid GCS URL format.")

        url_bucket = path_parts[0]
        object_path = path_parts[1]

        # Check if bucket in URL matches the configured one
        if url_bucket != bucket_name:
            return Response(status_code=403, content="URL bucket does not match configured bucket.")

        # Extract folder and object_key from path
        # Path format: folder/object_key
        path_parts = object_path.split("/", 1)
        if len(path_parts) == 2:
            folder = path_parts[0]
            object_key = path_parts[1]
        else:
            folder = ""
            object_key = object_path

        from src.storage import delete_from_google_storage
        deleted = delete_from_google_storage(folder, object_key)
        if not deleted:
            return Response(status_code=404, content="File not found in GCS.")
        return SUCCESS.response(
            data={"bucket": bucket_name},
            message=f"File deleted successfully from bucket '{bucket_name}'.",
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        raise HTTPException(
                status_code=500,
                detail=ERROR.build("MEDIA_DELETING_PROCESSING_ERROR", details={"user_id": current_user.uid}, exception=e, language=normalize_language(getattr(current_user, 'language', None)) if current_user else None)
            )


@router.on_event("startup")
async def startup_event():
    await cache.init()
