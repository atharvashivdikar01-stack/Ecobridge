import logging
import sys
from typing import Any, Dict
from .config import settings


class CustomFormatter(logging.Formatter):
    """Clean, structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return f"[{log_data['timestamp']}] [{log_data['level']}] [{log_data['logger']}]: {log_data['message']}"


def setup_logging() -> None:
    """Configures the root and uvicorn loggers."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CustomFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Silence verbose 3rd party logs
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Returns a logger instance with the specified name."""
    return logging.getLogger(name)
