from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import CstShop


def get_cstshops(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CstShop).offset(skip).limit(limit).all()
