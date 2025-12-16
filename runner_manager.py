# runner_manager.py
from google.adk.runners import InMemoryRunner
from config.app_config import APP_NAME, USER_ID, SESSION_ID

class RunnerManager:
    _runner = None
    _agent = None

    @classmethod
    async def init_runner(cls, agent):
        """
        Initialize the singleton runner with a specific agent.
        Creates the session once.
        """
        if cls._runner is None or cls._agent != agent:
            cls._agent = agent
            cls._runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
            await cls._runner.session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID
            )
        return cls._runner

    @classmethod
    def get_runner(cls):
        """
        Return the existing runner instance.
        Must be initialized first with init_runner(agent).
        """
        if cls._runner is None:
            raise RuntimeError("Runner not initialized. Call init_runner(agent) first.")
        return cls._runner

    @classmethod
    async def shutdown_runner(cls):
        """
        Clean up the runner instance and release resources.
        Called during FastAPI lifespan shutdown.
        """
        if cls._runner is not None:
            try:
                # If the runner has a shutdown/close method, call it
                if hasattr(cls._runner, "close"):
                    await cls._runner.close()
                elif hasattr(cls._runner, "shutdown"):
                    await cls._runner.shutdown()
            except Exception as e:
                # Log or print for debugging, but don't block shutdown
                print(f"Runner shutdown error: {e}")
            finally:
                cls._runner = None
                cls._agent = None
