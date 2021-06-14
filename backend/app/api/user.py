from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm

import bcrypt
# from fastapi_login.exceptions import InvalidCredentialsException
# from app import crud, schemas, config
from .. import schemas, models
from ..database import get_db
from ..auth import login_manager
from ..repository import user_crud
from .route_login import get_current_user_from_token


router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    pwhash = bcrypt.hashpw(bytes(user.password, 'utf-8'), bcrypt.gensalt())
    user.password = pwhash.decode('utf8')
    return user_crud.create_user(db=db, user=user)

# @router.get("/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = user_crud.get_users(db, skip=skip, limit=limit)
#     return users

@router.get("/users", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db),
               current_user: models.User = Depends(get_current_user_from_token)):
    # print(current_user.is_superuser)
    if current_user.is_superuser:
        users = user_crud.get_users(db)
        return users
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                        detail="You are not permitted!!")

@router.get('/my', response_model=schemas.UserFull)
def read_user_my(user=Depends(login_manager)):
    return user

@router.post('/login', response_model=schemas.UserToken)
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = data.username
    password = data.password
    user = user_crud.get_user_by_username(db, username=username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Username not found")
    elif not bcrypt.checkpw(bytes(data.password, 'utf-8'), bytes(user.password, 'utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = login_manager.create_access_token(
        data={'sub': user.id},
        expires=timedelta(hours=24)
    )
    user.token = access_token
    user.expiration = datetime.now() + timedelta(hours=24)
    return user

@router.get("/{user_id}", response_model=schemas.UserFull)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
