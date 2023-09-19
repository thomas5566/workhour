from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas import cstshop
from ..database import get_db
from ..repository import cstshop_crud
from ..auth import login_manager

router = APIRouter(
    prefix="/cstshop",
    tags=["CstShop"],
)


@router.get("/", response_model=List[cstshop.CstShpo])
def read_cstshop(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cstshop_items = cstshop_crud.get_cstshops(db, skip=skip, limit=limit)
    return cstshop_items

