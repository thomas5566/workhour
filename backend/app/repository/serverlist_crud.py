from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import ServerList
from ..schemas import serverlist


def get_serverlists(db: Session, skip: int = 0):
    return db.query(ServerList).offset(skip).all()


def get_serverlist_by_id(db: Session, serverlist_id: int):
    return db.query(ServerList).filter(ServerList.id == serverlist_id).first()


def get_serverlists_by_branch_id(db: Session, branch_id, skip: int = 0):
    return db.query(ServerList).filter(ServerList.branch_id == branch_id).offset(skip).all()


def update_serverlist_by_id(serverlist_id: int, serverlist_items: serverlist.ServerListUpdate, db: Session):
    db_serverlist = db.query(ServerList).filter(
        ServerList.id == serverlist_id)

    if not db_serverlist.first():
        return 0
    # serverlist_items.__dict__.update(user_id=user_id)
    db_serverlist.update(serverlist_items.__dict__)
    db.commit()
    return 1

