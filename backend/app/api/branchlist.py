from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import login_manager, require_manager
from ..repository import branch_crud
from ..schemas import branch_list
from .dependencies import DatabaseSession, PageLimit, PageOffset, PositivePathId

router = APIRouter(
    prefix="/branchlist",
    tags=["BranchList"],
    dependencies=[Depends(login_manager)],
)


@router.get("/", response_model=list[branch_list.BranchList])
def read_branchlist(
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    branchlist_items = branch_crud.get_branchlists(db, skip=skip, limit=limit)
    return branchlist_items


@router.post(
    "/",
    response_model=branch_list.BranchList,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_manager)],
)
def create_branchlist(payload: branch_list.BranchListWrite, db: DatabaseSession):
    return branch_crud.create_branchlist(db, payload)


@router.put(
    "/{branch_id}",
    response_model=branch_list.BranchList,
    dependencies=[Depends(require_manager)],
)
def update_branchlist(
    branch_id: PositivePathId,
    payload: branch_list.BranchListWrite,
    db: DatabaseSession,
):
    record = branch_crud.get_branchlist_by_id(db, branch_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch_crud.update_branchlist(db, record, payload)


@router.delete(
    "/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_manager)],
)
def delete_branchlist(branch_id: PositivePathId, db: DatabaseSession) -> None:
    record = branch_crud.get_branchlist_by_id(db, branch_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    branch_crud.delete_branchlist(db, record)
