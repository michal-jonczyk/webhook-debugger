import pytest
from datetime import datetime, timezone

def test_create_endpoint_success(clean_store):
    endpoint_id = "test-123"
    name = "My Test Endpoint"

    result = clean_store.create(endpoint_id=endpoint_id, name=name)

    assert result["id"] == endpoint_id
    assert result["name"] == name
    assert result["request_count"] == 0
    assert result["requests"] == []
    assert "created_at" in result
    assert isinstance(result["created_at"], datetime)


def test_create_endpoint_without_name(clean_store):
    endpoint_id = "test-456"

    result = clean_store.create(endpoint_id=endpoint_id,name=None)
    assert result["id"] == endpoint_id
    assert result["name"] is None


def test_create_multiple_endpoints(clean_store):
    endpoint1 = clean_store.create("id-1","Endpoint 1")
    endpoint2 = clean_store.create("id-2","Endpoint 2")

    assert endpoint1["id"] == "id-1"
    assert endpoint2["id"] == "id-2"
    assert endpoint1["name"] == "Endpoint 1"
    assert endpoint2["name"] == "Endpoint 2"
    assert clean_store.get("id-1") is not None
    assert clean_store.get("id-2") is not None


def test_get_existing_endpoint(clean_store):
    endpoint_id = "test-789"
    clean_store.create(endpoint_id, "Test")

    result = clean_store.get(endpoint_id)

    assert result is not None
    assert result["id"] == endpoint_id
    assert result["name"] == "Test"


def test_get_non_existing_endpoint(clean_store):
    result = clean_store.get("nonexistent-id")
    assert result is None


def test_add_request_success(clean_store,sample_webhook_data):
    endpoint_id = "test-add-request"
    clean_store.create(endpoint_id, "Test")

    result = clean_store.add_request(endpoint_id,sample_webhook_data)
    assert result is True

    endpoint = clean_store.get(endpoint_id)
    assert endpoint["request_count"] == 1
    assert len(endpoint["requests"]) == 1
    assert endpoint["requests"][0]["id"] == sample_webhook_data["id"]


def test_add_request_to_nonexisting_endpoint(clean_store,sample_webhook_data):
    result = clean_store.add_request("nonexistent-id",sample_webhook_data)

    assert result is False


def test_add_multiple_requests(clean_store,sample_webhook_data):
    endpoint_id = "test-multiple"
    clean_store.create(endpoint_id, "Test")

    for i in range(3):
        webhook_data = sample_webhook_data.copy()
        webhook_data["id"] = f"request-{i}"
        clean_store.add_request(endpoint_id,webhook_data)

    endpoint = clean_store.get(endpoint_id)
    assert endpoint["request_count"] == 3
    assert len(endpoint["requests"]) == 3


def test_max_requests_limit(clean_store, sample_webhook_data):
    endpoint_id = "test-limit"
    clean_store.create(endpoint_id, "Test")

    for i in range(101):
        webhook_data = sample_webhook_data.copy()
        webhook_data["id"] = f"request-{i}"
        clean_store.add_request(endpoint_id,webhook_data)

    endpoint = clean_store.get(endpoint_id)
    assert endpoint["request_count"] == 101
    assert len(endpoint["requests"]) == 100

    request_ids = [r["id"] for r in endpoint["requests"]]
    assert "request-0" not in request_ids
    assert "request-1" in request_ids


def test_increment_count(clean_store):
    endpoint_id = "test-counter"
    clean_store.create(endpoint_id, "Test")

    clean_store.increment_count(endpoint_id)
    clean_store.increment_count(endpoint_id)

    endpoint = clean_store.get(endpoint_id)
    assert endpoint["request_count"] == 2


def test_increment_count_nonexistent_endpoint(clean_store):
    clean_store.increment_count("nonexistent-id")

    assert True
