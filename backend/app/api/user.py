from fastapi import APIRouter, Depends, HTTPException
# from app import crud, schemas, config
from app import crud, schemas
from app.dependency import get_db
from app.auth import login_manager
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
import bcrypt
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    pwhash = bcrypt.hashpw(bytes(user.password, 'utf-8'), bcrypt.gensalt())
    user.password = pwhash.decode('utf8')
    return crud.create_user(db=db, user=user)

@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get('/my', response_model=schemas.UserFull)
def read_user_my(user=Depends(login_manager)):
    return user

@router.post('/login', response_model=schemas.UserToken)
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = data.username
    password = data.password
    user = crud.get_user_by_username(db, username=username)
    
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
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user