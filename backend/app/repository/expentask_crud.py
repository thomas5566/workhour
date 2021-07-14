from sqlalchemy.orm import Session
# from .. import models, schemas

from ..models import ExpenTask
from ..schemas import expentasks


def get_expentask(db: Session, expentask_id: int):
    return db.query(ExpenTask).filter(ExpenTask.id == expentask_id).first()


def get_expentask_by_expentaskname(db: Session, expentaskname: str):
    return db.query(ExpenTask).filter(ExpenTask.expentask_name == expentaskname).first()


def get_expentasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ExpenTask).offset(skip).limit(limit).all()


def create_expentask(db: Session, expentask_item: expentasks.ExpenTaskCreate):
    db_expentask = ExpenTask(
        expentask_name=expentask_item.expentask_name)
    db.add(db_expentask)
    db.commit()
    db.refresh(db_expentask)
    return db_expentask


def update_expentask(db: Session, expentask_id: int):
    db_expentask = db.query(ExpenTask).filter(
        ExpenTask.id == expentask_id).first()
    if db_expentask is None:
        return None
    for var, value in vars(db_expentask).items():
        setattr(db_expentask, var, value) if value else None
    db.add(db_expentask)
    db.commit()
    db.refresh(db_expentask)
    return db_expentask
