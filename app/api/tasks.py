from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import Task, User
from app.schemas import TaskModel, TaskPatchModel, TaskResponse

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    # dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


## Get Tasks
@router.get("", response_model=list[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.query(Task).filter(Task.owner_id == current_user.id).all()

## Search on Tasks
@router.get("/search", response_model=list[TaskResponse])
async def search(
    title: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Task)
        .filter(
            Task.owner_id == current_user.id,
            Task.title.like(f"%{title}%"),
        )
        .all()
    )


## Get a Task
@router.get("/{id}", response_model=TaskResponse)
async def get_task(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = db.query(Task).filter(Task.id == id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this task"
        )

    return db_task


## Create a Task
@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    task: TaskModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = Task(**task.model_dump(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


## Update a Task
@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
async def update_task(
    id: int,
    task: TaskModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = db.query(Task).filter(Task.id == id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this task"
        )

    db_task.title = task.title
    db_task.description = task.description
    db_task.priority = task.priority
    db.commit()
    db.refresh(db_task)

    return db_task

## Partially update a Task
@router.patch("/{id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
async def patch_task(
    id: int,
    task: TaskPatchModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = db.query(Task).filter(Task.id == id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this task"
        )

    for field, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)

    return db_task


## Delete a Task
@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
async def delete_task(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = db.query(Task).filter(Task.id == id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this task"
        )

    db.delete(db_task)
    db.commit()

    return db_task


