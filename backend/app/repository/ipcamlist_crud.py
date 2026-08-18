from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import IpCamList
from ..schemas import ipcamlist
from .transaction import commit_or_rollback


def get_ipcamlists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[IpCamList]:
    statement = select(IpCamList).order_by(IpCamList.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_ipcamlist_by_id(db: Session, ipcamlist_id: int) -> IpCamList | None:
    return db.get(IpCamList, ipcamlist_id)


def update_ipcamlist_by_id(
    ipcamlist_id: int,
    ipcamlist_items: ipcamlist.IpCamListUpdate,
    db: Session,
) -> IpCamList | None:
    db_ipcamlist = db.get(IpCamList, ipcamlist_id)
    if db_ipcamlist is None:
        return None
    for field, value in ipcamlist_items.model_dump().items():
        setattr(db_ipcamlist, field, value)
    commit_or_rollback(db)
    db.refresh(db_ipcamlist)
    return db_ipcamlist
