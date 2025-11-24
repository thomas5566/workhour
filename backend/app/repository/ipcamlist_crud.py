from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import IpCamList
from ..schemas import ipcamlist


def get_ipcamlists(db: Session, skip: int = 0):
    return db.query(IpCamList).offset(skip).all()


def get_ipcamlist_by_id(db: Session, ipcamlist_id: int):
    return db.query(IpCamList).filter(IpCamList.id == ipcamlist_id).first()


def update_ipcamlist_by_id(ipcamlist_id: int, ipcamlist_items: ipcamlist.IpCamListUpdate, db: Session):
    db_ipcamlist = db.query(IpCamList).filter(
        IpCamList.id == ipcamlist_id)

    if not db_ipcamlist.first():
        return 0
    
    db_ipcamlist.update(ipcamlist_items.__dict__)
    db.commit()
    return 1

