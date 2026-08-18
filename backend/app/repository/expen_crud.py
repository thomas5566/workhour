from sqlalchemy import Integer, cast, extract, func, select
from sqlalchemy.orm import Session, selectinload

from ..models import Expenditure, User
from ..schemas import expens
from .transaction import commit_or_rollback

EXPENDITURE_RESPONSE_OPTIONS = (
    selectinload(Expenditure.user).selectinload(User.department),
    selectinload(Expenditure.expentask),
)


def get_expen(db: Session, expen_id: int) -> Expenditure | None:
    statement = (
        select(Expenditure)
        .options(*EXPENDITURE_RESPONSE_OPTIONS)
        .where(
            Expenditure.id == expen_id,
            Expenditure.active.is_(True),
        )
    )
    return db.scalar(statement)


def get_expens(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Expenditure]:
    return get_expens_by_user_id(db, user_id, skip, limit)


def get_expens_by_user_id(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Expenditure]:
    statement = (
        select(Expenditure)
        .options(*EXPENDITURE_RESPONSE_OPTIONS)
        .where(
            Expenditure.user_id == user_id,
            Expenditure.active.is_(True),
        )
        .order_by(Expenditure.date.desc(), Expenditure.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_monthlyexpens_by_user_id(db: Session, user_id: int) -> list[dict]:
    year = cast(extract("year", Expenditure.date), Integer).label("year")
    month = cast(extract("month", Expenditure.date), Integer).label("month")
    statement = (
        select(year, month, func.sum(Expenditure.price).label("total_pric"))
        .where(
            Expenditure.user_id == user_id,
            Expenditure.active.is_(True),
        )
        .group_by(year, month)
        .order_by(year.desc(), month.desc())
    )
    return [
        {
            "year_month": f"{row.year:04d}-{row.month:02d}",
            "total_pric": row.total_pric,
        }
        for row in db.execute(statement)
    ]


def create_expen(
    db: Session,
    expen_item: expens.ExpenditureCreate,
    user_id: int,
) -> Expenditure:
    db_expen = Expenditure(
        **expen_item.model_dump(),
        user_id=user_id,
    )
    db.add(db_expen)
    commit_or_rollback(db)
    db.refresh(db_expen)
    return db_expen


def delete_expen(expen_id: int, db: Session) -> bool:
    expen_item = get_expen(db, expen_id)
    if expen_item is None:
        return False
    db.delete(expen_item)
    commit_or_rollback(db)
    return True


def update_expen(
    expen_id: int,
    request: expens.ExpenditureUpdate,
    db: Session,
    user_id: int,
) -> Expenditure | None:
    expen_item = get_expen(db, expen_id)
    if expen_item is None:
        return None
    for field, value in request.model_dump().items():
        setattr(expen_item, field, value)
    expen_item.user_id = user_id
    commit_or_rollback(db)
    db.refresh(expen_item)
    return expen_item
