# agents/recipe_pipeline.py  
import logging
from google.adk.agents import Agent, SequentialAgent
from google.adk.runners import InMemoryRunner
from agents import inventory_agent, diet_agent, planner_agent
from config.app_config import APP_NAME

# Define the pipeline by chaining the three agents
recipe_pipeline = SequentialAgent(
    name="RecipePipeline",
    sub_agents=[inventory_agent.inventory_agent, diet_agent.diet_agent, planner_agent.planner_agent]
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
    runner = InMemoryRunner(agent=recipe_pipeline)

    # # Run the pipeline with structured input
    # response = await runner.run_debug(
    #     {
    #         "pantry_items": pantry_items,
    #         "diet": diet,
    #     }
    # )

    logging.debug(f"Running recipe pipeline with pantry={pantry_items}, diet={diet}")
    # Run the pipeline with structured input
    response = await runner.run_debug(
        {
            "pantry_items": pantry_items,
            "diet": diet,
        }
    )
    logging.info(f"Pipeline response: {response}")


    return response
