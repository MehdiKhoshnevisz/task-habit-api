from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas import Token, UserModel, UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


## Get current user
@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_current_user(user: User = Depends(get_current_user)):
    return user


## User registration
@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register(user: UserModel, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if db_user is None:
        db_user = User(
            username=user.username, hashed_password=hash_password(user.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        raise HTTPException(status_code=400, detail="Username already registered")


## Login
@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == form_data.username).first()

    if db_user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    else:
        if verify_password(form_data.password, db_user.hashed_password):
            access_token = create_access_token(data={"sub": db_user.username})
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=401, detail="Incorrect username or password"
            )
