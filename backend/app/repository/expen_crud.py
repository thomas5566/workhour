from sqlalchemy.orm import Session
from sqlalchemy import text, func
from fastapi import HTTPException, status
# from .. import models, schemas
from ..models import expen
from ..schemas import expens


def get_expen(db: Session, id: int):
    return db.query(expen.Expenditure).filter(
        expen.Expenditure.id == id).first()


def get_expens(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(expen.Expenditure).filter(
        expen.Expenditure.user_id == user_id).order_by(
            text("date desc")).offset(
            skip).limit(limit).all()


def get_expens_by_user_expentask(db: Session, user_id: int, expentask_id: int, skip: int = 0, limit: int = 100):
    return db.query(expen.Expenditure).filter(
        expen.Expenditure.user_id == user_id, 
        expen.Expenditure.expentask_id == expentask_id).offset(
            skip).limit(limit).all()


def get_expens_by_user_id(db: Session, user_id, skip: int = 0, limit: int = 100):
    return db.query(expen.Expenditure).filter(
        expen.Expenditure.user_id == user_id).order_by(text("date desc")).offset(
            skip).limit(limit).all()


def get_expens_by_expentask_id(db: Session, expentask_id: int, skip: int = 0, limit: int = 100):
    return db.query(expen.Expenditure).filter(
        expen.Expenditure.expentask_id == expentask_id).offset(
            skip).limit(limit).all()


def get_monthlyexpens_by_user_id(db: Session, user_id):
    qry = (db.query(
        func.to_char(expen.Expenditure.date, 'YYYY-MM').label('year_month'),
        func.sum(expen.Expenditure.price).label('total_pric')
    )
        .order_by(text("year_month desc"))
        .filter(expen.Expenditure.user_id == user_id)
        .group_by(
        func.to_char(expen.Expenditure.date, 'YYYY-MM').label('year_month')
    )
        .all()
    )
    print(qry)
    return qry


def create_expen(db: Session, expen_item: expens.ExpenditureCreate):
    db_expen = expen.Expenditure(
        user_id=expen_item.user_id,
        expentask_id=expen_item.expentask_id,
        date=expen_item.date,
        price=expen_item.price,
        description=expen_item.description,
    )
    db.add(db_expen)
    db.commit()
    db.refresh(db_expen)
    return db_expen


def delete_expen(id: int, db: Session):
    expen_item = db.query(expen.Expenditure).filter(expen.Expenditure.id == id)

    if not expen_item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Expen with id {id} not found")

    expen_item.delete(synchronize_session=False)
    db.commit()
    return "Expen hase being delete"


def update_expen(id: int, request: expens.Expenditure, db: Session):
    expen_item = db.query(expen.Expenditure).filter(
        expen.Expenditure.id == id)
    if not expen_item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Expen with id {id} not found")
    expen_item.update(request.dict())
    db.commit()
    return 'Data has being update!'
