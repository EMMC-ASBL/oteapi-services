""" Test parser """

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_parser(client: "TestClient") -> None:
    """Test creating a parser"""
    response = client.post(
        "/parser/",
        json={
            "parserType": "parser/demo",
            "entity": "http://example.com/entity",
            "configuration": {
                "downloadUrl": "https://filesamples.com/sample2.json",
                "mediaType": "application/json",
            },
        },
    )
    assert "parser_id" in response.json()
    assert response.status_code == 200


def test_info_parser(client: "TestClient") -> None:
    """Test getting information about a parser"""
    response = client.get("/parser/parser-f752c613-fde0-4d43-a7f6-c50f68642daa/info")
    assert response.status_code == 200
    assert "parserType" in response.json()
    assert "configuration" in response.json()


def test_get_parser(client: "TestClient") -> None:
    """Test getting and parsing data using a specified parser"""
    response = client.get("/parser/parser-f752c613-fde0-4d43-a7f6-c50f68642daa")
    assert response.status_code == 200
