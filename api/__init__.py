"""
This module sets up the main API router for the application.
It includes all versioned API routes, starting with version 1 (`/api/v1`).
"""

from fastapi import APIRouter
from api.v1 import router as v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)
