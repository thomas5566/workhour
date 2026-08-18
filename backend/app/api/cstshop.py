from fastapi import APIRouter, Depends

from ..auth import login_manager
from ..repository import cstshop_crud
from ..schemas import cstshop
from .dependencies import DatabaseSession, PageLimit, PageOffset

router = APIRouter(
    prefix="/cstshop",
    tags=["CstShop"],
    dependencies=[Depends(login_manager)],
)


@router.get("/", response_model=list[cstshop.CstShop])
def read_cstshop(
    db: DatabaseSession,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    cstshop_items = cstshop_crud.get_cstshops(db, skip=skip, limit=limit)
    return cstshop_items
