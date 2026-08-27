from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.credentials import encrypt_credential
from ..models import ServerList
from ..schemas import serverlist
from .transaction import commit_or_rollback


def get_serverlists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[ServerList]:
    # New inventory entries appear first in both the full and filtered lists.
    statement = select(ServerList).order_by(ServerList.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_serverlist_by_id(db: Session, serverlist_id: int) -> ServerList | None:
    return db.get(ServerList, serverlist_id)


def create_serverlist(
    db: Session,
    serverlist_items: serverlist.ServerListCreate,
) -> ServerList:
    values = serverlist_items.model_dump()
    values["server_pass"] = encrypt_credential(
        serverlist_items.server_pass.get_secret_value()
    )
    db_serverlist = ServerList(**values)
    db.add(db_serverlist)
    commit_or_rollback(db)
    db.refresh(db_serverlist)
    return db_serverlist


def delete_serverlist_by_id(db: Session, serverlist_id: int) -> bool:
    db_serverlist = db.get(ServerList, serverlist_id)
    if db_serverlist is None:
        return False
    db.delete(db_serverlist)
    commit_or_rollback(db)
    return True


def get_serverlists_by_branch_id(
    db: Session, branch_id: int, skip: int = 0, limit: int = 100
) -> list[ServerList]:
    statement = (
        select(ServerList)
        .where(ServerList.branch_id == branch_id)
        .order_by(ServerList.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def update_serverlist_by_id(
    serverlist_id: int,
    serverlist_items: serverlist.ServerListUpdate,
    db: Session,
) -> ServerList | None:
    db_serverlist = db.get(ServerList, serverlist_id)
    if db_serverlist is None:
        return None
    values = serverlist_items.model_dump(exclude_unset=True, exclude={"server_pass"})
    if serverlist_items.server_pass is not None:
        values["server_pass"] = encrypt_credential(
            serverlist_items.server_pass.get_secret_value()
        )
    for field, value in values.items():
        setattr(db_serverlist, field, value)
    commit_or_rollback(db)
    db.refresh(db_serverlist)
    return db_serverlist
