import pytest
from fastapi import status


def test_create_endpoint_with_name(client):
    payload = {"name": "My Test Endpoint"}
    response = client.post("/endpoints", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert "url" in data
    assert "name" in data
    assert "created_at" in data
    assert data["name"] == "My Test Endpoint"
    assert data["url"].startswith("http://localhost:8000/w/")


def test_create_endpoint_without_name(client):
    payload = {}
    response = client.post("/endpoints", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] is None


def test_get_existing_endpoint(client):
    create_response = client.post("/endpoints", json={"name": "Test"})
    endpoint_id = create_response.json()["id"]

    response = client.get(f"/endpoints/{endpoint_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == endpoint_id
    assert data["name"] == "Test"


def test_get_nonexistent_endpoint(client):
    response = client.get("/endpoints/fake-id-12345")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_webhook_receiver_post(client):
    create_response = client.post("/endpoints", json={"name": "Webhook Test"})
    endpoint_id = create_response.json()["id"]

    webhook_payload = {"event": "user.created", "user_id": 123}
    response = client.post(f"/w/{endpoint_id}", json=webhook_payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "received"
    assert data["endpoint_id"] == endpoint_id
    assert "request_id" in data
    assert data["total_requests"] == 1


def test_webhook_receiver_get(client):
    create_response = client.post("/endpoints", json={"name": "GET Test"})
    endpoint_id = create_response.json()["id"]

    response = client.get(f"/w/{endpoint_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "received"


def test_webhook_receiver_all_methods(client):
    create_response = client.post("/endpoints", json={"name": "Multi Method"})
    endpoint_id = create_response.json()["id"]

    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    for method in methods:
        response = client.request(method, f"/w/{endpoint_id}")
        assert response.status_code == status.HTTP_200_OK, f"{method} failed"
        assert response.json()["status"] == "received"


def test_webhook_receiver_nonexistent_endpoint(client):
    response = client.post("/w/fake-id-99999", json={"test": "data"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_webhook_receiver_empty_body(client):
    create_response = client.post("/endpoints", json={"name": "Empty Body"})
    endpoint_id = create_response.json()["id"]

    response = client.post(f"/w/{endpoint_id}")
    assert response.status_code == status.HTTP_200_OK


def test_webhook_with_query_params(client):
    create_response = client.post("/endpoints", json={"name": "Query Test"})
    endpoint_id = create_response.json()["id"]

    response = client.post(
        f"/w/{endpoint_id}?token=abc123&user_id=456",
        json={"test": "data"}
    )
    assert response.status_code == status.HTTP_200_OK


def test_full_flow_create_and_receive(client):
    create_response = client.post("/endpoints", json={"name": "E2E Test"})
    assert create_response.status_code == 201
    endpoint_id = create_response.json()["id"]

    for i in range(3):
        webhook_response = client.post(
            f"/w/{endpoint_id}",
            json={"event": f"test_{i}"}
        )
        assert webhook_response.status_code == 200

    get_response = client.get(f"/endpoints/{endpoint_id}")
    assert get_response.status_code == 200

    endpoint_data = get_response.json()
    assert endpoint_data["id"] == endpoint_id