from sqlalchemy.orm import Session
from fastapi import HTTPException, status
# from .. import models, schemas

from ..models import DaysOff
from ..schemas import daysoff


def get_daysoff_by_id(db: Session, daysoff_id: int):
    return db.query(DaysOff).filter(DaysOff.id == daysoff_id).first()


def get_daysoff_by_daysoffname(db: Session, daysoff_name: str):
    return db.query(DaysOff).filter(DaysOff.daysoff_name == daysoff_name).first()


def get_daysoff_lists(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DaysOff).offset(skip).limit(limit).all()


def create_daysoff(db: Session, daysoff_items: daysoff.DaysoffCreate):
    db_daysoff = DaysOff(
        user_id=daysoff_items.user_id,
        daysoff_name=daysoff_items.daysoff_name,
        daysoff_date=daysoff_items.daysoff_date,
        daysoff_hour=daysoff_items.daysoff_hour)
    db.add(db_daysoff)
    db.commit()
    db.refresh(db_daysoff)
    return db_daysoff


def update_daysoff(daysoff_id: int, daysoff_items: daysoff.DaysoffUpdate, db: Session,  user_id: int):
    db_daysoff = db.query(DaysOff).filter(
        DaysOff.id == daysoff_id)

    if not db_daysoff.first():
        return 0
    daysoff_items.__dict__.update(user_id=user_id)
    db_daysoff.update(daysoff_items.__dict__)
    db.commit()
    return 1


def delete_daysoff(id: int, db: Session):
    daysoff_items = db.query(DaysOff).filter(
        DaysOff.id == id)

    if not daysoff_items.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Daysoff with id {id} not found")

    daysoff_items.delete(synchronize_session=False)
    db.commit()
    return "Daysoff hase being delete"
