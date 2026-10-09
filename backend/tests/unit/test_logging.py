import json
import logging
from app.core.logging import (
    JSONFormatter,
    correlation_id_ctx,
    get_logger,
    request_id_ctx,
    sanitize_sensitive_data,
    setup_logging,
    user_id_ctx,
)


def test_sanitize_sensitive_data():
    raw_payload = {
        "username": "johndoe",
        "password": "SuperSecretPassword!",
        "token": "eyJhbGciOi...",
        "api_key": "dkey_123456",
        "nested": {
            "secret": "topsecret",
            "normal": "value",
        },
        "list_items": [{"authorization": "Bearer token123"}],
    }

    sanitized = sanitize_sensitive_data(raw_payload)
    assert sanitized["username"] == "johndoe"
    assert sanitized["password"] == "******"
    assert sanitized["token"] == "******"
    assert sanitized["api_key"] == "******"
    assert sanitized["nested"]["secret"] == "******"
    assert sanitized["nested"]["normal"] == "value"
    assert sanitized["list_items"][0]["authorization"] == "******"


def test_json_formatter_with_contextvars():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message with param %s",
        args=("val",),
        exc_info=None,
    )

    token_c = correlation_id_ctx.set("corr-uuid-123")
    token_r = request_id_ctx.set("req-uuid-456")
    token_u = user_id_ctx.set("user-uuid-789")

    try:
        formatted = formatter.format(record)
        data = json.loads(formatted)
        assert data["level"] == "INFO"
        assert data["message"] == "Test message with param val"
        assert data["correlation_id"] == "corr-uuid-123"
        assert data["request_id"] == "req-uuid-456"
        assert data["user_id"] == "user-uuid-789"
    finally:
        correlation_id_ctx.reset(token_c)
        request_id_ctx.reset(token_r)
        user_id_ctx.reset(token_u)


def test_setup_logging_and_get_logger():
    setup_logging(log_level="DEBUG", log_format="json")
    logger = get_logger("my_module")
    assert logger.name == "my_module"
    assert logging.getLogger().level == logging.DEBUG
