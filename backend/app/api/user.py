from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm

import bcrypt
# from fastapi_login.exceptions import InvalidCredentialsException
# from app import crud, schemas, config
# from .. import schemas
from ..schemas import users, allfull
from ..database import get_db
from ..auth import login_manager
from ..repository import user_crud
# from .route_login import get_current_user_from_token


router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router.post("/", response_model=users.User)
def create_user(user_item: users.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_username(db, username=user_item.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    pwhash = bcrypt.hashpw(bytes(user_item.password, 'utf-8'), bcrypt.gensalt())
    user_item.password = pwhash.decode('utf8')
    return user_crud.create_user(db=db, user_item=user_item)

@router.get("/", response_model=List[users.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/alldata", response_model=List[users.DataTotal])
def read_users(db: Session = Depends(get_db)):
    countall = user_crud.get_allusers_monthly(db)
    return countall


@router.get("/get-dpuser", response_model=List[users.User])
def get_user_bydp(db: Session = Depends(get_db), user=Depends(login_manager)):
    user_dp = user.department_id
    list_dp_p = user.checklistAll_permission
    print("department_id:", user_dp)
    print("permission:", list_dp_p)
    # print(current_user.is_superuser)
    if list_dp_p == 1:
        users = user_crud.get_user_by_department(db, user_dp)
        return users
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                        detail="You are not permitted!!")

@router.get('/my', response_model=allfull.UserFull)
def read_user_my(user=Depends(login_manager)):
    return user

@router.post('/login', response_model=users.UserToken)
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

@router.get("/{user_id}", response_model=allfull.UserFull)
def read_user(user_id: int, db: Session = Depends(get_db), user=Depends(login_manager)):
    list_dp_p = user.checklistAll_permission
    if list_dp_p == 1:
        db_user = user_crud.get_user(db, user_id=user_id)
        return db_user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="You are not permitted!!")
    # if db_user is None:
    #     raise HTTPException(status_code=404, detail="User not found")
    # return db_user
