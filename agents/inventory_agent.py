# from models import InventoryResponse, InventoryInput
from config.app_config import APP_NAME, USER_ID, MODEL_NAME, retry_config, session_service, SESSION_ID
from typing import List
import json, os, asyncio, uuid
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# The Inventory Agent takes user input (a list of groceries) and checks this data, removing any unusable or blank entries. 
# It then outputs a cleaned list of ingredients ready for the next step.
# """
# # request example
# curl -X POST http://localhost:8000/inventory \
#      -H 'Content-Type: application/json' \
#      -d '{"items":["tomato"," ","chicken","spinach",""]}'
# Expected Response:
# {
#   "usable_items": ["tomato", "chicken", "spinach"],
#   "message": "Filtered usable items successfully."
# }
# """

# --- Input and Response schemas ---

# class InventoryInput(BaseModel):
#     """
#     Represents user input: a list of ingredients.
#     Example: {"items": ["chicken", "apple", " ", "??"]}
#     """
#     items: List[str] = Field(
#         ...,
#         description="List of raw ingredient names to be cleaned. "
#                     "Trim whitespace, drop invalid entries."
#     )

# class InventoryResponse(BaseModel):
#     usable_items: List[str] = Field(
#         ...,
#         description="Array of valid, non-empty ingredients suitable for cooking."
#     )
#     message: str = Field(
#         ...,
#         description="Short confirmation string summarizing the cleaning result."
#     )

# --- Prompt builder ---
# def create_prompt(user_input: InventoryInput) -> str:
#     return (
#         "You are a kitchen assistant. Given the list of ingredients:\n"
#         f"{user_input.items}\n"
#         "Return ONLY a valid JSON object with:\n"
#         "  usable_items: an array of non-empty, valid ingredients (trim whitespace, drop invalid entries)\n"
#         "  message: a short confirmation string\n"
#     )



# --- Constants ---
# #APP_NAME = "inventory_app"
# APP_NAME = "agents"
# USER_ID = "test_user"
# SESSION_ID = "inventory_session"
# MODEL_NAME = "gemini-2.5-flash-lite"

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment")

# --- Schemas ---
# class InventoryInput(BaseModel):
#     """
#     Represents user input: a list of ingredients.
#     Example: {"items": ["chicken", "apple", " ", "??"]}
#     """
#     items: List[str] = Field(
#         ...,
#         description="List of raw ingredient names to be cleaned. Trim whitespace, drop invalid entries."
#     )

# class InventoryResponse(BaseModel):
#     usable_items: List[str] = Field(
#         ...,
#         description="Array of valid, non-empty ingredients suitable for cooking."
#     )
#     message: str = Field(
#         ...,
#         description="Short confirmation string summarizing the cleaning result."
#     )

class InventoryInput(BaseModel):
    """
    Represents user input: a list of ingredients and diet type.
    Example: {"items": ["chicken", "apple", " ", "??"], "diet": "keto"}
    """
    items: List[str] = Field(
        ...,
        description="List of raw ingredient names to be cleaned. Trim whitespace, drop invalid entries."
    )
    diet: str = Field(
        ...,
        description="Diet type such as 'vegan', 'keto', 'vegetarian'. Passed through to DietAgent."
    )

class InventoryResponse(BaseModel):
    usable_items: List[str] = Field(
        ...,
        description="Array of valid, non-empty ingredients suitable for cooking."
    )
    diet: str = Field(
        ...,
        description="Diet type passed through for downstream agents."
    )
    message: str = Field(
        ...,
        description="Short confirmation string summarizing the cleaning result."
    )

"""
Configure Retry Options
When working with LLMs, you may encounter transient errors like rate limits or temporary service unavailability.
Retry options automatically handle these failures by retrying the request with exponential backoff.
"""
# retry_config=types.HttpRetryOptions(
#     attempts=5,  # Maximum retry attempts
#     exp_base=7,  # Delay multiplier
#     initial_delay=1,
#     http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
# )

# --- Agent definition ---
inventory_agent = LlmAgent(
    model=Gemini(
        model=MODEL_NAME,
        retry_options=retry_config
    ),
    name="inventory_agent",
    input_schema=InventoryInput,
    output_schema=InventoryResponse,
    output_key="inventory_result",
    description="Filters unusable ingredients and returns a clean list.",
    instruction=f"""You are a kitchen assistant.
The user will provide the ingredient list and diet type in JSON format like {{"items": ["chicken","apple","??"], "diet": "keto"}}.
Clean the ingredient list (trim whitespace, drop invalid entries) and pass the diet type forward unchanged.
Respond ONLY with a JSON object matching this exact schema:
{json.dumps(InventoryResponse.model_json_schema(), indent=2)}"""
)

# --- Session + Runner setup ---
# session_service = InMemorySessionService()

inventory_runner = Runner(
    agent=inventory_agent,
    app_name=APP_NAME,
    session_service=session_service
)

async def run_inventory(items: List[str], diet: str = "unknown") -> InventoryResponse:

    # Build user message from schema (include diet to satisfy Pydantic)
    query_json = InventoryInput(items=items, diet=diet).model_dump_json()
    user_content = types.Content(role="user", parts=[types.Part(text=query_json)])

    final_response_content = None
    async for event in inventory_runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = event.content.parts[0].text

    print(f"<<< Agent Response: {final_response_content}")

    # Retrieve from session state via output_key
    current_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    stored_output = None
    if current_session and inventory_agent.output_key:
        stored_output = current_session.state.get(inventory_agent.output_key)

    usable_items = []

    # First try stored_output
    if stored_output:
        if isinstance(stored_output, str):
            try:
                parsed_output = json.loads(stored_output)
                usable_items = parsed_output.get("usable_items", [])
            except json.JSONDecodeError:
                pass
        elif isinstance(stored_output, dict):
            usable_items = stored_output.get("usable_items", [])

    # If still empty, try parsing final_response_content
    if not usable_items and final_response_content:
        try:
            parsed_output = json.loads(final_response_content)
            usable_items = parsed_output.get("usable_items", [])
        except json.JSONDecodeError:
            pass

    # Fallback: return original items if agent gave nothing
    if not usable_items and items:
        usable_items = [i.strip() for i in items if i.strip()]
        
    return InventoryResponse(
        usable_items=usable_items,
        message="Filtered usable items successfully.",
        diet=diet
    )


# --- Quick test harness ---
if __name__ == "__main__":
    result = asyncio.run(run_inventory(["tomato", "chicken breast", "spinach", " "], diet="omnivore"))
    print(result)

