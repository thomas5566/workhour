from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import BranchList


def get_branchlists(db: Session, skip: int = 0, limit: int = 100):
    return db.query(BranchList).offset(skip).limit(limit).all()
