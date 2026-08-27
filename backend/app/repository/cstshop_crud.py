from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import CstShop
from ..schemas.cstshop import CstShopWrite
from .transaction import commit_or_rollback


def get_cstshops(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    main_department_id: int | None = None,
) -> list[CstShop]:
    statement = select(CstShop)
    if main_department_id is not None:
        statement = statement.where(CstShop.main_department_id == main_department_id)
    statement = statement.order_by(CstShop.shop_number, CstShop.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_cstshop_by_id(db: Session, shop_id: int) -> CstShop | None:
    return db.get(CstShop, shop_id)


def create_cstshop(db: Session, payload: CstShopWrite) -> CstShop:
    record = CstShop(**payload.model_dump())
    db.add(record)
    commit_or_rollback(db)
    db.refresh(record)
    return record


def update_cstshop(db: Session, record: CstShop, payload: CstShopWrite) -> CstShop:
    for field, value in payload.model_dump().items():
        setattr(record, field, value)
    commit_or_rollback(db)
    db.refresh(record)
    return record


def delete_cstshop(db: Session, record: CstShop) -> None:
    db.delete(record)
    commit_or_rollback(db)
