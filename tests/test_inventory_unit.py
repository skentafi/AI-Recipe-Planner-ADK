"""
Unit Tests for Inventory Agent
------------------------------

This module contains unit tests that validate the Inventory Agent logic
directly, without running Uvicorn or hitting FastAPI routes.

Tests focus on:
    - Schema validation of InventoryResponse.
    - Cleaning logic for usable_items (e.g., stripping empty strings).
    - Ensuring agent runner returns expected types and values.

These tests are fast and isolated, designed to catch logic errors early
before integration with the API layer.
"""

# to test: pytest test/test_inventory_unit.py -v --disable-warnings

from agents import inventory_agent
import pytest

@pytest.mark.asyncio
async def test_inventory_agent_direct():
    """
    Unit test: validate Inventory Agent logic directly via its runner wrapper.

    Checks:
        - Response schema matches InventoryResponse.
        - 'usable_items' is cleaned (no empty strings).
        - 'message' is returned as a string.
        - 'tomato' remains in usable_items after cleaning.
    """
    # Prepare input
    payload = inventory_agent.InventoryInput(
    items=["tomato", "chicken breast", "spinach", " "],
    diet="omnivore"   # or "vegan", "unknown", etc.
)

    # Run agent directly through its runner wrapper
    response = await inventory_agent.run_inventory(payload.items, diet=payload.diet)

    # Validate schema
    assert isinstance(response.usable_items, list)
    assert isinstance(response.message, str)

    # Check cleaning logic
    assert " " not in response.usable_items
    assert "tomato" in response.usable_items

# test/test_inventory_unit.py

@pytest.mark.asyncio
async def test_inventory_agent_direct():
    # Prepare input with diet included
    payload = inventory_agent.InventoryInput(
        items=["tomato", "chicken breast", "spinach", " "],
        diet="omnivore"   # or "vegan", "unknown", etc.
    )

    response = await inventory_agent.run_inventory(payload.items, diet=payload.diet)

    # Assertions
    assert isinstance(response.usable_items, list)
    assert "tomato" in response.usable_items
    assert response.message == "Filtered usable items successfully."

