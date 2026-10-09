import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_correlation_id_middleware_generates_id(client: AsyncClient):
    response = await client.get("/health/liveness")
    assert response.status_code == 200
    assert "x-correlation-id" in response.headers
    assert "x-request-id" in response.headers
    assert len(response.headers["x-correlation-id"]) > 0


@pytest.mark.asyncio
async def test_correlation_id_middleware_preserves_incoming_id(client: AsyncClient):
    custom_cid = "custom-client-correlation-id-999"
    response = await client.get("/health/liveness", headers={"X-Correlation-ID": custom_cid})
    assert response.status_code == 200
    assert response.headers["x-correlation-id"] == custom_cid


@pytest.mark.asyncio
async def test_request_timing_middleware_adds_header(client: AsyncClient):
    response = await client.get("/health/liveness")
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    assert response.headers["x-process-time"].endswith("ms")


@pytest.mark.asyncio
async def test_not_found_returns_standard_error_envelope(client: AsyncClient):
    response = await client.get("/non-existent-endpoint-404")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "timestamp" in data["error"]
