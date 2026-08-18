from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import require_manager
from ..repository import fetnetlist_crud
from ..schemas import fetnetlist
from ..schemas.common import MessageResponse
from .dependencies import (
    DatabaseSession,
    PageLimit,
    PageOffset,
    PositivePathId,
    PositiveQueryId,
)

# Telecom inventory includes account and circuit details and is manager-only.
router = APIRouter(
    prefix="/fetnetlist",
    tags=["FetnetList"],
    dependencies=[Depends(require_manager)],
)


@router.get("/", response_model=list[fetnetlist.FetnetList])
def read_fetnetlist(
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    fetnetlist_items = fetnetlist_crud.get_fetnetlists(db, skip=skip, limit=limit)
    return fetnetlist_items


@router.get(
    "/fetnetlist-branchid",
    response_model=list[fetnetlist.FetnetList],
)
def read_fetnetlist_by_id(
    branch_id: PositiveQueryId,
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    return fetnetlist_crud.get_fetnetlists_by_branch_id(
        db, branch_id, skip=skip, limit=limit
    )


@router.put("/{fetnetlist_id}", response_model=MessageResponse)
def edit_fetnetlist(
    fetnetlist_id: PositivePathId,
    fetnetlist_items: fetnetlist.FetnetListUpdate,
    db: DatabaseSession,
) -> MessageResponse:
    fetnetlist_retrieved = fetnetlist_crud.get_fetnetlist_by_id(
        db=db,
        fetnetlist_id=fetnetlist_id,
    )
    if not fetnetlist_retrieved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fetnet item with id {fetnetlist_id} does not exist",
        )

    fetnetlist_crud.update_fetnetlist_by_id(
        fetnetlist_id=fetnetlist_id,
        fetnetlist_items=fetnetlist_items,
        db=db,
    )
    return MessageResponse(detail="Successfully updated data.")
