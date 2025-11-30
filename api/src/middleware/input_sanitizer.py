"""
Input Sanitization Utilities
Provides functions to sanitize user input to prevent XSS, SQL Injection, and other attacks.
"""

import re
import html
import json
from typing import Any, Dict, List, Union


class InputSanitizer:
    """
    Utility class for sanitizing user input
    """

    # Dangerous characters that should be escaped
    DANGEROUS_CHARS = {
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
        "&": "&amp;",
        "(": "&#40;",
        ")": "&#41;",
        ";": "&#59;",
        "=": "&#61;",
    }

    @staticmethod
    def sanitize_html(value: str) -> str:
        """
        Sanitize HTML to prevent XSS attacks.
        Escapes HTML special characters.
        """
        if not isinstance(value, str):
            return value

        return html.escape(value, quote=True)

    @staticmethod
    def sanitize_sql_input(value: Any) -> Any:
        """
        Sanitize input for SQL queries.
        Note: This is a basic sanitizer. Always use parameterized queries!
        """
        if isinstance(value, str):
            # Remove or escape SQL special characters
            value = value.replace("'", "''")  # SQL escape single quotes
            value = value.replace(";", "")  # Remove semicolons
            value = value.replace("--", "")  # Remove SQL comments
            value = value.replace("/*", "")  # Remove block comments
            value = value.replace("*/", "")  # Remove block comments
        return value

    @staticmethod
    def sanitize_path(value: str) -> str:
        """
        Sanitize file paths to prevent path traversal attacks.
        """
        if not isinstance(value, str):
            return value

        # Remove path traversal sequences
        value = value.replace("../", "")
        value = value.replace("..\\", "")
        value = value.replace("%2e%2e%2f", "")
        value = value.replace("%2e%2e%5c", "")

        # Remove leading slashes and dots
        value = value.lstrip("/").lstrip("\\").lstrip(".")

        # Remove any remaining dangerous characters
        for char in ["<", ">", "|", "&", ";", "`", "$", "(", ")", "{", "}"]:
            value = value.replace(char, "")

        return value

    @staticmethod
    def sanitize_url(value: str) -> str:
        """
        Sanitize URLs to prevent SSRF and other attacks.
        """
        if not isinstance(value, str):
            return value

        # Remove dangerous protocols
        dangerous_protocols = ["file://", "gopher://", "dict://", "ldap://"]
        for protocol in dangerous_protocols:
            if value.lower().startswith(protocol):
                return ""

        # Check for localhost/private IPs
        private_ip_patterns = [
            r"localhost",
            r"127\.0\.0\.1",
            r"0\.0\.0\.0",
            r"::1",
            r"169\.254\.169\.254",
            r"192\.168\.\d+\.\d+",
            r"10\.\d+\.\d+\.\d+",
            r"172\.(1[6-9]|2[0-9]|3[01])\.\d+\.\d+",
        ]

        for pattern in private_ip_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                # Only block if it's not a public URL with localhost in path
                if not re.match(r"^https?://[^/]+", value):
                    return ""

        return value

    @staticmethod
    def sanitize_command(value: str) -> str:
        """
        Sanitize command input to prevent command injection.
        """
        if not isinstance(value, str):
            return value

        # Remove command separators
        value = value.replace(";", "")
        value = value.replace("|", "")
        value = value.replace("&", "")
        value = value.replace("&&", "")
        value = value.replace("||", "")
        value = value.replace("`", "")
        value = value.replace("$(", "")
        value = value.replace("${", "")

        # Remove dangerous commands
        dangerous_commands = [
            r"rm\s", r"del\s", r"delete\s", r"format\s", r"mkfs\s",
            r"shutdown\s", r"reboot\s", r"kill\s", r"pkill\s", r"killall\s"
        ]

        for cmd_pattern in dangerous_commands:
            value = re.sub(cmd_pattern, "", value, flags=re.IGNORECASE)

        return value

    @staticmethod
    def sanitize_json(value: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """
        Sanitize JSON input to prevent NoSQL injection.
        """
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return InputSanitizer.sanitize_json(parsed)
            except json.JSONDecodeError:
                # If not valid JSON, sanitize as string
                return InputSanitizer.sanitize_html(value)

        if isinstance(value, dict):
            sanitized = {}
            for key, val in value.items():
                # Remove MongoDB operators
                if key.startswith("$"):
                    continue
                sanitized[InputSanitizer.sanitize_html(str(key))] = InputSanitizer.sanitize_json(val)
            return sanitized

        if isinstance(value, list):
            return [InputSanitizer.sanitize_json(item) for item in value]

        if isinstance(value, (int, float, bool, type(None))):
            return value

        if isinstance(value, str):
            return InputSanitizer.sanitize_html(value)

        return value

    @staticmethod
    def sanitize_all(value: Any, sanitize_type: str = "html") -> Any:
        """
        Sanitize input based on type.

        Args:
            value: Input value to sanitize
            sanitize_type: Type of sanitization ('html', 'sql', 'path', 'url', 'command', 'json', 'all')
        """
        if value is None:
            return None

        if sanitize_type == "all":
            # Apply all sanitizations
            if isinstance(value, str):
                value = InputSanitizer.sanitize_html(value)
                value = InputSanitizer.sanitize_path(value)
                value = InputSanitizer.sanitize_command(value)
            elif isinstance(value, (dict, list)):
                value = InputSanitizer.sanitize_json(value)
        elif sanitize_type == "html":
            value = InputSanitizer.sanitize_html(str(value)) if isinstance(value, str) else value
        elif sanitize_type == "sql":
            value = InputSanitizer.sanitize_sql_input(value)
        elif sanitize_type == "path":
            value = InputSanitizer.sanitize_path(str(value)) if isinstance(value, str) else value
        elif sanitize_type == "url":
            value = InputSanitizer.sanitize_url(str(value)) if isinstance(value, str) else value
        elif sanitize_type == "command":
            value = InputSanitizer.sanitize_command(str(value)) if isinstance(value, str) else value
        elif sanitize_type == "json":
            value = InputSanitizer.sanitize_json(value)

        return value


# Convenience functions
def sanitize_html(value: str) -> str:
    """Sanitize HTML input"""
    return InputSanitizer.sanitize_html(value)


def sanitize_sql(value: Any) -> Any:
    """Sanitize SQL input (use parameterized queries instead!)"""
    return InputSanitizer.sanitize_sql_input(value)


def sanitize_path(value: str) -> str:
    """Sanitize file path"""
    return InputSanitizer.sanitize_path(value)


def sanitize_url(value: str) -> str:
    """Sanitize URL"""
    return InputSanitizer.sanitize_url(value)


def sanitize_command(value: str) -> str:
    """Sanitize command input"""
    return InputSanitizer.sanitize_command(value)


def sanitize_json(value: Union[str, Dict, List]) -> Union[str, Dict, List]:
    """Sanitize JSON input"""
    return InputSanitizer.sanitize_json(value)

