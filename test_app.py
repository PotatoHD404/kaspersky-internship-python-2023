import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

search_directory = "./search_directory"


def test_create_search():
    response = client.post(
        "/search",
        json={
            "text": "1",
            "file_mask": "*1*.p?",
            "size": {
                "value": 42000,
                "operator": "lt"
            },
            "creation_time": {
                "value": "2024-03-03T14:00:54Z",
                "operator": "lt"
            }
        },
    )

    assert response.status_code == 200
    assert "search_id" in response.json()


def test_get_search_results():
    search_id = uuid.uuid4()
    response = client.get(f"/searches/{search_id}")

    assert response.status_code == 404

    response = client.post(
        "/search",
        json={
            "text": "1",
            "file_mask": "*1*.p?",
            "size": {
                "value": 42000,
                "operator": "lt"
            },
            "creation_time": {
                "value": "2024-03-03T14:00:54Z",
                "operator": "lt"
            }
        },
    )

    search_id = response.json()["search_id"]

    response = client.get(f"/searches/{search_id}")
    assert response.status_code == 200
    assert response.json()["finished"] is True
    assert len(response.json()["paths"]) == 3


def test_invalid_search_id():
    response = client.get("/searches/invalid_search_id")

    assert response.status_code == 400
    assert "Search id is not valid" in response.json()["message"]
