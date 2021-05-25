from sqlalchemy.orm import Session
from .. import models, schemas

def get_expentask(db: Session, expentask_id: int):
    return db.query(models.ExpenTask).filter(models.ExpenTask.id == expentask_id).first()


def get_expentask_by_expentaskname(db: Session, expentaskname: str):
    return db.query(models.ExpenTask).filter(models.ExpenTask.expentask_name == expentaskname).first()


def get_expentasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ExpenTask).offset(skip).limit(limit).all()


def create_expentask(db: Session, expentask: schemas.ExpenTaskCreate):
    db_expentask = models.ExpenTask(
        expentaskname=expentask.expentask_name)
    db.add(db_expentask)
    db.commit()
    db.refresh(db_expentask)
    return db_expentask


def update_expentask(db: Session, expentask_id: int, expentask: schemas.ExpenTaskUpdate):
    db_expentask = db.query(models.ExpenTask).filter(
        models.ExpenTask.id == expentask_id).first()
    if db_expentask is None:
        return None
    for var, value in vars(db_expentask).items():
        setattr(db_expentask, var, value) if value else None
    db.add(db_expentask)
    db.commit()
    db.refresh(db_expentask)
    return db_expentask
