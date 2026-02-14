"""Tests for main FastAPI application."""

from typing import Any

from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient) -> None:
    """Test that health check endpoint returns 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_returns_json(client: TestClient) -> None:
    """Test that health check endpoint returns JSON content type."""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"


def test_health_check_response_structure(client: TestClient) -> None:
    """Test that health check response has correct structure."""
    response = client.get("/health")
    data: dict[str, Any] = response.json()

    assert "status" in data
    assert "service" in data
    assert len(data) == 2


def test_health_check_response_values(client: TestClient) -> None:
    """Test that health check response has correct values."""
    response = client.get("/health")
    data: dict[str, Any] = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "banking-data-validator"


def test_health_check_idempotency(client: TestClient) -> None:
    """Test that health check is idempotent (multiple calls return same result)."""
    response1 = client.get("/health")
    response2 = client.get("/health")

    assert response1.json() == response2.json()
    assert response1.status_code == response2.status_code


def test_root_endpoint_does_not_exist(client: TestClient) -> None:
    """Test that root endpoint returns 404 (not implemented yet)."""
    response = client.get("/")
    assert response.status_code == 404


def test_invalid_endpoint_returns_404(client: TestClient) -> None:
    """Test that non-existent endpoints return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
