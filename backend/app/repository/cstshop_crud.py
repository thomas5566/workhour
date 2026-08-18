from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import CstShop


def get_cstshops(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[CstShop]:
    statement = select(CstShop).order_by(CstShop.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())
