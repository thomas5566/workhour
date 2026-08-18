from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import BranchList


def get_branchlists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[BranchList]:
    statement = select(BranchList).order_by(BranchList.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())
