from pydantic import BaseModel
from typing import List
from pydantic import BaseModel, Field
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.tools import google_search
import json
from models.planner_schemas import PlannerInput, PlannerResponse
from config.app_config import APP_NAME, USER_ID, MODEL_NAME, retry_config, session_service, SESSION_ID
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# async def search_tool(query: str):
#     return await google_search({"query": query})

planner_agent = Agent(
    model=Gemini(
        model=MODEL_NAME,
        retry_options=retry_config
    ),
    name="planner_agent",
    input_schema=PlannerInput,
    output_schema=PlannerResponse,
    output_key="planner_result",
    # tools=[google_search],
    # tools=[search_tool],
    description="Chooses the best recipe idea and expands it into a full recipe.",
    instruction = f"""
You are a kitchen assistant.
The diet agent will provide compatible items and recipe ideas in JSON format like:
{{
  "compatible_items": ["tomato","spinach"],
  "suggested_recipe_ideas": ["Vegan Tomato Soup","Spinach Salad","Tomato-Spinach Pasta"],
  "diet": "vegan"
}}.
- Choose the best recipe idea from the list.
- Expand it into a complete recipe with title, ingredients, and step-by-step instructions.
Respond ONLY with a JSON object matching this exact schema:
{json.dumps(PlannerResponse.model_json_schema(), indent=2)}
"""
##### AFC is always active because the SDK enforces it whenever tools are attached. 
##### It’s not the prompt or the agent design — it’s the runtime’s default. 
##### That’s why the course demos worked (different environment, no AFC enforcement), but our test fail.
##### conceptually, an agent should be able to “choose its workflow.” But in ADK, that choice lives in 
##### the orchestration layer, not inside the agent itself. That’s why you felt blocked — 
##### you were trying to make PlannerAgent both schema‑bound and tool‑driven. Splitting them is the way forward.
#     instruction = f"""
# You are a kitchen assistant.
# The diet agent will provide compatible items and recipe ideas in JSON format like:
# {{
#   "compatible_items": ["tomato","spinach"],
#   "suggested_recipe_ideas": ["Vegan Tomato Soup","Spinach Salad","Tomato-Spinach Pasta"],
#   "diet": "vegan"
# }}.
# - Choose the best recipe idea from the list.
# - Use the google_search tool if needed to enrich the recipe with realistic ingredients and cooking steps.
# - Expand it into a complete recipe with title, ingredients, and step-by-step instructions.
# Respond ONLY with a JSON object matching this exact schema:
# {json.dumps(PlannerResponse.model_json_schema(), indent=2)}
# """
)

planner_runner = Runner(
    agent=planner_agent,
    app_name=APP_NAME,
    session_service=session_service
)

async def run_planner(compatible_items: List[str], suggested_recipe_ideas: List[str], diet: str) -> PlannerResponse:

    # await session_service.create_session(
    #     app_name=APP_NAME,
    #     user_id=USER_ID,
    #     session_id=SESSION_ID
    # )

    # Build user message from schema
    query_json = PlannerInput(
        compatible_items=compatible_items,
        suggested_recipe_ideas=suggested_recipe_ideas,
        diet=diet
    ).model_dump_json()

    user_content = types.Content(role="user", parts=[types.Part(text=query_json)])

    # Run agent asynchronously
    async for event in planner_runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_content
    ):
        if event.is_final_response():
            final_response_content = (
                event.content.parts[0].text
                if event.content and event.content.parts
                else None
            )

    # Retrieve from session state via output_key
    current_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    stored_output = None
    if current_session and planner_agent.output_key:
        stored_output = current_session.state.get(planner_agent.output_key)

    title, ingredients, steps = "", [], []
    if stored_output:
        try:
            parsed_output = (
                json.loads(stored_output)
                if isinstance(stored_output, str)
                else stored_output
            )
            title = parsed_output.get("title", "")
            ingredients = parsed_output.get("ingredients", [])
            steps = parsed_output.get("steps", [])
        except (json.JSONDecodeError, AttributeError):
            pass

    return PlannerResponse(
        title=title,
        ingredients=ingredients,
        steps=steps
    )
