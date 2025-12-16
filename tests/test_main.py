
"""
tests/test_main.py
------------

This file defines a **test-only FastAPI application** used for integration testing.
It assembles the app by including the existing route modules (inventory, diet, and recipe),
but does not contain any test functions itself.

Note:
- For testing, we keep a separate `test_main.py` so that pytest can import
  a clean app instance without mixing in demo code or unit tests.
- Other integration test files (e.g., test_recipe_integration.py) import
  `app` from here and use FastAPI's `TestClient` to send requests in memory.
"""

from fastapi import FastAPI
from routes.inventory_routes import router as inventory_router
from routes.diet_routes import router as diet_router
from routes.recipe_routes import router as recipe_router
# from routes.recipe_routes import lifespan
from contextlib import asynccontextmanager
from runner_manager import RunnerManager
from agents.recipe_pipeline import recipe_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> Lifespan startup running")
    # Startup logic
    # await RunnerManager.init_runner(recipe_pipeline)
    yield
    print(">>> Lifespan shutdown running")
    # Shutdown logic (optional)
    await RunnerManager.shutdown_runner()

# Build a test-only FastAPI app
# app = FastAPI(title="Test App: Recipe & Diet API")
app = FastAPI(lifespan=lifespan, title="Test App: Recipe & Diet API")

app.include_router(inventory_router, prefix="/api", tags=["inventory"])
app.include_router(diet_router, prefix="/api", tags=["diet"])
app.include_router(recipe_router, prefix="/api", tags=["recipe"])
