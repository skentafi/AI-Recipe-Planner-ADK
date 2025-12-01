
import asyncio
import json
from unittest import runner
from agents.recipe_pipeline import recipe_pipeline  # your SequentialAgent pipeline
import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from config.app_config import APP_NAME, USER_ID, MODEL_NAME, retry_config, session_service, SESSION_ID, setup_session

async def main():
    """
    Entry point for testing the recipe_pipeline agent with the ADK InMemoryRunner.

    Steps performed:
    1. Construct an InMemoryRunner bound to the recipe_pipeline agent and the configured app name.
    2. Explicitly create a session in the runner's own session_service using APP_NAME, USER_ID, and SESSION_ID.
       This ensures the runner can locate and attach to the correct session.
    3. Send a sample user message containing pantry items and a diet preference ("vegan") to the pipeline.
    4. Iterate asynchronously over events returned by runner.run_async until the final response is received.
    5. Capture the agent's final response text, which should be a JSON string representing a recipe,
       and parse it into structured JSON for inspection.

    The function prints both the raw agent output and the parsed JSON to verify that the pipeline
    produces valid, structured recipe data.
    """
        
    # Step 1: Construct the runner
    runner = InMemoryRunner(agent=recipe_pipeline, app_name=APP_NAME)

    # Step 2: Explicitly create the session in the runner's own session_service
    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # Step 3: Run the pipeline
    final_response = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=json.dumps({
                "pantry_items":  [
                "tomato",
                "spinach",
                "chicken breast",
                "onion",
                "bell pepper",
                "garlic",
                "olive oil",
                "rice"],
                "diet": "vegan"
            }))]
        )
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    # Step 4: Print results
    print("Raw agent output:", final_response)
    print("Parsed JSON:", json.dumps(json.loads(final_response), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
