import contextvars
import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Context variables for distributed request tracing
correlation_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "correlation_id", default=None
)
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)

SENSITIVE_KEYS = {
    "password",
    "token",
    "secret",
    "authorization",
    "api_key",
    "access_token",
    "refresh_token",
}


def sanitize_sensitive_data(data: Any) -> Any:
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sens in k.lower() for sens in SENSITIVE_KEYS):
                sanitized[k] = "******"
            else:
                sanitized[k] = sanitize_sensitive_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_sensitive_data(item) for item in data]
    elif isinstance(data, str):
        # Basic check for bearer tokens or JWT strings
        if data.lower().startswith("bearer "):
            return "Bearer ******"
        if len(data) > 64 and re.match(r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$", data):
            return "******"
    return data


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Add context tracing variables if present
        cid = correlation_id_ctx.get()
        if cid:
            log_payload["correlation_id"] = cid

        rid = request_id_ctx.get()
        if rid:
            log_payload["request_id"] = rid

        uid = user_id_ctx.get()
        if uid:
            log_payload["user_id"] = uid

        # Include extra custom attributes attached to log record
        extra_info: Dict[str, Any] = {}
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message",
        }
        for key, val in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                extra_info[key] = sanitize_sensitive_data(val)

        if extra_info:
            log_payload["extra"] = extra_info

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, default=str)


class ConsoleFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",    # Cyan
        logging.INFO: "\033[32m",     # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",    # Red
        logging.CRITICAL: "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        cid = correlation_id_ctx.get() or "-"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{timestamp}] [{color}{record.levelname:8}{self.RESET}] [{cid}]"
        message = f"{prefix} {record.name}:{record.lineno} - {record.getMessage()}"
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        return message


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    root_logger = logging.getLogger()
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(numeric_level)

    if log_format.lower() == "json":
        stream_handler.setFormatter(JSONFormatter())
    else:
        stream_handler.setFormatter(ConsoleFormatter())

    root_logger.addHandler(stream_handler)

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
