from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import BranchList
from ..schemas.branch_list import BranchListWrite
from .transaction import commit_or_rollback


def get_branchlists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[BranchList]:
    statement = select(BranchList).order_by(BranchList.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_branchlist_by_id(db: Session, branch_id: int) -> BranchList | None:
    return db.get(BranchList, branch_id)


def create_branchlist(db: Session, payload: BranchListWrite) -> BranchList:
    record = BranchList(**payload.model_dump())
    db.add(record)
    commit_or_rollback(db)
    db.refresh(record)
    return record


def update_branchlist(db: Session, record: BranchList, payload: BranchListWrite) -> BranchList:
    for field, value in payload.model_dump().items():
        setattr(record, field, value)
    commit_or_rollback(db)
    db.refresh(record)
    return record


def delete_branchlist(db: Session, record: BranchList) -> None:
    db.delete(record)
    commit_or_rollback(db)
