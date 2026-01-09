"""
Structured logging configuration for Wasteless UI
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname:8}{self.RESET}"
        return super().format(record)


def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Setup structured logging for the application.

    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional file path for logging. If None, uses default location.

    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger('wasteless_ui')
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name=None):
    """
    Get a logger instance.

    Args:
        name: Logger name (default: wasteless_ui)

    Returns:
        Logger instance
    """
    logger_name = f'wasteless_ui.{name}' if name else 'wasteless_ui'
    return logging.getLogger(logger_name)


# Initialize default logger
default_logger = setup_logging(
    log_level=logging.INFO,
    log_file='logs/wasteless_ui.log'
)


# Convenience functions
def log_user_action(action: str, details: dict = None, user: str = "streamlit_user"):
    """Log user actions for audit trail."""
    logger = get_logger('user_actions')
    details_str = f" | {details}" if details else ""
    logger.info(f"User: {user} | Action: {action}{details_str}")


def log_db_query(query_name: str, duration_ms: float, success: bool = True):
    """Log database query performance."""
    logger = get_logger('database')
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Query: {query_name} | Duration: {duration_ms:.2f}ms | Status: {status}")


def log_error(error: Exception, context: str = None):
    """Log errors with context."""
    logger = get_logger('errors')
    context_str = f" | Context: {context}" if context else ""
    logger.error(f"Error: {type(error).__name__}: {str(error)}{context_str}", exc_info=True)


def log_config_change(setting: str, old_value: any, new_value: any, user: str = "streamlit_user"):
    """Log configuration changes."""
    logger = get_logger('config')
    logger.warning(f"Config Change | User: {user} | Setting: {setting} | Old: {old_value} | New: {new_value}")


def log_cache_stats(cache_name: str, hits: int, misses: int):
    """Log cache statistics."""
    logger = get_logger('cache')
    hit_rate = (hits / (hits + misses) * 100) if (hits + misses) > 0 else 0
    logger.debug(f"Cache: {cache_name} | Hits: {hits} | Misses: {misses} | Hit Rate: {hit_rate:.1f}%")
