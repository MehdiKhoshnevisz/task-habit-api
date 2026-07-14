from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Habit, HabitLog, User
from app.schemas import CheckinResponse, HabitModel, HabitResponse, HabitStatsResponse

router = APIRouter(
    prefix="/habits",
    tags=["habits"],
    # dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


## Get Habits
@router.get("", response_model=list[HabitResponse])
async def get_habits(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.query(Habit).filter(Habit.owner_id == current_user.id).all()


## Create a Habit
@router.post("", status_code=status.HTTP_201_CREATED, response_model=HabitResponse)
async def create_habit(
    habit: HabitModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_habit = Habit(name=habit.name, owner_id=current_user.id)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)

    return db_habit


## Update a Habit
@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=HabitResponse)
async def update_habit(
    id: int,
    habit: HabitModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_habit = db.query(Habit).filter(Habit.id == id).first()

    if db_habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    if db_habit.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this habit"
        )

    db_habit.name = habit.name
    db.commit()
    db.refresh(db_habit)

    return db_habit


## Delete a Habit
@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=HabitResponse)
async def delete_habit(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_habit = db.query(Habit).filter(Habit.id == id).first()

    if db_habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    if db_habit.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this habit"
        )

    db.query(HabitLog).filter(HabitLog.habit_id == id).delete()
    db.delete(db_habit)
    db.commit()

    return db_habit


## Checking a Habit
@router.post(
    "/{id}/checkin",
    status_code=status.HTTP_200_OK,
    response_model=CheckinResponse,
)
async def checkin_habit(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_habit = db.query(Habit).filter(Habit.id == id).first()

    if db_habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    if db_habit.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this habit"
        )

    today = date.today()
    existing_log = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == id, HabitLog.date == today)
        .first()
    )

    if existing_log:
        raise HTTPException(status_code=400, detail="Habit already checked in today")
    else:
        new_log = HabitLog(habit_id=id, date=today)
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        return {"message": "Habit checked in successfully", "date": today}


## streak calculation
@router.get("/{habit_id}/stats", response_model=HabitStatsResponse)
async def get_stats(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_habit = db.query(Habit).filter(Habit.id == habit_id).first()

    if db_habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    if db_habit.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this habit"
        )

    # calculate current streak
    log_dates = {log.date for log in db_habit.logs}
    today = date.today()
    current_streak = 0
    check_date = today if today in log_dates else today - timedelta(days=1)
    while check_date in log_dates:
        current_streak += 1
        check_date = check_date - timedelta(days=1)

    # calculate longest streak
    sorted_dates = sorted(log_dates)
    longest_streak = 0
    current_run = 0
    previous_date = None
    for d in sorted_dates:
        if previous_date is not None and d == previous_date + timedelta(days=1):
            current_run += 1
        else:
            current_run = 1
        longest_streak = max(longest_streak, current_run)
        previous_date = d

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_checkins": len(log_dates),
    }
