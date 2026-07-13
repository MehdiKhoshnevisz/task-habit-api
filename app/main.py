from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, tasks, habits

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(habits.router)
