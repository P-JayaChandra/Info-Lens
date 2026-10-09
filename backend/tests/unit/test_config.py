import pytest
from app.core.config import Settings, get_settings
from app.core.constants import Environment


def test_default_settings():
    settings = get_settings()
    assert settings.APP_NAME == "AI Document Intelligence Platform"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert len(settings.SECRET_KEY) >= 32


def test_environment_helper_properties():
    dev_settings = Settings(ENVIRONMENT=Environment.DEVELOPMENT)
    assert not dev_settings.is_testing
    assert not dev_settings.is_production

    test_settings = Settings(ENVIRONMENT=Environment.TESTING)
    assert test_settings.is_testing
    assert not test_settings.is_production

    prod_settings = Settings(ENVIRONMENT=Environment.PRODUCTION)
    assert not prod_settings.is_testing
    assert prod_settings.is_production


def test_cors_origins_parsing():
    settings_from_str = Settings(CORS_ORIGINS="http://localhost:3000, http://example.com")
    assert "http://localhost:3000" in settings_from_str.CORS_ORIGINS
    assert "http://example.com" in settings_from_str.CORS_ORIGINS

    settings_from_list = Settings(CORS_ORIGINS=["http://test.com"])
    assert settings_from_list.CORS_ORIGINS == ["http://test.com"]


def test_resolved_storage_path(tmp_path):
    custom_path = str(tmp_path / "custom_storage")
    settings = Settings(LOCAL_STORAGE_PATH=custom_path)
    resolved = settings.resolved_storage_path
    assert resolved.exists()
    assert resolved.is_dir()
