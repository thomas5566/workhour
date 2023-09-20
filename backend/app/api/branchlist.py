from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas import branch_list
from ..database import get_db
from ..repository import branch_crud

router = APIRouter(
    prefix="/branchlist",
    tags=["BranchList"],
)


@router.get("/", response_model=List[branch_list.BranchList])
def read_branchlist(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    branchlist_items = branch_crud.get_branchlists(db, skip=skip)
    return branchlist_items

