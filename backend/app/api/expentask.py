from fastapi import APIRouter, Depends, HTTPException
# from app import crud, schemas, config
# from .. import schemas

from ..schemas import expentasks, allfull
from ..database import get_db
from ..auth import login_manager
from ..repository import expentask_crud
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/expentask",
    tags=["Expentask"],
)

@router.post("/", response_model=expentasks.ExpenTask)
def create_expentask(expentask_item: expentasks.ExpenTaskCreate, db: Session = Depends(get_db)):
    # expentasks.user_id = user.id
    return expentask_crud.create_expentask(db=db, expentask_item=expentask_item)


@router.get("/", response_model=List[expentasks.ExpenTask])
def read_expentasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expentasks = expentask_crud.get_expentasks(db, skip=skip, limit=limit)
    return expentasks

@router.get("/{expentask_id}", response_model=allfull.ExpenTaskFull)
def read_expentask(expentask_id: int, db: Session = Depends(get_db)):
    db_expentask = expentask_crud.get_expentask(db, expentask_id=expentask_id)
    if db_expentask is None:
        raise HTTPException(status_code=404, detail="Expentask not found")
    return db_expentask

@router.put("/{expentask_id}", response_model=allfull.ExpenTaskFull)
def edit_expentask(expentask_items: expentasks.ExpenTaskUpdate, expentask_id: int, db: Session = Depends(get_db)):
    db_expentask = expentask_crud.update_expentask(db, expentask_id=expentask_id, expentask_items=expentask_items)
    if db_expentask is None:
        raise HTTPException(status_code=404, detail="ExpenTask not found")
    return db_expentask
