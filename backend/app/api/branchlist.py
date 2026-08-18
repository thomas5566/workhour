from fastapi import APIRouter, Depends

from ..auth import login_manager
from ..repository import branch_crud
from ..schemas import branch_list
from .dependencies import DatabaseSession, PageLimit, PageOffset

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
