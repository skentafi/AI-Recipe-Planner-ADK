from fastapi import APIRouter, HTTPException
from models.inventory_schemas import InventoryInput
from models.planner_schemas import PlannerResponse
from google.genai import types
from config.app_config import APP_NAME, SESSION_ID, USER_ID
from agents.recipe_pipeline import recipe_pipeline
from runner_manager import RunnerManager
import json

router = APIRouter()

@router.post("/recipe", response_model=PlannerResponse)
async def recipe_endpoint(payload: InventoryInput) -> PlannerResponse:
    
    runner = await RunnerManager.init_runner(recipe_pipeline)

    user_content = types.Content(
        role="user",
        parts=[types.Part(text=payload.model_dump_json())]
    )

    final_response_content = None

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

    if not final_response_content:
        raise HTTPException(
            status_code=500,
            detail="No final response from recipe pipeline"
        )

    parsed_output = json.loads(final_response_content or "{}")

    return PlannerResponse(**parsed_output)
