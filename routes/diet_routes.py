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

from fastapi import APIRouter
from typing import List
from agents import diet_agent

router = APIRouter()

@router.post("/diet", response_model=diet_agent.DietResponse)
async def diet_endpoint(payload: diet_agent.DietInput) -> diet_agent.DietResponse:
    """
    FastAPI route for diet agent.
    Accepts items + diet type, returns compatible items and recipe ideas.
    """
    return await diet_agent.run_diet(payload.items, payload.diet)
