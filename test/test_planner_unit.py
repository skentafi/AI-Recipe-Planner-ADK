import pytest
from agents import planner_agent

@pytest.mark.asyncio
async def test_planner_agent_direct():
    compatible_items = ["tomato", "spinach", "garlic", "olive oil"]
    suggested_recipe_ideas = [
        "Vegan Tomato Soup",
        "Spinach Salad",
        "Tomato-Spinach Pasta",
        "Garlic Stir Fry",
        "Mediterranean Veggie Bowl"
    ]
    diet = "vegan"

    # Call the agent’s run function
    response = await planner_agent.run_planner(
        compatible_items=compatible_items,
        suggested_recipe_ideas=suggested_recipe_ideas,
        diet=diet
    )

    # --- Schema checks ---
    assert isinstance(response, planner_agent.PlannerResponse), "Response is not a PlannerResponse"
    assert isinstance(response.title, str), "Title must be a string"
    assert response.title.strip() != "", "Recipe title is empty"
    assert isinstance(response.ingredients, list), "Ingredients must be a list"
    assert len(response.ingredients) > 0, "Ingredients list is empty"
    assert isinstance(response.steps, list), "Steps must be a list"
    assert len(response.steps) > 0, "Steps list is empty"

    # --- Step structure checks ---
    for step in response.steps:
        assert isinstance(step.step_number, int), "Step number must be an integer"
        assert step.step_number > 0, "Step number must be positive"
        assert isinstance(step.instruction, str), "Instruction must be a string"
        assert step.instruction.strip() != "", "Instruction text is empty"

    # --- Debug output for inspection ---
    print("\nGenerated Recipe:")
    print(f"Title: {response.title}")
    print("Ingredients:", response.ingredients)
    print("Steps:")
    for step in response.steps:
        print(f" {step.step_number}. {step.instruction}")

