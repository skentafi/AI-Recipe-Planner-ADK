# agents/recipe_pipeline.py  
import logging
from google.adk.agents import SequentialAgent
from google.adk.runners import InMemoryRunner
from agents.inventory_agent import inventory_agent
from agents.diet_agent import diet_agent
from agents.planner_agent import planner_agent
from config.app_config import APP_NAME, SESSION_ID, USER_ID
# from runner_factory import get_runner

# Define the pipeline by chaining the three agents
recipe_pipeline = SequentialAgent(
    name="RecipePipeline",
    sub_agents=[inventory_agent, diet_agent,planner_agent]
)

# # Optional: helper function to run the pipeline end-to-end
async def run_recipe_pipeline(pantry_items: list[str], diet: str):
    """
    Run the full recipe pipeline:
    1. InventoryAgent filters pantry items
    2. DietAgent applies diet rules and suggests recipes
    3. PlannerAgent expands one recipe idea into full recipe
    """
    # Wrap the root pipeline agent in an InMemoryRunner
    runner = InMemoryRunner(agent=recipe_pipeline, app_name=APP_NAME)

    # Run the pipeline with structured input
    response = await runner.run_debug(
        {
            "pantry_items": pantry_items,
            "diet": diet,
        }
    )

    logging.debug(f"Running recipe pipeline with pantry={pantry_items}, diet={diet}")
    # Run the pipeline with structured input
    # runner = get_runner(recipe_pipeline, app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    response = await runner.run_debug(
        {
            "pantry_items": pantry_items,
            "diet": diet,
        }
    )
    logging.info(f"Pipeline response: {response}")


    return response
