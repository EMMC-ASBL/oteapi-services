""" Test parser """

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_dataresource(client: "TestClient"):
    response = client.post(
        "/dataresource/",
        json={
            "downloadUrl": "https://filesamples.com/sample2.json",
            "mediaType": "application/json",
            "resourceType": "resource/demo",
        },
    )
    assert response.status_code == 200


def test_get_dataresource_info(client: "TestClient"):
    response = client.get(
        "/dataresource/dataresource-910c9965-a318-4ac4-9123-9c55d5b86f2e/info"
    )
    assert response.status_code == 200


def test_read_dataresource(client: "TestClient"):
    response = client.get(
        "/dataresource/dataresource-910c9965-a318-4ac4-9123-9c55d5b86f2e"
    )
    assert response.status_code == 200


def test_initialize_dataresource(client: "TestClient"):
    response = client.post(
        "/dataresource/dataresource-910c9965-a318-4ac4-9123-9c55d5b86f2e/initialize"
    )
    assert response.status_code == 200
