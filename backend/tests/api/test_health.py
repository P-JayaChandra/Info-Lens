import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_system_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "app_name" in data
    assert "version" in data
    assert "components" in data
    assert "database" in data["components"]
    assert "storage" in data["components"]


@pytest.mark.asyncio
async def test_get_liveness_probe(client: AsyncClient):
    response = await client.get("/health/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_readiness_probe(client: AsyncClient):
    response = await client.get("/health/readiness")
    assert response.status_code in (200, 503)
    data = response.json()
    assert data["status"] in ("ready", "unready")


@pytest.mark.asyncio
async def test_api_v1_health_route(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
