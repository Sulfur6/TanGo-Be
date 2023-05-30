import uvicorn
from fastapi import FastAPI

from api import api_router
from db.database import init_db_pool
from db.redis import init_redis_pool

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

app.include_router(router=api_router, prefix='/api')


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.on_event("startup")
async def startup_event():
    app.state.database = await init_db_pool()
    app.state.redis = await init_redis_pool()


@app.on_event("shutdown")
async def shutdown() -> None:
    await app.state.database.disconnect()
    await app.state.redis.close()


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
