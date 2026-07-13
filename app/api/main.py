from fastapi import APIRouter

from app.api import auth, habits, root, tasks

api_router = APIRouter()
api_router.include_router(root.router)
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(habits.router)
