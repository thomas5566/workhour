from fastapi import APIRouter, HTTPException, status

from ..auth import CurrentUser, ManagerUser, is_manager
from ..repository import expentask_crud
from ..schemas import allfull, expentasks
from .dependencies import DatabaseSession, PageLimit, PageOffset, PositivePathId

router = APIRouter(
    prefix="/expentask",
    tags=["Expentask"],
)


@router.post(
    "/",
    response_model=expentasks.ExpenTask,
)
def create_expentask(
    expentask_item: expentasks.ExpenTaskCreate,
    db: DatabaseSession,
    manager: ManagerUser,
):
    existing_item = expentask_crud.get_expentask_by_expentaskname(
        db,
        expentask_item.expentask_name,
    )
    if existing_item is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Expense task name already registered",
        )
    return expentask_crud.create_expentask(db=db, expentask_item=expentask_item)


@router.get("/", response_model=list[expentasks.ExpenTask])
def read_expentasks(
    db: DatabaseSession,
    user: CurrentUser,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    return expentask_crud.get_expentasks(db, skip=skip, limit=limit)


@router.get("/{expentask_id}", response_model=allfull.ExpenTaskFull)
def read_expentask(
    expentask_id: PositivePathId,
    db: DatabaseSession,
    user: CurrentUser,
):
    db_expentask = expentask_crud.get_expentask(db, expentask_id=expentask_id)
    if db_expentask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense task not found",
        )
    if not is_manager(user):
        response = allfull.ExpenTaskFull.model_validate(db_expentask)
        response.expenditures = [item for item in response.expenditures if item.user_id == user.id]
        return response
    return db_expentask


@router.put("/{expentask_id}", response_model=allfull.ExpenTaskFull)
def edit_expentask(
    expentask_items: expentasks.ExpenTaskUpdate,
    expentask_id: PositivePathId,
    db: DatabaseSession,
    manager: ManagerUser,
):
    db_expentask = expentask_crud.update_expentask(
        db,
        expentask_id=expentask_id,
        expentask_items=expentask_items,
    )
    if db_expentask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense task not found",
        )
    return db_expentask
