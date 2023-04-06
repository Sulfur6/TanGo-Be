from fastapi import APIRouter

from api.cloud_info.view import base_router

cloud_info_router = APIRouter()
cloud_info_router.include_router(base_router)
