import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..auth import ManagerUser, require_manager
from ..core.credentials import decrypt_credential
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
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[ipcamlist.IpCamList])
def read_ipcamlist(
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    ipcamlist_items = ipcamlist_crud.get_ipcamlists(db, skip=skip, limit=limit)
    return ipcamlist_items


@router.post("/", response_model=ipcamlist.IpCamList, status_code=status.HTTP_201_CREATED)
def create_ipcamlist(
    items: ipcamlist.IpCamListCreate,
    db: DatabaseSession,
) -> ipcamlist.IpCamList:
    return ipcamlist_crud.create_ipcamlist(db, items)


@router.post(
    "/{ipcamlist_id}/reveal-passwords",
    response_model=ipcamlist.IpCamCredentialReveal,
)
def reveal_ipcam_passwords(
    ipcamlist_id: PositivePathId,
    db: DatabaseSession,
    manager: ManagerUser,
    response: Response,
) -> ipcamlist.IpCamCredentialReveal:
    record = ipcamlist_crud.get_ipcamlist_by_id(db, ipcamlist_id)
    if record is None:
        raise HTTPException(status_code=404, detail="IP camera not found")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    logger.info(
        "Manager user_id=%s revealed camera credentials record_id=%s",
        manager.id,
        ipcamlist_id,
    )
    return ipcamlist.IpCamCredentialReveal(
        admin_password=decrypt_credential(record.admin_pass),
        user_password=decrypt_credential(record.user_pass),
    )


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
