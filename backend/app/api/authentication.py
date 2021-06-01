from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, database, models, jwttoken
from ..hashing import Hash
from ..repository import user_crud
from ..auth import login_manager
import bcrypt
from datetime import datetime, timedelta
from ..database import get_db

router = APIRouter(tags=["Authentication"])


# @router.post('/login', response_model=schemas.Token)
# def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
#     user = db.query(models.User).filter(
#         models.User.username == request.username).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Invalid Credentials')
#     if not Hash.verify(user.password, request.password):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Invalid Password')

#     access_token = jwttoken.create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}

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