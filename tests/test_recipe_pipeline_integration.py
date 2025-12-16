"""
Integration tests for the Recipe API route.

This module exercises the `/recipe` endpoint end-to-end using FastAPI's
TestClient, allowing HTTP requests to be simulated entirely in memory.
The test application is constructed in `test_main.py`, which assembles
a test-only FastAPI instance with all relevant routers included.

These tests validate the complete execution path:
    - Request payload parsing and validation.
    - Route → recipe pipeline invocation.
    - Response schema structure and field types.
    - Correct handling of realistic ingredient lists and constraints.

The objective is to ensure that the `/recipe` endpoint returns a well-formed
RecipeResponse when driven through the full FastAPI interface.
"""


from fastapi.testclient import TestClient
from tests.test_main import app

# TestClient(app) automatically runs lifespan, so RunnerManager.init_runner(recipe_pipeline) 
# executes before the first request.
# client = TestClient(app)

def test_recipe_route():
    payload = {
        "items": ["tomato", "spinach", "garlic", "olive oil", "chicken breast"],
        "diet": "keto"
    }

     # ✅ context manager ensures lifespan runs
    with TestClient(app) as client:
        response = client.post("/api/recipe", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "ingredients" in data
        assert "steps" in data
