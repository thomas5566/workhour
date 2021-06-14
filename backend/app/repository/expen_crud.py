from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
from .. import models, schemas


def get_expen(db: Session, id: int):
    return db.query(models.Expenditure).filter(models.Expenditure.id == id).first()


def get_expens(db: Session, user_id: int):
    return db.query(models.Expenditure).filter(models.Expenditure.user_id == user_id).order_by(text("date desc")).all()


def get_expens_by_user_expentask(db: Session, user_id: int, expentask_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Expenditure).filter(models.Expenditure.user_id == user_id, models.Expenditure.expentask_id == expentask_id).offset(skip).limit(limit).all()


def get_expens_by_user_id(db: Session, user_id, skip: int = 0, limit: int = 100):
    return db.query(models.Expenditure).filter(models.Expenditure.user_id == user_id).offset(skip).limit(limit).all()


def get_expens_by_expentask_id(db: Session, expentask_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Expenditure).filter(models.Expenditure.expentask_id == expentask_id).offset(skip).limit(limit).all()


def create_expen(db: Session, expen: schemas.ExpenditureCreate):
    db_expen = models.Expenditure(
        user_id=expen.user_id,
        expentask_id=expen.expentask_id,
        date=expen.date,
        price=expen.price,
        description=expen.description,
    )
    db.add(db_expen)
    db.commit()
    db.refresh(db_expen)
    return db_expen


def delete_expen(id: int, db: Session):
    expen = db.query(models.Expenditure).filter(models.Expenditure.id == id)

    if not expen.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Expen with id {id} not found")

    expen.delete(synchronize_session=False)
    db.commit()
    return "Expen hase being delete"


def update_expen(id: int, request: schemas.Expenditure, db: Session):
    expen = db.query(models.Expenditure).filter(
        models.Expenditure.id == id)
    if not expen.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Expen with id {id} not found")
    expen.update(request.dict())
    db.commit()
    return 'Data has being update!'
