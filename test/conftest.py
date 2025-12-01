
import asyncio
import sys

#This replaces the default ProactorEventLoop with SelectorEventLoop, which avoids the “loop closed” error.
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())