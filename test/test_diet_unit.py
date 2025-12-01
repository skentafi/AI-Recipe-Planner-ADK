import pytest
from agents import diet_agent

@pytest.mark.asyncio
async def test_diet_agent_direct():
    items = ["tomato", "chicken breast", "spinach"]
    diet = "vegan"

    response = await diet_agent.run_diet(items, diet)

    # Schema checks
    assert isinstance(response.compatible_items, list)
    assert isinstance(response.suggested_recipe_ideas, list)

    # Scenario-specific check
    assert "chicken breast" not in response.compatible_items

    # Display lists for debugging / inspection
    print("\nCompatible items:", response.compatible_items)
    print("Suggested recipe ideas:", response.suggested_recipe_ideas)
