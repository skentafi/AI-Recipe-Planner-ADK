# config/app_config.py
from google.genai import types
from google.adk.sessions import InMemorySessionService

# Global constants
# APP_NAME = "ai_diet_meal_planner" #"inventory_app"
# APP_NAME = "ai_diet_meal_planner"
APP_NAME = "agents"
USER_ID = "test_user"
SESSION_ID = "recipe_session"
MODEL_NAME = "gemini-2.5-flash-lite"



# Shared session service (singleton by module import)
session_service = InMemorySessionService()

async def setup_session():
    """
    Ensure a session exists for the pipeline.
    Call this once before running any agent workflow.
    """
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

"""
Configure Retry Options
When working with LLMs, you may encounter transient errors like rate limits or temporary service unavailability.
Retry options automatically handle these failures by retrying the request with exponential backoff.
"""
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)
