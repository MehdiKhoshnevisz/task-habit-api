from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import fastapi_settings
from app.database import Base, engine
from app.routers import auth, habits, root, tasks


# Runs once when the app starts (before requests) and optionally on shutdown (after yield).
# Used here to create database tables instead of doing it at import time.
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=fastapi_settings.title,
    description=fastapi_settings.description,
    version=fastapi_settings.version,
    lifespan=lifespan,
)

app.include_router(root.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(habits.router)
