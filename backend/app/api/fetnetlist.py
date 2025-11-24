from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas import fetnetlist
from ..database import get_db
from ..repository import fetnetlist_crud

router = APIRouter(
    prefix="/fetnetlist",
    tags=["FetnetList"],
)


@router.get("/", response_model=List[fetnetlist.FetnetList])
def read_fetnetlist(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    fetnetlist_items = fetnetlist_crud.get_fetnetlists(db, skip=skip)
    return fetnetlist_items


@router.get("/fetnetlist-branchid", response_model=List[fetnetlist.FetnetListByBranchId])
def read_fetnetlist_by_id(branch_id: int = None, db: Session = Depends(get_db)):
    db_get_fetnetlist_by_branch_id = fetnetlist_crud.get_fetnetlists_by_branch_id(db, branch_id)
    
    if db_get_fetnetlist_by_branch_id is None:
        raise HTTPException(status_code=404, detail="Get server list by branch id is not found")
    return db_get_fetnetlist_by_branch_id


@router.put("/{fetnetlist_id}")
def edit_fetnetlist(fetnetlist_id: int, fetnetlist_items: fetnetlist.FetnetListUpdate, db: Session = Depends(get_db)):    
    fetnetlist_retrieved = fetnetlist_crud.get_fetnetlist_by_id(
        db=db, fetnetlist_id=fetnetlist_id)
    if not fetnetlist_retrieved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"fetnet with id {id} does not exist")
    
    else: fetnetlist_crud.update_fetnetlist_by_id(
            fetnetlist_id=fetnetlist_id, fetnetlist_items=fetnetlist_items, db=db)
        
    return {"detail": "Successfully updated data."}
