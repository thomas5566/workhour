from fastapi import APIRouter, Depends, HTTPException, status, Response
# from starlette.status import HTTP_404_NOT_FOUND
from sqlalchemy.orm import Session, session
from typing import List
# from app import crud, schemas, config
from .. import schemas, models, oauth2
from ..database import get_db
from ..auth import login_manager
from ..repository import expen_crud


router = APIRouter(
    prefix="/expen",
    tags=["Expens"],
)


@router.post("/", response_model=schemas.ExpenditureFull)
def create_expen(expen: schemas.ExpenditureCreate, db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(oauth2.get_current_user)):
    # expen.user_id = user.id
    return expen_crud.create_expen(db=db, expen=expen)


@router.get('/', response_model=List[schemas.ExpenditureFull])
def all(db: Session = Depends(get_db),
        current_user: schemas.User = Depends(oauth2.get_current_user)):
    return expen_crud.get_expens(db)
# @router.get("/", response_model=List[schemas.ExpenditureFull])
# def read_expens(skip: int = 0, limit: int = 100, user_id: int = None, expen_id: int = None, db: Session = Depends(get_db)):
#     if user_id and expen_id:
#         expens = expen_crud.get_expens_by_user_expentask(
#             db, skip=skip, limit=limit, user_id=user_id, expen_id=expen_id)
#     elif user_id:
#         expens = expen_crud.get_expens_by_user_id(
#             db, skip=skip, limit=limit, user_id=user_id)
#     elif expen_id:
#         expens = expen_crud.get_expens_by_expentask_id(
#             db, skip=skip, limit=limit, expen_id=expen_id)
#     else:
#         expens = expen_crud.get_expens(db, skip=skip, limit=limit)
#     return expens


@router.get("/{expen_id}", response_model=schemas.ExpenditureFull)
def read_expen(expen_id: int, db: Session = Depends(get_db),
            current_user: schemas.User = Depends(oauth2.get_current_user)):
    db_expen = expen_crud.get_expen(db, expen_id=expen_id)
    if db_expen is None:
        raise HTTPException(status_code=404, detail="Expen not found")
    return db_expen


@router.put("/{expen_id}", status_code=status.HTTP_202_ACCEPTED)
def update_expen(id: int, request: schemas.Expenditure,
                 db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(oauth2.get_current_user)):
    return expen_crud.update_expen(id, request, db)


@router.delete("/{id}", response_class=Response)
def delete_expen(id: int, db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(oauth2.get_current_user)):
    return expen_crud.delete_expen(id, db)