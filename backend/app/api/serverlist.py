from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas import serverlist
from ..database import get_db
from ..repository import serverlist_crud

router = APIRouter(
    prefix="/serverlist",
    tags=["ServerList"],
)


@router.get("/", response_model=List[serverlist.ServerList])
def read_serverlist(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    serverlist_items = serverlist_crud.get_serverlists(db, skip=skip)
    return serverlist_items


@router.get("/serverlist-branchid", response_model=List[serverlist.ServerListByBranchId])
def read_serverlist_by_id(branch_id: int = None, db: Session = Depends(get_db)):
    db_get_serverlist_by_branch_id = serverlist_crud.get_serverlists_by_branch_id(db, branch_id)
    
    if db_get_serverlist_by_branch_id is None:
        raise HTTPException(status_code=404, detail="Get server list by branch id is not found")
    return db_get_serverlist_by_branch_id

