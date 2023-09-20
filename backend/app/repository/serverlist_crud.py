from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import ServerList


def get_serverlists(db: Session, skip: int = 0):
    return db.query(ServerList).offset(skip).all()


def get_serverlists_by_branch_id(db: Session, branch_id, skip: int = 0):
    return db.query(ServerList).filter(ServerList.branch_id == branch_id).offset(skip).all()
