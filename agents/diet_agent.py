from typing import List
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner   
from models.diet_schemas import DietInput, DietResponse
import json
from config.app_config import APP_NAME, USER_ID, MODEL_NAME, retry_config, session_service, SESSION_ID

from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# --- Agent definition ---
diet_agent = LlmAgent(
    model=Gemini(
        model=MODEL_NAME,
        retry_options=retry_config
    ),
    name="diet_agent",
    input_schema=DietInput,
    output_schema=DietResponse,
    output_key="diet_result",
    description="Suggests diet-compatible items and recipe ideas.",
    instruction = f"""
    You are a nutrition assistant.
    The inventory agent will provide available items in JSON format like:
    {{"items": ["tomato","chicken","spinach"], "diet": "vegan"}}.
    - Filter items to only those compatible with the given diet.
    - Include 5 recipe ideas using only the compatible items.
    Respond ONLY with a JSON object matching this exact schema:
    {json.dumps(DietResponse.model_json_schema(), indent=2)}
    """
)

# --- Session + Runner setup ---
diet_runner = Runner(
    agent=diet_agent,
    app_name=APP_NAME,
    session_service=session_service
)

# Assuming these are already defined/imported in your module:
# session_service, diet_runner, diet_agent, APP_NAME, USER_ID
async def run_diet(items: List[str], diet: str) -> DietResponse:
    # Ensure session exists (shared session_id passed from pipeline)
    # await session_service.create_session(
    #     app_name=APP_NAME,
    #     user_id=USER_ID,
    #     session_id=SESSION_ID
    # )

    # Build user message from schema
    query_json = DietInput(items=items, diet=diet).model_dump_json()
    user_content = types.Content(role="user", parts=[types.Part(text=query_json)])

    final_response_content = None
    async for event in diet_runner.run_async(
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
        session_id= SESSION_ID
    )

    stored_output = None
    if current_session and diet_agent.output_key:
        stored_output = current_session.state.get(diet_agent.output_key)

    compatible_items, suggested_recipe_ideas = [], []

    # First try stored_output
    if stored_output:
        try:
            parsed_output = (
                json.loads(stored_output)
                if isinstance(stored_output, str)
                else stored_output
            )
            compatible_items = parsed_output.get("compatible_items", [])
            suggested_recipe_ideas = parsed_output.get("suggested_recipe_ideas", [])
        except (json.JSONDecodeError, AttributeError):
            pass

    # If still empty, try parsing final_response_content
    if not compatible_items and final_response_content:
        try:
            parsed_output = json.loads(final_response_content)
            compatible_items = parsed_output.get("compatible_items", [])
            suggested_recipe_ideas = parsed_output.get("suggested_recipe_ideas", [])
        except json.JSONDecodeError:
            pass

    # Fallback: if still empty, assume all items are compatible
    if not compatible_items and items:
        compatible_items = items
        suggested_recipe_ideas = ["Fallback recipe idea based on available items"]

    return DietResponse(
        compatible_items=compatible_items,
        suggested_recipe_ideas=suggested_recipe_ideas
    )