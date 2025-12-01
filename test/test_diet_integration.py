
"""
Integration Tests for Diet Routes
---------------------------------

This module contains integration tests that validate the FastAPI endpoints
exposed by the Diet Agent. Tests send HTTP requests to the running application
(via TestClient) and verify end-to-end behavior.

Tests focus on:
    - Status code and JSON response validation.
    - Presence and types of required keys: compatible_items, suggested_recipe_ideas.
    - Scenario-specific checks, such as vegan diets excluding non-vegan items.
    - Handling of varied input lists to confirm schema compliance.

These tests ensure that route wiring, request validation, and response
serialization all work correctly when the Diet API is deployed.
"""

import pytest
from fastapi.testclient import TestClient
import main
from main import app


client = TestClient(app)

def test_diet_route_vegan():
    payload = {"items": ["tomato", "chicken breast", "spinach"], "diet": "vegan"}
    response = client.post("/diet", json=payload)

    assert response.status_code == 200
    body = response.json()

    # Required keys
    for key in ["compatible_items", "suggested_recipe_ideas"]:
        assert key in body

    # Type checks
    assert isinstance(body["compatible_items"], list)
    assert isinstance(body["suggested_recipe_ideas"], list)

    # Scenario-specific check
    assert "chicken breast" not in body["compatible_items"]
