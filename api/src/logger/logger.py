"""
Professional Centralized Logging System for WINSTA_AI Backend API V3
FastAPI-compatible version with enhanced features
Features:
- Single unified log file (server.log) for all logs including errors
- Enhanced formatting with timestamp, module, label, user_id, request_id
- File rotation and size management (50MB, 10 backups)
- Performance monitoring
- Error tracking with stack traces
- Request/Response logging
- Security event logging
- Module, timestamp, and label support
"""
import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any


def _get_utc_offset() -> int:
    """
    Safely get UTC offset from environment variable.
    Handles string values like 'true'/'false' and converts to integer.
    Defaults to UTC+3 if parsing fails.
    """
    try:
        utc_offset = os.environ.get("UTC", "3")
        if isinstance(utc_offset, str) and utc_offset.lower() in ['true', 'false']:
            return 3  # Default to UTC+3
        return int(utc_offset)
    except (ValueError, TypeError):
        return 3  # Default to UTC+3


class ProfessionalLogger:
    """
    Professional centralized logging system for WINSTA_AI Backend API V3
    FastAPI-compatible version
    """

    def __init__(self, name: str = 'WINSTA_AI_V3_API'):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # Setup log directory
        try:
            # Try to use logs directory relative to the API root
            api_root = Path(__file__).parent.parent.parent
            self.log_dir = api_root / "logs"
            self.log_dir.mkdir(exist_ok=True)
            if not self.log_dir.exists():
                raise OSError(f"Failed to create logs directory: {self.log_dir}")
        except Exception as e:
            # Fallback to a relative path
            self.log_dir = Path("logs")
            self.log_dir.mkdir(exist_ok=True)
            print(f"Warning: Using fallback logs directory: {self.log_dir}")

        # Timezone configuration
        utc_offset = _get_utc_offset()
        self.tz = timezone(timedelta(hours=utc_offset))

        # Configure handlers
        self._setup_console_handler()
        self._setup_file_handlers()
        self._setup_error_handler()

        # Performance tracking
        self.performance_data = {}

        # Security events tracking
        self.security_events = []

    def _setup_console_handler(self):
        """Setup colored console output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO))

        # Custom formatter with colors and enhanced details
        class ColoredFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': '\033[36m',    # Cyan
                'INFO': '\033[32m',     # Green
                'WARNING': '\033[33m',  # Yellow
                'ERROR': '\033[31m',    # Red
                'CRITICAL': '\033[35m', # Magenta
                'SUCCESS': '\033[92m',  # Bright Green
                'SECURITY': '\033[91m', # Bright Red
                'RESET': '\033[0m'      # Reset
            }

            def format(self, record):
                log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
                reset_color = self.COLORS['RESET']

                # Format timestamp with milliseconds
                utc_offset = _get_utc_offset()
                timestamp = datetime.now(tz=timezone(timedelta(hours=utc_offset))).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                # Build module info
                module_info = ""
                if hasattr(record, 'module_name') and record.module_name:
                    module_info = f"[{record.module_name}]"

                # Build label/tag info
                label_info = ""
                if hasattr(record, 'label') and record.label:
                    label_info = f"[{record.label}]"

                # Build user info
                user_info = ""
                if hasattr(record, 'user_id') and record.user_id:
                    user_info = f"[User:{record.user_id}]"

                # Build request info
                request_info = ""
                if hasattr(record, 'request_id') and record.request_id:
                    request_info = f"[Req:{record.request_id[:8]}]"

                # Build file/line info
                file_info = f"{record.filename}:{record.lineno}" if hasattr(record, 'filename') else ""

                # Format message
                parts = [
                    f"{log_color}[{record.levelname}]{reset_color}",
                    timestamp,
                    module_info,
                    label_info,
                    user_info,
                    request_info,
                    file_info,
                    record.getMessage()
                ]
                formatted_msg = " ".join(filter(None, parts))
                return formatted_msg

        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)

    def _setup_file_handlers(self):
        """Setup single file handler for all logs including errors"""
        # Single unified log file for all logs (including errors)
        unified_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'server.log',
            maxBytes=50*1024*1024,  # 50MB (larger since it contains all logs)
            backupCount=10  # Keep more backups
        )
        unified_handler.setLevel(logging.DEBUG)  # Log everything from DEBUG and above

        # Custom formatter that includes timestamp, module, label, user_id, etc.
        class EnhancedFormatter(logging.Formatter):
            def format(self, record):
                # Add timestamp with milliseconds
                utc_offset = _get_utc_offset()
                timestamp = datetime.now(tz=timezone(timedelta(hours=utc_offset))).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                # Build context parts
                context_parts = []

                # Level
                level = f"[{record.levelname}]"
                context_parts.append(level)

                # Module
                if hasattr(record, 'module_name') and record.module_name:
                    context_parts.append(f"[Module:{record.module_name}]")
                elif hasattr(record, 'module') and record.module:
                    context_parts.append(f"[Module:{record.module}]")

                # Label
                if hasattr(record, 'label') and record.label:
                    context_parts.append(f"[Label:{record.label}]")

                # User ID
                if hasattr(record, 'user_id') and record.user_id:
                    context_parts.append(f"[User:{record.user_id}]")

                # Request ID
                if hasattr(record, 'request_id') and record.request_id:
                    context_parts.append(f"[Req:{record.request_id[:8]}]")

                # File and line
                file_info = f"{record.filename}:{record.lineno}"
                context_parts.append(f"[{file_info}]")

                context_str = " ".join(context_parts)

                # Format message
                message = record.getMessage()

                # Add exception info if present
                if record.exc_info:
                    exc_text = self.formatException(record.exc_info)
                    message = f"{message}\n{exc_text}"

                return f"{timestamp} {context_str} {message}"

        enhanced_formatter = EnhancedFormatter()
        unified_handler.setFormatter(enhanced_formatter)

        # Add only the unified handler
        self.logger.addHandler(unified_handler)

    def _setup_error_handler(self):
        """Setup handler for uncaught exceptions"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            # Don't handle KeyboardInterrupt or SystemExit
            if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Only log if logger is fully initialized
            try:
                if self.logger and self.logger.handlers:
                    self.logger.critical(
                        "Uncaught exception",
                        exc_info=(exc_type, exc_value, exc_traceback)
                    )
                else:
                    # Fallback to stderr if logger not ready
                    print(f"Uncaught exception (logger not ready): {exc_type.__name__}: {exc_value}", file=sys.stderr)
                    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
            except Exception:
                # If logging fails, use basic print
                print(f"Uncaught exception: {exc_type.__name__}: {exc_value}", file=sys.stderr)
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

        sys.excepthook = handle_exception

    def _log_with_context(self, level: str, message: str, **kwargs):
        """Log with additional context"""
        extra = {
            'module_name': kwargs.get('module', kwargs.get('module_name', None)),
            'label': kwargs.get('label', None),
            'user_id': kwargs.get('user_id', None),
            'request_id': kwargs.get('request_id', None),
            'performance': kwargs.get('performance', None),
            'extra_data': kwargs.get('extra_data', {})
        }

        # Remove None values
        extra = {k: v for k, v in extra.items() if v is not None}

        getattr(self.logger, level.lower())(message, extra=extra)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context('INFO', message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context('DEBUG', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_with_context('ERROR', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context('CRITICAL', message, **kwargs)

    def success(self, message: str, **kwargs):
        """Log success message"""
        self._log_with_context('INFO', f"✅ SUCCESS: {message}", **kwargs)

    def security(self, message: str, **kwargs):
        """Log security event"""
        self._log_with_context('WARNING', f"🔒 SECURITY: {message}", **kwargs)
        self.security_events.append({
            'timestamp': datetime.now(tz=self.tz).isoformat(),
            'message': message,
            'context': kwargs
        })

    def performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self._log_with_context('INFO', f"⚡ PERFORMANCE: {operation} took {duration:.3f}s",
                              performance={'operation': operation, 'duration': duration}, **kwargs)
        self.performance_data[operation] = duration

    def request(self, method: str, path: str, status_code: int, duration: float, **kwargs):
        """Log HTTP request"""
        self._log_with_context('INFO',
                              f"🌐 REQUEST: {method} {path} -> {status_code} ({duration:.3f}s)",
                              extra_data={'method': method, 'path': path, 'status_code': status_code, 'duration': duration},
                              **kwargs)

    def database(self, operation: str, table: str, duration: float, **kwargs):
        """Log database operations"""
        self._log_with_context('DEBUG',
                              f"🗄️ DATABASE: {operation} on {table} ({duration:.3f}s)",
                              extra_data={'operation': operation, 'table': table, 'duration': duration},
                              **kwargs)

    def api_call(self, service: str, endpoint: str, status_code: int, duration: float, **kwargs):
        """Log external API calls"""
        self._log_with_context('INFO',
                              f"🔗 API: {service} {endpoint} -> {status_code} ({duration:.3f}s)",
                              extra_data={'service': service, 'endpoint': endpoint, 'status_code': status_code, 'duration': duration},
                              **kwargs)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'total_operations': len(self.performance_data),
            'average_duration': sum(self.performance_data.values()) / len(self.performance_data) if self.performance_data else 0,
            'slowest_operation': max(self.performance_data.items(), key=lambda x: x[1]) if self.performance_data else None,
            'operations': self.performance_data
        }

    def get_security_summary(self) -> Dict[str, Any]:
        """Get security events summary"""
        return {
            'total_events': len(self.security_events),
            'recent_events': self.security_events[-10:] if self.security_events else [],
            'all_events': self.security_events
        }

    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log files"""
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        for log_file in self.log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                self.info(f"Cleaned up old log file: {log_file.name}")


# Global logger instance
_logger_instance = None

def get_logger() -> ProfessionalLogger:
    """Get or create singleton logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ProfessionalLogger()
    return _logger_instance

# Create default logger instance
logger = get_logger()

# Convenience functions for backward compatibility and easy access
def info(message: str, **kwargs):
    """Log info message"""
    logger.info(message, **kwargs)

def warning(message: str, **kwargs):
    """Log warning message"""
    logger.warning(message, **kwargs)

def error(message: str, **kwargs):
    """Log error message"""
    logger.error(message, **kwargs)

def success(message: str, **kwargs):
    """Log success message"""
    logger.success(message, **kwargs)

def debug(message: str, **kwargs):
    """Log debug message"""
    logger.debug(message, **kwargs)

def critical(message: str, **kwargs):
    """Log critical message"""
    logger.critical(message, **kwargs)

def security(message: str, **kwargs):
    """Log security event"""
    logger.security(message, **kwargs)

def performance(operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    logger.performance(operation, duration, **kwargs)

def request(method: str, path: str, status_code: int, duration: float, **kwargs):
    """Log HTTP request"""
    logger.request(method, path, status_code, duration, **kwargs)

def database(operation: str, table: str, duration: float, **kwargs):
    """Log database operations"""
    logger.database(operation, table, duration, **kwargs)

def api_call(service: str, endpoint: str, status_code: int, duration: float, **kwargs):
    """Log external API calls"""
    logger.api_call(service, endpoint, status_code, duration, **kwargs)
