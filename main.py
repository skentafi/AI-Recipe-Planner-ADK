
import asyncio
import json
from unittest import runner
from agents.recipe_pipeline import recipe_pipeline  # your SequentialAgent pipeline
import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from config.app_config import APP_NAME, USER_ID, MODEL_NAME, retry_config, session_service, SESSION_ID, setup_session
import logging
import os

def setup_logging():
    for log_file in ["logger.log"]:
        if os.path.exists(log_file):
            os.remove(log_file)

    logging.basicConfig(
        filename="logger.log",
        # level=logging.DEBUG,
        # switch from DEBUG to INFO to reduce verbosity
        # cut out the noisy TCP/TLS traces and kept only the essentials:
        # Startup confirmation: Logging configured for Recipe Pipeline
        # Model requests: each time Gemini is called, you see the request/response cycle.
        # Pipeline outputs: the final structured recipe JSON output from the pipeline
        level=logging.INFO, 
        format="%(asctime)s %(filename)s:%(lineno)d %(levelname)s:%(message)s",
    )
    logging.info("✅ Logging configured for Recipe Pipeline")


async def main():
    """
    Entry point for testing the recipe_pipeline agent with the ADK SequentialAgent and InMemoryRunner.

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

    setup_logging()

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
        # Log the raw event class/type for visibility
        logging.debug(f"Event received: {type(event).__name__}")

        # Final response case
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text
            agent_name = getattr(event, "source_agent", "UnknownAgent")
            logging.info(f"Final response from {agent_name}: {response_text}")
            final_response = response_text  # keep the latest full response
        # Intermediate content case
        elif event.content:
            logging.debug(f"Intermediate content: {event.content}")
        # Catch-all for other event types
        else:
            logging.warning(f"Unhandled event: {event}")


    # Step 4: Print results
    print("Raw agent output:", final_response)
    print("Parsed JSON:", json.dumps(json.loads(final_response), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
