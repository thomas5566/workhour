from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import require_manager
from ..repository import serverlist_crud
from ..schemas import serverlist
from ..schemas.common import MessageResponse
from .dependencies import (
    DatabaseSession,
    PageLimit,
    PageOffset,
    PositivePathId,
    PositiveQueryId,
)

# Server inventory responses include credentials, so every route requires a
# manager even when the caller only reads data.
router = APIRouter(
    prefix="/serverlist",
    tags=["ServerList"],
    dependencies=[Depends(require_manager)],
)


@router.get("/", response_model=list[serverlist.ServerList])
def read_serverlist(
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    serverlist_items = serverlist_crud.get_serverlists(db, skip=skip, limit=limit)
    return serverlist_items


@router.get(
    "/serverlist-branchid",
    response_model=list[serverlist.ServerList],
)
def read_serverlist_by_id(
    branch_id: PositiveQueryId,
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    return serverlist_crud.get_serverlists_by_branch_id(
        db, branch_id, skip=skip, limit=limit
    )


@router.put("/{serverlist_id}", response_model=MessageResponse)
def edit_serverlist(
    serverlist_id: PositivePathId,
    serverlist_items: serverlist.ServerListUpdate,
    db: DatabaseSession,
) -> MessageResponse:
    serverlist_retrieved = serverlist_crud.get_serverlist_by_id(
        db=db,
        serverlist_id=serverlist_id,
    )
    if not serverlist_retrieved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server-list with id {serverlist_id} does not exist",
        )

    serverlist_crud.update_serverlist_by_id(
        serverlist_id=serverlist_id,
        serverlist_items=serverlist_items,
        db=db,
    )
    return MessageResponse(detail="Successfully updated data.")
