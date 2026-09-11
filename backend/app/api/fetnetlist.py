from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import login_manager
from ..repository import branch_crud, fetnetlist_crud
from ..schemas import fetnetlist
from ..schemas.common import MessageResponse
from .dependencies import (
    DatabaseSession,
    PageLimit,
    PageOffset,
    PositivePathId,
    PositiveQueryId,
)

# Authenticated users may maintain telecom inventory.
router = APIRouter(
    prefix="/fetnetlist",
    tags=["FetnetList"],
    dependencies=[Depends(login_manager)],
)


@router.get("/", response_model=list[fetnetlist.FetnetList])
def read_fetnetlist(
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    fetnetlist_items = fetnetlist_crud.get_fetnetlists(db, skip=skip, limit=limit)
    return fetnetlist_items


@router.post("/", response_model=fetnetlist.FetnetList, status_code=status.HTTP_201_CREATED)
def create_fetnetlist(
    items: fetnetlist.FetnetListCreate,
    db: DatabaseSession,
) -> fetnetlist.FetnetList:
    if (
        items.branch_id is not None
        and branch_crud.get_branchlist_by_id(db, items.branch_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Selected branch does not exist",
        )
    return fetnetlist_crud.create_fetnetlist(db, items)


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
    if (
        fetnetlist_items.branch_id is not None
        and branch_crud.get_branchlist_by_id(db, fetnetlist_items.branch_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Selected branch does not exist",
        )
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


@router.delete("/{fetnetlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fetnetlist(
    fetnetlist_id: PositivePathId,
    db: DatabaseSession,
) -> None:
    if not fetnetlist_crud.delete_fetnetlist_by_id(db, fetnetlist_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fetnet item not found",
        )
