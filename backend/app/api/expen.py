from fastapi import APIRouter, HTTPException, status

from ..auth import CurrentUser, ensure_owner_or_manager
from ..repository import expen_crud
from ..schemas import allfull, expens
from .dependencies import DatabaseSession, PageLimit, PageOffset, PositivePathId

router = APIRouter(
    prefix="/expen",
    tags=["Expenses"],
)


@router.post(
    "/",
    response_model=allfull.ExpenditureFull,
)
def create_expenditure(
    expenditure: expens.ExpenditureCreate,
    db: DatabaseSession,
    user: CurrentUser,
):
    return expen_crud.create_expen(
        db=db,
        expen_item=expenditure,
        user_id=user.id,
    )


@router.get("/expens", response_model=list[allfull.ExpenditureFull])
def read_my_expenditures(
    db: DatabaseSession,
    user: CurrentUser,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    return expen_crud.get_expens(
        db,
        user_id=user.id,
        skip=skip,
        limit=limit,
    )


@router.get("/my/{user_id}", response_model=list[allfull.ExpenditureFull])
def read_expenditures_by_user(
    user_id: PositivePathId,
    db: DatabaseSession,
    user: CurrentUser,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    ensure_owner_or_manager(user, user_id)
    return expen_crud.get_expens_by_user_id(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
    )


@router.get("/totalexpen/{user_id}", response_model=list[expens.ExpenTotal])
def get_monthly_expenditure_totals(
    user_id: PositivePathId,
    db: DatabaseSession,
    user: CurrentUser,
):
    ensure_owner_or_manager(user, user_id)
    return expen_crud.get_monthlyexpens_by_user_id(db, user_id=user_id)


@router.get("/{expen_id}", response_model=allfull.ExpenditureFull)
def read_expenditure(
    expen_id: PositivePathId,
    db: DatabaseSession,
    user: CurrentUser,
):
    expenditure = expen_crud.get_expen(db, expen_id=expen_id)
    if expenditure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expenditure not found",
        )
    ensure_owner_or_manager(user, expenditure.user_id)
    return expenditure


@router.put("/{expen_id}", response_model=allfull.ExpenditureFull)
def update_expenditure(
    expen_id: PositivePathId,
    expenditure_update: expens.ExpenditureUpdate,
    db: DatabaseSession,
    user: CurrentUser,
):
    expenditure = expen_crud.get_expen(db, expen_id)
    if expenditure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expenditure not found",
        )
    ensure_owner_or_manager(user, expenditure.user_id)
    return expen_crud.update_expen(
        expen_id,
        expenditure_update,
        db,
        user_id=expenditure.user_id,
    )


@router.delete("/{expen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expenditure(
    expen_id: PositivePathId,
    db: DatabaseSession,
    user: CurrentUser,
) -> None:
    expenditure = expen_crud.get_expen(db, expen_id)
    if expenditure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expenditure not found",
        )
    ensure_owner_or_manager(user, expenditure.user_id)
    expen_crud.delete_expen(expen_id, db)
