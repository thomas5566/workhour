from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth import login_manager, require_manager
from ..repository import cstshop_crud, task_crud
from ..schemas import cstshop
from .dependencies import DatabaseSession, PageLimit, PageOffset, PositivePathId

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
    main_department_id: Annotated[int | None, Query(gt=0)] = None,
):
    cstshop_items = cstshop_crud.get_cstshops(
        db,
        skip=skip,
        limit=limit,
        main_department_id=main_department_id,
    )
    return cstshop_items


def _validate_main_department(db: DatabaseSession, main_department_id: int) -> None:
    if task_crud.get_task(db, main_department_id) is None:
        raise HTTPException(status_code=422, detail="Main department does not exist")


@router.post(
    "/",
    response_model=cstshop.CstShop,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_manager)],
)
def create_cstshop(payload: cstshop.CstShopWrite, db: DatabaseSession):
    _validate_main_department(db, payload.main_department_id)
    return cstshop_crud.create_cstshop(db, payload)


@router.put(
    "/{shop_id}",
    response_model=cstshop.CstShop,
    dependencies=[Depends(require_manager)],
)
def update_cstshop(
    shop_id: PositivePathId,
    payload: cstshop.CstShopWrite,
    db: DatabaseSession,
):
    record = cstshop_crud.get_cstshop_by_id(db, shop_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    _validate_main_department(db, payload.main_department_id)
    return cstshop_crud.update_cstshop(db, record, payload)


@router.delete(
    "/{shop_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_manager)],
)
def delete_cstshop(shop_id: PositivePathId, db: DatabaseSession) -> None:
    record = cstshop_crud.get_cstshop_by_id(db, shop_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    cstshop_crud.delete_cstshop(db, record)
