from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas import ipcamlist
from ..database import get_db
from ..repository import ipcamlist_crud

router = APIRouter(
    prefix="/ipcamlist",
    tags=["IpCamList"],
)


@router.get("/", response_model=List[ipcamlist.IpCamList])
def read_ipcamlist(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ipcamlist_items = ipcamlist_crud.get_ipcamlists(db, skip=skip)
    return ipcamlist_items


@router.put("/{ipcamlist_id}")
def edit_ipcamlist(ipcamlist_id: int, ipcamlist_items: ipcamlist.IpCamListUpdate, db: Session = Depends(get_db)):    
    ipcamlist_retrieved = ipcamlist_crud.get_ipcamlist_by_id(
        db=db, ipcamlist_id=ipcamlist_id)
    if not ipcamlist_retrieved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"ipcam with id {id} does not exist")
    
    else: ipcamlist_crud.update_ipcamlist_by_id(
            ipcamlist_id=ipcamlist_id, ipcamlist_items=ipcamlist_items, db=db)
        
    return {"detail": "Successfully updated data."}
