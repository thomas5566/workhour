from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.credentials import encrypt_credential
from ..models import IpCamList
from ..schemas import ipcamlist
from .transaction import commit_or_rollback


def get_ipcamlists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[IpCamList]:
    statement = select(IpCamList).order_by(IpCamList.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_ipcamlist_by_id(db: Session, ipcamlist_id: int) -> IpCamList | None:
    return db.get(IpCamList, ipcamlist_id)


def create_ipcamlist(db: Session, items: ipcamlist.IpCamListCreate) -> IpCamList:
    values = items.model_dump(exclude={"admin_pass", "user_pass"})
    values["admin_pass"] = encrypt_credential(
        items.admin_pass.get_secret_value() if items.admin_pass else None
    )
    values["user_pass"] = encrypt_credential(
        items.user_pass.get_secret_value() if items.user_pass else None
    )
    record = IpCamList(**values)
    db.add(record)
    commit_or_rollback(db)
    db.refresh(record)
    return record


def update_ipcamlist_by_id(
    ipcamlist_id: int,
    ipcamlist_items: ipcamlist.IpCamListUpdate,
    db: Session,
) -> IpCamList | None:
    db_ipcamlist = db.get(IpCamList, ipcamlist_id)
    if db_ipcamlist is None:
        return None
    values = ipcamlist_items.model_dump(
        exclude_unset=True,
        exclude={"admin_pass", "user_pass"},
    )
    if ipcamlist_items.admin_pass is not None:
        values["admin_pass"] = encrypt_credential(
            ipcamlist_items.admin_pass.get_secret_value()
        )
    if ipcamlist_items.user_pass is not None:
        values["user_pass"] = encrypt_credential(
            ipcamlist_items.user_pass.get_secret_value()
        )
    for field, value in values.items():
        setattr(db_ipcamlist, field, value)
    commit_or_rollback(db)
    db.refresh(db_ipcamlist)
    return db_ipcamlist
