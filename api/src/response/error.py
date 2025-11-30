import os
from fastapi.responses import JSONResponse
from fastapi import status
import traceback
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Optional
from src.response.map import ERRORS
from src.multilingual.multilingual import translate_error, get_language





class ERROR:
    """
    Centralized Error Response Utility
    Provides standardized JSON error responses with codes, messages, and metadata
    """

    ERRORS = ERRORS

    @classmethod
    def _serialize_data(cls, obj: Any) -> Any:
        """
        Recursively convert non-serializable objects (datetime, date, Decimal) to JSON-serializable types.
        Handles datetime, date, Decimal, dict, list, and Pydantic models.
        """
        if isinstance(obj, datetime):
            return obj.isoformat() + "Z" if not obj.tzinfo else obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: cls._serialize_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [cls._serialize_data(item) for item in obj]
        elif hasattr(obj, 'dict'):
            # Handle Pydantic models
            return cls._serialize_data(obj.dict(exclude_none=True))
        elif hasattr(obj, '__dict__'):
            # Handle other objects with __dict__
            return cls._serialize_data(obj.__dict__)
        return obj

    @classmethod
    def build(
        cls,
        error_key: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict = None,
        exception: Exception = None,
        show_trace: bool = True,
        language: Optional[str] = None
    ):
        """
        Return dict version of the error (no JSONResponse)

        Args:
            language: Language code (e.g., "en", "ar") - if None, uses request.state.language or default
        """
        error = cls.ERRORS.get(error_key, {"code": 1020, "message": f"Dynamic error: {error_key}"})
        error_id = str(uuid.uuid4())

        # Get language - simple and fast
        lang = get_language(language=language)

        # Translate error message
        error_message = error.get("message", f"Dynamic error: {error_key}")
        translated_message = translate_error(error_message, lang)

        # Use http_status from error map if available, otherwise use provided status_code
        final_status_code = error.get("http_status", status_code)

        # Serialize details to handle datetime, date, Decimal, and other non-serializable types
        serialized_details = cls._serialize_data(details) if details else {}

        error_response = {
            "success": False,
            "error": {
                "id": error_id,
                "code": error["code"],
                "message": translated_message,
                "details": serialized_details,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        }
        if exception:
            error_response["error"]["debug"] = {
                "type": type(exception).__name__,
                "exception_message": str(exception),
            }
            if show_trace:
                error_response["error"]["debug"]["traceback"] = traceback.format_exc().splitlines()
        return error_response

    @classmethod
    def response(
        cls,
        error_key: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict = None,
        exception: Exception = None,
        show_trace: bool = os.environ.get('DEBUG_MODE', 'true').lower() == 'true',
        language: Optional[str] = None
    ):
        """
        Return a structured JSON error response.

        Args:
            error_key (str): The error identifier (will use dynamic mapping if not predefined).
            status_code (int): HTTP status code.
            details (dict): Extra contextual details for the client.
            exception (Exception): Optional Python exception for debug info.
            show_trace (bool): Include full traceback if True.
            language (str): Language code (e.g., "en", "ar") - if None, uses request.state.language or default.
        """
        # If error key is unknown, auto-generate message
        error = cls.ERRORS.get(error_key, {"code": 1020, "message": f"Dynamic error: {error_key}"})

        error_id = str(uuid.uuid4())

        # Get language - simple and fast
        lang = get_language(language=language)

        # Translate error message
        error_message = error.get("message", f"Dynamic error: {error_key}")
        translated_message = translate_error(error_message, lang)

        # Use http_status from error map if available, otherwise use provided status_code
        final_status_code = error.get("http_status", status_code)

        # Serialize details to handle datetime, date, Decimal, and other non-serializable types
        serialized_details = cls._serialize_data(details) if details else {}

        error_response = {
            "success": False,
            "error": {
                "id": error_id,
                "code": error["code"],
                "message": translated_message,
                "details": serialized_details,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        }

        if exception:
            error_response["error"]["debug"] = {
                "type": type(exception).__name__,
                "exception_message": str(exception),
            }
            if show_trace:
                error_response["error"]["debug"]["traceback"] = traceback.format_exc().splitlines()

        return JSONResponse(status_code=final_status_code, content=error_response)
