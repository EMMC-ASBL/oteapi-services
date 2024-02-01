""" Test parser """

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

def test_create_parser(client: "TestClient") -> None:
    """ Test creating a parser """
    response = client.post(
        "/parser/",
        json={
            "parserType": "parser/demo",
            "configuration": {},
        },
    )
    assert "parser_id" in response.json()
    assert response.status_code == 200