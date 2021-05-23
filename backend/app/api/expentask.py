from fastapi import APIRouter, Depends, HTTPException
# from app import crud, schemas, config
from .. import crud, schemas
from ..database import get_db
from ..auth import login_manager
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/expentask",
    tags=["expentask"],
)

@router.post("/", response_model=schemas.ExpenTask)
def create_expentask(expentask: schemas.ExpenTaskCreate, db: Session = Depends(get_db), user=Depends(login_manager)):
    expentask.user_id = user.id
    return crud.create_expentask(db=db, expentask=expentask)


@router.get("/", response_model=List[schemas.ExpenTask])
def read_expentasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expentasks = crud.get_expentasks(db, skip=skip, limit=limit)
    return expentasks

@router.get("/{expentask_id}", response_model=schemas.ExpenTaskFull)
def read_expentask(expentask_id: int, db: Session = Depends(get_db)):
    db_expentask = crud.get_expentask(db, expentask_id=expentask_id)
    if db_expentask is None:
        raise HTTPException(status_code=404, detail="Expentask not found")
    return db_expentask

@router.put("/{expentask_id}", response_model=schemas.ExpenTaskFull)
def edit_expentask(expentask: schemas.ExpenTaskUpdate, expentask_id: int, db: Session = Depends(get_db)):
    db_expentask = crud.update_expentask(db, expentask_id=expentask_id, expentask=expentask)
    if db_expentask is None:
        raise HTTPException(status_code=404, detail="ExpenTask not found")
    return db_expentask
