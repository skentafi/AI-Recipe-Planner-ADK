
"""
Inventory Routes Module
-----------------------

This module defines FastAPI routes related to inventory management.
It exposes endpoints that delegate to the Inventory Agent for cleaning
and filtering item lists, as well as basic health check routes.

Endpoints:
    GET /                - Root health check, returns a simple success message.
    GET /health          - Health status endpoint, returns {"status": "ok"}.
    POST /inventory      - Delegates to the Inventory Agent to filter usable items.
    POST /ask            - Stub endpoint for testing, simulates inventory agent behavior.

Usage:
    Imported into main.py and registered via app.include_router(inventory_routes.router).
"""
from fastapi import APIRouter
from agents import inventory_agent

router = APIRouter()

# Health check endpoints
@router.get("/")
def health_check():
    return {"message": "Success!"}

@router.get("/health")
def health():
    return {"status": "ok"}

# Stub /ask endpoint for testing
@router.post("/ask")
def ask(payload: dict):
    """
    This endpoint simulates the inventory agent.
    It accepts a JSON payload with 'items' and 'diet',
    and returns usable_items, diet_filtered, and suggestions.
    """
    items = payload.get("items", [])
    diet = payload.get("diet", "")

    # Filter out chicken breast if diet is vegan
    diet_filtered = [i for i in items if not (diet == "vegan" and i == "chicken breast")]

    return {
        "usable_items": [i for i in items if i.strip()],
        "diet_filtered": diet_filtered,
        "suggestions": ["Try a vegan salad"]
    }

@router.post("/inventory", response_model=inventory_agent.InventoryResponse)
async def filter_inventory(request: inventory_agent.InventoryInput):
    """
    Endpoint that delegates to the Inventory Agent.
    """
    return await inventory_agent.run_inventory(request.items)