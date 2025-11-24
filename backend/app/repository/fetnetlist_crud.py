from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import FetnetList
from ..schemas import fetnetlist


def get_fetnetlists(db: Session, skip: int = 0):
    return db.query(FetnetList).offset(skip).all()


def get_fetnetlist_by_id(db: Session, fetnetlist_id: int):
    return db.query(FetnetList).filter(FetnetList.id == fetnetlist_id).first()


def get_fetnetlists_by_branch_id(db: Session, branch_id, skip: int = 0):
    return db.query(FetnetList).filter(FetnetList.branch_id == branch_id).offset(skip).all()


def update_fetnetlist_by_id(fetnetlist_id: int, fetnetlist_items: fetnetlist.FetnetListUpdate, db: Session):
    db_fetnetlist = db.query(FetnetList).filter(
        FetnetList.id == fetnetlist_id)

    if not db_fetnetlist.first():
        return 0
    
    db_fetnetlist.update(fetnetlist_items.__dict__)
    db.commit()
    return 1

