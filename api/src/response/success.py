from fastapi.responses import JSONResponse
from fastapi import status
from datetime import datetime, date
import uuid
from typing import Any, Union, Optional
from decimal import Decimal
from src.multilingual.multilingual import (
    translate_message,
    get_language,
    translate_json_data
)


class SUCCESS:
    """
    Centralized Success Response Utility
    Provides standardized JSON success responses with metadata and pagination support
    """

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
    def _build_meta(cls, data: Any = None, meta: dict = None) -> dict:
        """Auto-build meta section with pagination or stats if applicable"""
        base_meta = meta or {}
        # Add count info if data is a list
        if isinstance(data, list):
            base_meta.setdefault("count", len(data))
        # Add type hint
        base_meta.setdefault("type", type(data).__name__)
        return base_meta

    @classmethod
    def build(
        cls,
        data: Union[dict, list, None] = None,
        message: str = "Request successful",
        status_code: int = status.HTTP_200_OK,
        meta: dict = None,
        request_id: str = None,
        language: Optional[str] = None,
        translate_data: bool = False
    ):
        """
        Return dict version of success response (no JSONResponse)
        Serializes datetime, date, and Decimal objects to JSON-compatible types

        Args:
            language: Language code (e.g., "en", "ar") - if None, uses request.state.language or default
            translate_data: If True, translate JSON data structures (default: False)
        """
        # Get language - simple and fast
        lang = get_language(language=language)

        # Translate message
        translated_message = translate_message(message, lang)

        # Serialize data to handle datetime, date, Decimal, and other non-serializable types
        serialized_data = cls._serialize_data(data) if data is not None else {}

        # Optionally translate JSON data
        if translate_data and serialized_data:
            serialized_data = translate_json_data(serialized_data, lang)

        return {
            "success": True,
            "id": request_id or str(uuid.uuid4()),
            "message": translated_message,
            "data": serialized_data,
            "meta": cls._build_meta(data, meta),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @classmethod
    def response(
        cls,
        data: Union[dict, list, None] = None,
        message: str = "Request successful",
        status_code: int = status.HTTP_200_OK,
        meta: dict = None,
        request_id: str = None,
        language: Optional[str] = None,
        translate_data: bool = False
    ):
        """
        Return JSONResponse version of success response
        Serializes datetime, date, and Decimal objects to JSON-compatible types

        Args:
            language: Language code (e.g., "en", "ar") - if None, uses request.state.language or default
            translate_data: If True, translate JSON data structures (default: False)
        """
        # Get language - simple and fast
        lang = get_language(language=language)

        # Translate message
        translated_message = translate_message(message, lang)

        # Serialize data to handle datetime, date, Decimal, and other non-serializable types
        serialized_data = cls._serialize_data(data) if data is not None else {}

        # Optionally translate JSON data
        if translate_data and serialized_data:
            serialized_data = translate_json_data(serialized_data, lang)

        content = {
            "success": True,
            "id": request_id or str(uuid.uuid4()),
            "message": translated_message,
            "data": serialized_data,
            "meta": cls._build_meta(data, meta),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        return JSONResponse(status_code=status_code, content=content)

    @classmethod
    def message_with_data(
        cls,
        message: str,
        data: dict,
        status_code: int = status.HTTP_200_OK,
        language: Optional[str] = None,
        translate_data: bool = False
    ):
        return cls.response(
            data={**data, "message": message},
            message=message,
            status_code=status_code,
            language=language,
            translate_data=translate_data
        )

    @classmethod
    def message(
        cls,
        message: str,
        status_code: int = status.HTTP_200_OK,
        language: Optional[str] = None
    ):
        return cls.response(
            data={"message": message},
            message=message,
            status_code=status_code,
            language=language
        )