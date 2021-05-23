from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import bcrypt

from .. import schemas, crud
from ..auth import login_manager
from ..database import get_db

router = APIRouter(tags=["Authentication"])

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
