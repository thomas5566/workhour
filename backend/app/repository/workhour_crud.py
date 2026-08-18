from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..models import CstShop, Task, User, Workhour
from ..schemas import workhours
from .transaction import commit_or_rollback

WORKHOUR_RESPONSE_OPTIONS = (
    selectinload(Workhour.user).selectinload(User.department),
    selectinload(Workhour.task).selectinload(Task.cstshops),
    selectinload(Workhour.shop),
)


def get_workhour(db: Session, workhour_id: int) -> Workhour | None:
    statement = (
        select(Workhour)
        .options(*WORKHOUR_RESPONSE_OPTIONS)
        .where(Workhour.id == workhour_id, Workhour.active.is_(True))
        .order_by(Workhour.start_date.desc(), Workhour.id.desc())
    )
    return db.scalar(statement)


def get_workhours(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Workhour]:
    statement = (
        select(Workhour)
        .options(*WORKHOUR_RESPONSE_OPTIONS)
        .where(Workhour.user_id == user_id, Workhour.active.is_(True))
        .order_by(Workhour.start_date.desc(), Workhour.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_all_workhours(
    db: Session,
    skip: int = 0,
    limit: int = 1000,
) -> list[Workhour]:
    statement = (
        select(Workhour)
        .options(*WORKHOUR_RESPONSE_OPTIONS)
        .where(Workhour.active.is_(True))
        .order_by(Workhour.start_date.desc(), Workhour.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_worklist_by_yearmonth(db: Session):
    year_month = func.date_trunc("month", Workhour.start_date).label("year_month")
    statement = (
        select(year_month, func.count(Workhour.id).label("total_events"))
        .where(Workhour.active.is_(True))
        .group_by(year_month)
        .order_by(year_month.asc())
    )
    return db.execute(statement).all()


def get_worklist_by_userid(db: Session):
    statement = (
        select(
            Workhour.user_id,
            func.count(Workhour.id).label("total_events"),
            User.username,
            User.fullname,
        )
        .join(User, Workhour.user_id == User.id)
        .where(Workhour.active.is_(True))
        .group_by(Workhour.user_id, User.username, User.fullname)
    )
    return db.execute(statement).all()


def get_worklist_by_shopid(db: Session):
    statement = (
        select(
            Workhour.shop_id,
            func.count(Workhour.id).label("total_events"),
            CstShop.shop_name,
        )
        .join(CstShop, CstShop.id == Workhour.shop_id)
        .where(Workhour.active.is_(True))
        .group_by(Workhour.shop_id, CstShop.shop_name)
    )
    return db.execute(statement).all()


def get_workhours_by_user_id(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Workhour]:
    return get_workhours(db, user_id, skip, limit)


def get_monthlyworkhours_by_user_id(db: Session, user_id: int):
    year_month = func.to_char(Workhour.start_date, "YYYY-MM").label("year_month")
    statement = (
        select(
            year_month,
            func.sum(Workhour.hour).label("total_hour"),
            func.sum(Workhour.overtime_hour).label("total_overtime_hour"),
        )
        .where(Workhour.user_id == user_id, Workhour.active.is_(True))
        .group_by(year_month)
        .order_by(year_month.desc())
    )
    return db.execute(statement).all()


def create_workhour(
    db: Session,
    workhour_items: workhours.WorkhourCreate,
    user_id: int,
) -> Workhour:
    db_workhour = Workhour(
        **workhour_items.model_dump(),
        user_id=user_id,
    )
    db.add(db_workhour)
    commit_or_rollback(db)
    db.refresh(db_workhour)
    return db_workhour


def update_workhour(
    workhour_id: int,
    workhour_items: workhours.WorkhourUpdate,
    db: Session,
    user_id: int,
) -> Workhour | None:
    db_workhour = get_workhour(db, workhour_id)
    if db_workhour is None:
        return None

    for field, value in workhour_items.model_dump(exclude={"user_id"}).items():
        setattr(db_workhour, field, value)
    db_workhour.user_id = user_id
    commit_or_rollback(db)
    db.refresh(db_workhour)
    return db_workhour


def delete_workhour(workhour_id: int, db: Session) -> bool:
    workhour_item = get_workhour(db, workhour_id)
    if workhour_item is None:
        return False

    db.delete(workhour_item)
    commit_or_rollback(db)
    return True
