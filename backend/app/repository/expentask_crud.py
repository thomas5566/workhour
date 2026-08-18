from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Expenditure, ExpenTask, User
from ..schemas import expentasks
from .transaction import commit_or_rollback


def get_expentask(db: Session, expentask_id: int) -> ExpenTask | None:
    statement = (
        select(ExpenTask)
        .options(
            selectinload(ExpenTask.expens)
            .selectinload(Expenditure.user)
            .selectinload(User.department),
            selectinload(ExpenTask.expens).selectinload(Expenditure.expentask),
        )
        .where(ExpenTask.id == expentask_id)
    )
    return db.scalar(statement)


def get_expentask_by_expentaskname(
    db: Session,
    expentaskname: str,
) -> ExpenTask | None:
    statement = select(ExpenTask).where(
        ExpenTask.expentask_name == expentaskname
    )
    return db.scalar(statement)


def get_expentasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[ExpenTask]:
    statement = select(ExpenTask).order_by(ExpenTask.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def create_expentask(
    db: Session,
    expentask_item: expentasks.ExpenTaskCreate,
) -> ExpenTask:
    db_expentask = ExpenTask(expentask_name=expentask_item.expentask_name)
    db.add(db_expentask)
    commit_or_rollback(db)
    db.refresh(db_expentask)
    return db_expentask


def update_expentask(
    db: Session,
    expentask_id: int,
    expentask_items: expentasks.ExpenTaskUpdate,
) -> ExpenTask | None:
    db_expentask = db.get(ExpenTask, expentask_id)
    if db_expentask is None:
        return None
    for field, value in expentask_items.model_dump().items():
        setattr(db_expentask, field, value)
    commit_or_rollback(db)
    db.refresh(db_expentask)
    return db_expentask
