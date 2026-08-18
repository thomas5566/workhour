from fastapi import APIRouter, HTTPException, status

from ..auth import CurrentUser, ManagerUser, ensure_owner_or_manager
from ..repository import workhour_crud
from ..schemas import allfull, workhours
from ..schemas.common import MessageResponse
from .dependencies import DatabaseSession, PageLimit, PageOffset, PositivePathId

router = APIRouter(
    prefix="/workhour",
    tags=["Workhour"],
)


@router.post(
    "/",
    response_model=allfull.WorkhourFull,
)
def create_workhour(
    workhour_items: workhours.WorkhourCreate,
    db: DatabaseSession,
    user: CurrentUser,
):
    return workhour_crud.create_workhour(
        db=db,
        workhour_items=workhour_items,
        user_id=user.id,
    )


@router.get("/workhours", response_model=list[allfull.WorkhourFull])
def read_workhours(
    db: DatabaseSession,
    user: CurrentUser,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    # Defaults preserve the repository's legacy page while enabling navigation.
    return workhour_crud.get_workhours(
        db,
        user.id,
        skip=skip,
        limit=limit,
    )


@router.get("/allworkhours", response_model=list[allfull.WorkhourFull])
def read_all_workhours(
    db: DatabaseSession,
    manager: ManagerUser,
    skip: PageOffset = 0,
    limit: PageLimit = 1000,
):
    return workhour_crud.get_all_workhours(db, skip=skip, limit=limit)


@router.get("/worklist-year-month", response_model=list[workhours.WorkhourByYearMonth])
def read_workhours_by_year_month(
    db: DatabaseSession,
    manager: ManagerUser,
):
    return workhour_crud.get_worklist_by_yearmonth(db)


@router.get("/worklist-userid", response_model=list[workhours.WorkhourByUserId])
def read_workhours_by_user_id_summary(
    db: DatabaseSession,
    manager: ManagerUser,
):
    return workhour_crud.get_worklist_by_userid(db)


@router.get("/worklist-shopid", response_model=list[workhours.WorkhourByShopId])
def read_workhours_by_shop_id_summary(
    db: DatabaseSession,
    manager: ManagerUser,
):
    return workhour_crud.get_worklist_by_shopid(db)


@router.get("/my/{user_id}", response_model=list[allfull.WorkhourFull])
def read_workhours_my(
    user_id: PositivePathId,
    db: DatabaseSession,
    manager: ManagerUser,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    return workhour_crud.get_workhours_by_user_id(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
    )


@router.get("/totalhour/{user_id}", response_model=list[workhours.WorkhourTotal])
def get_totalworkhours_byid(
    user_id: PositivePathId,
    db: DatabaseSession,
    manager: ManagerUser,
):
    return workhour_crud.get_monthlyworkhours_by_user_id(
        db,
        user_id=user_id,
    )


@router.get("/{workhour_id}", response_model=allfull.WorkhourFull)
def read_workhour(
    workhour_id: PositivePathId,
    db: DatabaseSession,
    user: CurrentUser,
):
    db_workhour = workhour_crud.get_workhour(db, workhour_id=workhour_id)
    if db_workhour is None:
        raise HTTPException(status_code=404, detail="Workhour not found")
    ensure_owner_or_manager(user, db_workhour.user_id)
    return db_workhour


@router.put("/{workhour_id}", response_model=MessageResponse)
def edit_workhour(
    workhour_id: PositivePathId,
    workhour_items: workhours.WorkhourUpdate,
    db: DatabaseSession,
    user: CurrentUser,
) -> MessageResponse:
    workhour_retrieved = workhour_crud.get_workhour(
        db=db,
        workhour_id=workhour_id,
    )
    if not workhour_retrieved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workhour with id {workhour_id} does not exist",
        )
    ensure_owner_or_manager(user, workhour_retrieved.user_id)
    workhour_crud.update_workhour(
        workhour_id=workhour_id,
        workhour_items=workhour_items,
        db=db,
        user_id=workhour_retrieved.user_id,
    )
    return MessageResponse(detail="Successfully updated data.")


@router.delete("/{workhour_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workhour(
    workhour_id: PositivePathId,
    db: DatabaseSession,
    user: CurrentUser,
) -> None:
    workhour = workhour_crud.get_workhour(db, workhour_id)
    if workhour is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workhour not found",
        )
    ensure_owner_or_manager(user, workhour.user_id)
    workhour_crud.delete_workhour(workhour_id, db)
