from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import FetnetList
from ..schemas import fetnetlist
from .transaction import commit_or_rollback


def get_fetnetlists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[FetnetList]:
    statement = select(FetnetList).order_by(FetnetList.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_fetnetlist_by_id(db: Session, fetnetlist_id: int) -> FetnetList | None:
    return db.get(FetnetList, fetnetlist_id)


def create_fetnetlist(db: Session, items: fetnetlist.FetnetListCreate) -> FetnetList:
    record = FetnetList(**items.model_dump())
    db.add(record)
    commit_or_rollback(db)
    db.refresh(record)
    return record


def get_fetnetlists_by_branch_id(
    db: Session, branch_id: int, skip: int = 0, limit: int = 100
) -> list[FetnetList]:
    statement = (
        select(FetnetList)
        .where(FetnetList.branch_id == branch_id)
        .order_by(FetnetList.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def update_fetnetlist_by_id(
    fetnetlist_id: int,
    fetnetlist_items: fetnetlist.FetnetListUpdate,
    db: Session,
) -> FetnetList | None:
    db_fetnetlist = db.get(FetnetList, fetnetlist_id)
    if db_fetnetlist is None:
        return None
    for field, value in fetnetlist_items.model_dump(exclude_unset=True).items():
        setattr(db_fetnetlist, field, value)
    commit_or_rollback(db)
    db.refresh(db_fetnetlist)
    return db_fetnetlist


def delete_fetnetlist_by_id(db: Session, fetnetlist_id: int) -> bool:
    record = db.get(FetnetList, fetnetlist_id)
    if record is None:
        return False
    db.delete(record)
    commit_or_rollback(db)
    return True
