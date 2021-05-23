from fastapi import APIRouter, Depends, HTTPException
# from app import crud, schemas, config
from .. import crud, schemas
from ..database import get_db
from ..auth import login_manager
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/workhour",
    tags=["workhour"],
)

@router.post("/", response_model=schemas.WorkhourFull)
def create_workhour(workhour: schemas.WorkhourCreate, db: Session = Depends(get_db), user=Depends(login_manager)):
    workhour.user_id = user.id
    return crud.create_workhour(db=db, workhour=workhour)

@router.get("/", response_model=List[schemas.WorkhourFull])
def read_workhours(skip: int = 0, limit: int = 100, user_id: int = None, task_id: int = None, db: Session = Depends(get_db)):
    if user_id and task_id:
        workhours = crud.get_workhours_by_user_task(db, skip=skip, limit=limit, user_id=user_id, task_id=task_id)
    elif user_id:
        workhours = crud.get_workhours_by_user_id(db, skip=skip, limit=limit, user_id=user_id)
    elif task_id:
        workhours = crud.get_workhours_by_task_id(db, skip=skip, limit=limit, task_id=task_id)
    else:
        workhours = crud.get_workhours(db, skip=skip, limit=limit)
    return workhours

@router.get('/my', response_model=List[schemas.WorkhourFull])
def read_workhours_my(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    workhours = crud.get_workhours_by_user_id(db, skip=skip, limit=limit, user_id=user_id)
    return workhours

@router.get("/{workhour_id}", response_model=schemas.WorkhourFull)
def read_workhour(workhour_id: int, db: Session = Depends(get_db)):
    db_workhour = crud.get_workhour(db, workhour_id=workhour_id)
    if db_workhour is None:
        raise HTTPException(status_code=404, detail="Workhour not found")
    return db_workhour

@router.put("/{workhour_id}", response_model=schemas.WorkhourFull)
def edit_workhour(workhour: schemas.WorkhourUpdate, workhour_id: int, db: Session = Depends(get_db), user=Depends(login_manager)):
    user_id = user.id
    db_workhour = crud.update_workhour(db, workhour_id=workhour_id, workhour=workhour, user_id=user_id)
    if db_workhour is None:
        raise HTTPException(status_code=404, detail="Workhour not found")
    return db_workhour

# @router.get("/totalhours", response_model=List[schemas.WorkhourFull])
# def read_totalworkhours(skip: int=0, db: Session = Depends(get_db)):
#     totalworkhours = crud.get_totalworkhours_by_user_id(db, skip=skip)
#     list_totalhours = [int(number) for number in totalworkhours]
#     return list_totalhours
