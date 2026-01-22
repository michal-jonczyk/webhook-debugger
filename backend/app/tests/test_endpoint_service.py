import pytest
from unittest.mock import Mock
from fastapi import HTTPException

def test_create_endpoint_with_name(clean_service):
    name = "My Webhook"
    result = clean_service.create_endpoint(name=name)

    assert "id" in result
    assert "url" in result
    assert "name" in result
    assert "created_at" in result
    assert result["name"] == name
    assert result["url"].startswith("http://localhost:8000/w/")
    assert len(result["id"]) == 36


def test_create_endpoint_without_name(clean_service):
    result = clean_service.create_endpoint(name=None)

    assert result["name"] is None
    assert "id" in result
    assert "url" in result


def test_create_endpoint_generates_unique_ids(clean_service):
    endpoint1 = clean_service.create_endpoint("Endpoint 1")
    endpoint2 = clean_service.create_endpoint("Endpoint 2")

    assert endpoint1["id"] != endpoint2["id"]


def test_get_existing_endpoint(clean_service):
    created = clean_service.create_endpoint("Endpoint 1")
    endpoint_id = created["id"]

    result = clean_service.get_endpoint(endpoint_id)

    assert result is not None
    assert result["id"] == endpoint_id
    assert result["name"] == "Endpoint 1"
    assert result["url"] == f"http://localhost:8000/w/{endpoint_id}"


def test_get_nonexistent_endpoint(clean_service):
    result = clean_service.get_endpoint("fake-id-12345")

    assert result is None


@pytest.mark.asyncio
async def test_receive_webhook_success(clean_service):
    create = clean_service.create_endpoint("Test")
    endpoint_id = create["id"]

    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.headers = {"Content-Type": "application/json"}
    mock_request.query_params = {}
    mock_request.client = Mock()
    mock_request.client.host = "127.0.0.1"

    async def mock_body():
        return b'{"test": "data"}'
    mock_request.body = mock_body

    result = await clean_service.receive_webhook(endpoint_id, mock_request)

    assert result["status"] == "received"
    assert result["endpoint_id"] == endpoint_id
    assert "request_id" in result
    assert "received_at" in result
    assert result["total_requests"] == 1


@pytest.mark.asyncio
async def test_receive_webhook_nonexistent_endpoint(clean_service):
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.headers = {}
    mock_request.query_params = {}
    mock_request.client = None

    async def mock_body():
        return b''

    mock_request.body = mock_body

    with pytest.raises(HTTPException) as exc_info:
        await clean_service.receive_webhook("fake-id",mock_request)

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_receive_webhook_with_json_body(clean_service):
    created = clean_service.create_endpoint("Test")
    endpoint_id = created["id"]

    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.headers = {"content-type": "application/json"}
    mock_request.query_params = {}
    mock_request.client = None

    json_data = '{"key": "value", "number": 123}'

    async def mock_body():
        return json_data.encode('utf-8')

    mock_request.body = mock_body

    result = await clean_service.receive_webhook(endpoint_id, mock_request)

    assert result["status"] == "received"

    endpoint = clean_service.store.get(endpoint_id)
    saved_request = endpoint["requests"][0]
    assert saved_request["body_json"] == {"key": "value", "number": 123}
    assert saved_request["body_raw"] == json_data


@pytest.mark.asyncio
async def test_receive_webhook_with_invalid_json(clean_service):
    created = clean_service.create_endpoint("Test")
    endpoint_id = created["id"]

    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.headers = {"content-type": "application/json"}
    mock_request.query_params = {}
    mock_request.client = None

    invalid_json = '{invalid json}'

    async def mock_body():
        return invalid_json.encode('utf-8')

    mock_request.body = mock_body

    result = await clean_service.receive_webhook(endpoint_id, mock_request)
    assert result["status"] == "received"

    endpoint = clean_service.store.get(endpoint_id)
    saved_request = endpoint["requests"][0]
    assert saved_request["body_json"] is None
    assert saved_request["body_raw"] == invalid_json


@pytest.mark.asyncio
async def test_receive_multiple_webhooks(clean_service):
    created = clean_service.create_endpoint("Test")
    endpoint_id = created["id"]

    for i in range(3):
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.headers = {}
        mock_request.query_params = {}
        mock_request.client = None

        async def mock_body():
            return f'{{"request": {i}}}'.encode('utf-8')

        mock_request.body = mock_body

        await clean_service.receive_webhook(endpoint_id, mock_request)

    endpoint = clean_service.store.get(endpoint_id)
    assert endpoint["request_count"] == 3
    assert len(endpoint["requests"]) == 3



