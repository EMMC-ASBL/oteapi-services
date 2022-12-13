"""Test transformation."""
import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_transformation(client: "TestClient") -> None:
    """Test creating a transformation."""
    response = client.post(
        "/transformation/",
        json={
            "transformationType": "script/dummy",
            "name": "script/dummy",
            "configuration": {},
        },
    )
    assert response.status_code == 200


def test_create_transformation_auth_model(client: "TestClient") -> None:
    """Test creating a transformation through the model."""
    dummy_secret = "Bearer 123"
    response = client.post(
        "/transformation/",
        json={
            "transformationType": "script/dummy",
            "name": "script/dummy",
            "configuration": {},
            "secret": dummy_secret,
        },
    )
    assert response.status_code == 200

    response = client.get(f"/redis/{response.json()['transformation_id']}")
    assert response.status_code == 200
    assert json.loads(response.json()).get("secret") == dummy_secret


def test_create_transformation_auth_headers(client: "TestClient") -> None:
    """Test creating a transformation through the request headers."""
    dummy_secret = "Bearer 123"
    response = client.post(
        "/transformation/",
        json={
            "transformationType": "script/dummy",
            "name": "script/dummy",
            "configuration": {},
        },
        headers={"Authorization": dummy_secret},
    )
    assert response.status_code == 200

    response = client.get(f"/redis/{response.json()['transformation_id']}")
    assert response.status_code == 200
    assert json.loads(response.json()).get("secret") == dummy_secret


def test_get_transformation(client: "TestClient") -> None:
    """Test getting a transformation."""
    response = client.get(
        "/transformation/transformation-f752c613-fde0-4d43-a7f6-c50f68642daa"
    )
    assert response.status_code == 200


def test_initialize_transformation(client: "TestClient") -> None:
    """Test initializing a transformation."""
    response = client.post(
        "/transformation/transformation-f752c613-fde0-4d43-a7f6-c50f68642daa/execute",
        json={},
    )
    assert response.status_code == 200


def test_get_transformation_status(client: "TestClient") -> None:
    """Test getting a transformation status."""
    from oteapi.models.transformationconfig import TransformationStatus
    from pydantic import ValidationError

    response = client.get(
        "/transformation/transformation-f752c613-fde0-4d43-a7f6-c50f68642daa/status?task_id="
    )
    try:
        TransformationStatus(**response.json())
    except ValidationError as exc:
        pytest.fail(f"Failed to validate as a `TransformationStatus`. Exc: {exc}")
    assert response.status_code == 200


def test_execute_transformation(client: "TestClient") -> None:
    """Test executing a transformation."""
    response = client.post(
        "/transformation/transformation-f752c613-fde0-4d43-a7f6-c50f68642daa/execute",
        json={},
    )
    assert response.status_code == 200
