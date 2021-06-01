from sqlalchemy.orm import Session
from sqlalchemy import text
from .. import models, schemas

def get_workhour(db: Session, workhour_id: int):
    return db.query(models.Workhour).filter(models.Workhour.id == workhour_id).first()


# def get_workhours(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Workhour).order_by(text("date desc")).offset(skip).limit(limit).all()
def get_workhours(db: Session, user_id: int):
    return db.query(models.Workhour).order_by(text("date desc")).filter(models.Workhour.user_id == user_id).all()


def get_workhours_by_user_id(db: Session, user_id, skip: int = 0, limit: int = 100):
    return db.query(models.Workhour).filter(models.Workhour.user_id == user_id).offset(skip).limit(limit).all()

# def get_totalworkhours_by_user_id(db: Session, skip: int = 0):
#     return db.query(func.sum(models.Workhour.hour)).offset(skip).first()


def get_workhours_by_task_id(db: Session, task_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Workhour).filter(models.Workhour.task_id == task_id).offset(skip).limit(limit).all()


def get_workhours_by_user_task(db: Session, user_id: int, task_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Workhour).filter(models.Workhour.user_id == user_id, models.Workhour.task_id == task_id).offset(skip).limit(limit).all()


def create_workhour(db: Session, workhour: schemas.WorkhourCreate):
    db_workhour = models.Workhour(
        user_id=workhour.user_id,
        task_id=workhour.task_id,
        date=workhour.date,
        hour=workhour.hour,
        description=workhour.description,
        is_overtime=workhour.is_overtime)
    db.add(db_workhour)
    db.commit()
    db.refresh(db_workhour)
    return db_workhour


def update_workhour(db: Session, workhour_id: int, workhour: schemas.WorkhourUpdate):
    db_workhour = db.query(models.Workhour).filter(
        models.Workhour.id == workhour_id).first()
    if db_workhour is None:
        return None
    for var, value in vars(workhour).items():
        setattr(db_workhour, var, value) if value else None
    db.add(db_workhour)
    db.commit()
    db.refresh(db_workhour)
    return db_workhour