from fastapi import APIRouter

from api.scheduling.view import base_router

scheduling_router = APIRouter()
scheduling_router.include_router(base_router)
