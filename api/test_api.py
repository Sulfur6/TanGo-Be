from fastapi import APIRouter

from db.database import database
from db.models import User

base_router = APIRouter()


@base_router.get("/test")
async def test():
    return {"message": "Hello test"}


@base_router.get("/users")
@database.transaction()
async def get_users():
    users = await User.objects.all()
    return users
