import pytest
import json
from agents.recipe_pipeline import recipe_pipeline
import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from config.app_config import APP_NAME, USER_ID, MODEL_NAME, retry_config, session_service, SESSION_ID


@pytest.mark.asyncio
async def test_recipe_pipeline_generates_valid_json():
    """
    Verify that the recipe_pipeline SequentialAgent produces valid structured JSON output.

    This test constructs an InMemoryRunner with the recipe_pipeline agent,
    ensures a session is created for the given APP_NAME, USER_ID, and SESSION_ID,
    and then runs the pipeline with a sample input message containing pantry items
    and a diet preference.

    The test asserts that the final agent response can be parsed as JSON and
    contains the expected top-level keys: "title", "ingredients", and "steps".
    It also checks that "steps" is returned as a list, confirming the pipeline
    generates a usable recipe format.
    """
    runner = InMemoryRunner(agent=recipe_pipeline, app_name=APP_NAME)

    # without await the session is not created and tests fail by session inexistant
    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    final_response = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=json.dumps({
                "pantry_items": ["tomato", "spinach"],
                "diet": "vegan"
            }))]
        )
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text

    parsed = json.loads(final_response)
    assert "title" in parsed
    assert "ingredients" in parsed
    assert "steps" in parsed
    assert isinstance(parsed["steps"], list)


@pytest.mark.asyncio
async def test_recipe_pipeline_includes_chicken_for_omnivore():
    """
    Verify that the recipe_pipeline includes chicken when diet is set to 'omnivore'.
    """
    runner = InMemoryRunner(agent=recipe_pipeline, app_name=APP_NAME)
    await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    final_response = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=json.dumps({
                "pantry_items": ["tomato", "spinach", "chicken breast"],
                "diet": "omnivore"
            }))]
        )
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text

    parsed = json.loads(final_response)
    assert any("chicken" in ing.lower() for ing in parsed["ingredients"])