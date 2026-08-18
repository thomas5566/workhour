from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import require_manager
from ..repository import ipcamlist_crud
from ..schemas import ipcamlist
from ..schemas.common import MessageResponse
from .dependencies import DatabaseSession, PageLimit, PageOffset, PositivePathId

# Camera inventory exposes network locations and credentials and is manager-only.
router = APIRouter(
    prefix="/ipcamlist",
    tags=["IpCamList"],
    dependencies=[Depends(require_manager)],
)


@router.get("/", response_model=list[ipcamlist.IpCamList])
def read_ipcamlist(
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    ipcamlist_items = ipcamlist_crud.get_ipcamlists(db, skip=skip, limit=limit)
    return ipcamlist_items


@router.put("/{ipcamlist_id}", response_model=MessageResponse)
def edit_ipcamlist(
    ipcamlist_id: PositivePathId,
    ipcamlist_items: ipcamlist.IpCamListUpdate,
    db: DatabaseSession,
) -> MessageResponse:
    ipcamlist_retrieved = ipcamlist_crud.get_ipcamlist_by_id(
        db=db,
        ipcamlist_id=ipcamlist_id,
    )
    if not ipcamlist_retrieved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP camera with id {ipcamlist_id} does not exist",
        )

    ipcamlist_crud.update_ipcamlist_by_id(
        ipcamlist_id=ipcamlist_id,
        ipcamlist_items=ipcamlist_items,
        db=db,
    )
    return MessageResponse(detail="Successfully updated data.")
