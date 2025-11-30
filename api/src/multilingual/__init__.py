"""
Multilingual support module for API responses.
Provides translation functionality for error messages and success messages.
"""

from .multilingual import (
    get_language,
    translate_message,
    translate_error,
    translate_json_data,
    normalize_language
)


__all__ = [
    "get_language",
    "translate_message",
    "translate_error",
    "translate_json_data",
    "normalize_language",
]

