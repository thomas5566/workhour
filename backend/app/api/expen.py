from fastapi import APIRouter, Depends, HTTPException
# from app import crud, schemas, config
from .. import crud, schemas
from ..database import get_db
from ..auth import login_manager
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/expen",
    tags=["expen"],
)

@router.post("/", response_model=schemas.ExpenditureFull)
def create_workhour(expen: schemas.ExpenditureCreate, db: Session = Depends(get_db), user=Depends(login_manager)):
    expen.user_id = user.id
    return crud.create_expen(db=db, expen=expen)

@router.get("/", response_model=List[schemas.ExpenditureFull])
def read_expens(skip: int = 0, limit: int = 100, user_id: int = None, expentask_id: int = None, db: Session = Depends(get_db)):
    if user_id and expentask_id:
        expens = crud.get_expens_by_user_expentask(db, skip=skip, limit=limit, user_id=user_id, expentask_id=expentask_id)
    elif user_id:
        expens = crud.get_expens_by_user_id(db, skip=skip, limit=limit, user_id=user_id)
    elif expentask_id:
        expens = crud.get_expens_by_expentask_id(db, skip=skip, limit=limit, expentask_id=expentask_id)
    else:
        expens = crud.get_expens(db, skip=skip, limit=limit)
    return expens

@router.get("/{expen_id}", response_model=schemas.ExpenditureFull)
def read_expen(expen_id: int, db: Session = Depends(get_db)):
    db_expen = crud.get_expen(db, workhour_id=expen_id)
    if db_expen is None:
        raise HTTPException(status_code=404, detail="Workhour not found")
    return db_expen

@router.put("/{expen_id}", response_model=schemas.ExpenditureFull)
def edit_expen(expen: schemas.ExpenditureUpdate, expen_id: int, db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    db_expen = crud.update_expen(db, expen_id=expen_id, expen=expen, user_id=user_id)
    if db_expen is None:
        raise HTTPException(status_code=404, detail="Workhour not found")
    return db_expen

@router.delete("/{expen_id}", response_model=schemas.Expenditure)
def delete_expen(expen: schemas.Expenditure, db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    db_user = crud.delete_expen(db, expen_id=expen.id, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Expen not deleted")
    return db_user

# @router.get("/totalhours", response_model=List[schemas.WorkhourFull])
# def read_totalworkhours(skip: int=0, db: Session = Depends(get_db)):
#     totalworkhours = crud.get_totalworkhours_by_user_id(db, skip=skip)
#     list_totalhours = [int(number) for number in totalworkhours]
#     return list_totalhours
