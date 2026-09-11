import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..auth import ITUser, require_it_user
from ..core.credentials import decrypt_credential
from ..repository import branch_crud, serverlist_crud
from ..schemas import serverlist
from ..schemas.common import MessageResponse
from .dependencies import (
    DatabaseSession,
    PageLimit,
    PageOffset,
    PositivePathId,
    PositiveQueryId,
)

# Server inventory and explicit secret reveal are available to IT users and
# system administrators.
router = APIRouter(
    prefix="/serverlist",
    tags=["ServerList"],
    dependencies=[Depends(require_it_user)],
)
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[serverlist.ServerList])
def read_serverlist(
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    serverlist_items = serverlist_crud.get_serverlists(db, skip=skip, limit=limit)
    return serverlist_items


@router.post("/", response_model=serverlist.ServerList, status_code=status.HTTP_201_CREATED)
def create_serverlist(
    serverlist_items: serverlist.ServerListCreate,
    db: DatabaseSession,
) -> serverlist.ServerList:
    # Reject stale or forged branch IDs before creating inventory records.
    if branch_crud.get_branchlist_by_id(db, serverlist_items.branch_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Selected branch does not exist",
        )
    return serverlist_crud.create_serverlist(db, serverlist_items)


@router.delete("/{serverlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_serverlist(
    serverlist_id: PositivePathId,
    db: DatabaseSession,
) -> None:
    if not serverlist_crud.delete_serverlist_by_id(db, serverlist_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server device not found",
        )


@router.post(
    "/{serverlist_id}/reveal-password",
    response_model=serverlist.ServerCredentialReveal,
)
def reveal_server_password(
    serverlist_id: PositivePathId,
    db: DatabaseSession,
    operator: ITUser,
    response: Response,
) -> serverlist.ServerCredentialReveal:
    record = serverlist_crud.get_serverlist_by_id(db, serverlist_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Server device not found")
    # Explicit reveal responses must not be retained by browsers or proxies.
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    logger.info(
        "IT operator user_id=%s revealed server credential record_id=%s",
        operator.id,
        serverlist_id,
    )
    return serverlist.ServerCredentialReveal(
        password=decrypt_credential(record.server_pass)
    )


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
    if (
        serverlist_items.branch_id is not None
        and branch_crud.get_branchlist_by_id(db, serverlist_items.branch_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Selected branch does not exist",
        )
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
