
"""
Integration tests for the Diet API routes.

This module verifies the FastAPI endpoints backed by the Diet Agent using
FastAPI's TestClient, allowing in‑memory request simulation without launching
a live server.

The tests validate:
    - Correct HTTP status codes and JSON response structure.
    - Required response fields (compatible_items, suggested_recipe_ideas) and
      their expected types.
    - Diet-specific behavior, such as vegan inputs excluding non-vegan items.
    - Robust handling of varied input lists to ensure schema and validation
      consistency.

Together, these tests confirm that routing, request parsing, agent invocation,
and response serialization function correctly across the Diet API surface.
"""


import pytest
from fastapi.testclient import TestClient
import main
from tests.test_main import app


client = TestClient(app)

# def test_diet_route_vegan():
#     """
#     Integration test for the /diet route.
#     Validates that the DietAgent correctly filters non-vegan items
#     and returns structured response fields.
#     """
#     payload = {
#         "items": ["tomato", "chicken breast", "spinach"],
#         "diet": "vegan"
#     }
#     response = client.post("/api/diet", json=payload)

#     # --- Basic response validation ---
#     assert response.status_code == 200
#     body = response.json()

#     # --- Required keys ---
#     # The response must contain both compatible_items and suggested_recipe_ideas
#     for key in ["compatible_items", "suggested_recipe_ideas"]:
#         assert key in body

#     # --- Type checks ---
#     # Both fields should be lists, even if empty
#     assert isinstance(body["compatible_items"], list)
#     assert isinstance(body["suggested_recipe_ideas"], list)

#     # --- Scenario-specific check ---
#     # Since the diet is vegan, "chicken breast" must not appear in compatible_items
#     assert "chicken breast" not in body["compatible_items"]


def test_diet_route_vegan():
    """
    Integration test for the /diet route.
    Validates that the DietAgent correctly filters non-vegan items
    and returns structured response fields.
    """
    payload = {
        "items": ["tomato", "chicken breast", "spinach"],
        "diet": "vegan"
    }

    response = client.post("/api/diet", json=payload)

    # --- Basic response validation ---
    assert response.status_code == 200
    body = response.json()

    # --- Required keys ---
    for key in ["compatible_items", "suggested_recipe_ideas"]:
        assert key in body

    # --- Type checks ---
    assert isinstance(body["compatible_items"], list)
    assert isinstance(body["suggested_recipe_ideas"], list)

    # --- Scenario-specific check ---
    assert "chicken breast" not in body["compatible_items"]


# def test_diet_route_vegan():
#     """
#     Integration test for the /diet route.
#     Validates that the DietAgent correctly filters non-vegan items
#     and returns structured response fields.
#     """
#     # payload = {"items": ["tomato", "chicken breast", "spinach"], "diet": "vegan"}
#     payload = {
#     "ingredients": ["tomato", "chicken breast", "spinach"],
#     "diet_type": "vegan"
#     }

#     response = client.post("/api/diet", json=payload)

#     # --- Basic response validation ---
#     assert response.status_code == 200
#     body = response.json()

#     # --- Required keys ---
#     for key in ["compatible_items", "suggested_recipe_ideas"]:
#         assert key in body

#     # --- Type checks ---
#     assert isinstance(body["compatible_items"], list)
#     assert isinstance(body["suggested_recipe_ideas"], list)

#     # --- Scenario-specific check ---
#     assert "chicken breast" not in body["compatible_items"]