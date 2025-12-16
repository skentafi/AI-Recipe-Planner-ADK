"""
Integration tests for the Inventory API route.

This module validates the current `/inventory` endpoint using FastAPI's
TestClient, sending in-memory HTTP requests to the running application
instance imported from `main`.

The tests verify:
    - Correct HTTP status codes and JSON response structure.
    - Required response fields (`usable_items`, `message`) and their types.
    - Basic diet-aware filtering behavior when applicable (e.g., vegan inputs).
    - Proper handling of empty or whitespace-only item lists.

These tests reflect the existing Inventory implementation and ensure that
routing, request parsing, and response serialization behave as expected
without modifying the underlying agent or runner structure.
"""
# File: tests/test_inventory_integration.py

# tests/test_inventory_agent_pytest.py
# run the test using: pytest main_tests.py -v ## -v → verbose mode, shows each test name and result.
# to run the server: uvicorn main:app --reload --log-level debug
# pytest test/test_inventory_integration.py -v --disable-warnings

import os
import pytest
from fastapi.testclient import TestClient
# from app.main import app
import main
from tests.test_main import app


client = TestClient(app)

def test_api_key_loaded():
    # Still useful to confirm environment setup
    API_KEY = os.getenv("GEMINI_API_KEY") # adjust path if needed
    assert API_KEY is not None, "Google API key must be set in .env"

def test_health_endpoint():
    """
    Verify that the FastAPI service is alive and returns status 'ok'.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
    print("✅ Health endpoint is reachable and reports status 'ok'.")

def test_inventory_route_basic():
    """
    Integration test: send payload to /inventory and validate response structure.
    """
    payload = {"items": ["tomato", "chicken breast", "spinach"], "diet": "vegan"}
    response = client.post("/api/inventory", json=payload)

    assert response.status_code == 200
    body = response.json()

    # Required keys must exist (InventoryResponse schema)
    for key in ["usable_items", "message"]:
        assert key in body, f"Missing key: {key}"

    # Type checks
    assert isinstance(body["usable_items"], list)
    assert isinstance(body["message"], str)

def test_inventory_route_empty_items():
    """
    Integration test: empty items should return usable_items == []
    """
    payload = {"items": ["", " ", ""], "diet": "vegan"}
    response = client.post("/api/inventory", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["usable_items"] == []
    assert isinstance(body["message"], str)
