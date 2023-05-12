from fastapi import APIRouter

from api.cloud_info import cloud_info_router
from api.scheduling import scheduling_router
from api.test_api import base_router

api_router = APIRouter()
api_router.include_router(base_router)
api_router.include_router(cloud_info_router, prefix="/cloud_info")
api_router.include_router(scheduling_router, prefix="/scheduling")
