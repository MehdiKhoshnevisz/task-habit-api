from datetime import date, datetime
from pydantic import BaseModel


class TaskModel(BaseModel):
    title: str
    description: str | None = None
    priority: int = 1


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    priority: int
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class HabitModel(BaseModel):
    name: str


class HabitResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class CheckinResponse(BaseModel):
    message: str
    date: date


class HabitStatsResponse(BaseModel):
    current_streak: int
    longest_streak: int
    total_checkins: int


class UserModel(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
