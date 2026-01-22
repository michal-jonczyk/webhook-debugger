import pytest
from fastapi.testclient import TestClient
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from storage.store import EndpointStore
from services.endpoint_service import EndpointService
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def clean_store():
    store = EndpointStore()
    return store


@pytest.fixture
def clean_service(clean_store):
    service = EndpointService()
    service.store = clean_store
    return service


@pytest.fixture
def sample_endpoint_data():
    return {
        "id": "test-endpoint-123",
        "name": "test-endpoint",
        "created_at": datetime.now(),
        "request_count": 0,
        "requests": []
    }


@pytest.fixture
def sample_webhook_data():

    return {
        "id": "webhook-request-456",
        "timestamp": datetime.now(),
        "method": "POST",
        "headers": {"content-type": "application/json"},
        "body_raw": '{"test": "data"}',
        "body_json": {"test": "data"},
        "content_type": "application/json",
        "content_length": 16,
        "ip_address": "127.0.0.1",
        "query_params": {}
    }