"""
Diet Routes Module
------------------

This module defines FastAPI routes related to diet planning.
It exposes endpoints that delegate to the Diet Agent for generating
compatible items and recipe suggestions based on dietary preferences.

Endpoints:
    GET /health          - Health status endpoint, returns {"status": "ok"}.
    POST /diet           - Delegates to the Diet Agent to suggest recipes
                           and filter items according to the specified diet.

Usage:
    Imported into main.py and registered via app.include_router(diet_routes.router).
"""


from fastapi import APIRouter, HTTPException
from models.diet_schemas import DietInput, DietResponse
# from models.planner_schemas import PlannerResponse
from google.genai import types
from config.app_config import APP_NAME, SESSION_ID, USER_ID
from agents.diet_agent import diet_agent
from runner_manager import RunnerManager
import json

router = APIRouter()

@router.post("/diet", response_model=DietResponse)
async def diet_endpoint(payload: DietInput) -> DietResponse:
    """
    Diet endpoint.
    Uses the DietAgent pipeline to filter items based on dietary rules
    and return structured suggestions.
    """

    # Initialize (or reuse) the singleton runner for the DietAgent
    runner = await RunnerManager.init_runner(diet_agent)

    # Convert payload to JSON string for the agent
    user_content = types.Content(
        role="user",
        parts=[types.Part(text=payload.model_dump_json())]
    )

    final_response_content = None

    # Stream events from the agent until the final response arrives
    async for event in runner.run_async(
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

    # Ensure we received a final response
    if not final_response_content:
        raise HTTPException(
            status_code=500,
            detail="No final response from diet pipeline"
        )

    # Parse JSON output safely
    parsed_output = json.loads(final_response_content or "{}")

    # Return typed response model
    return DietResponse(**parsed_output)

