from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ServerList
from ..schemas import serverlist
from .transaction import commit_or_rollback


def get_serverlists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[ServerList]:
    statement = select(ServerList).order_by(ServerList.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_serverlist_by_id(db: Session, serverlist_id: int) -> ServerList | None:
    return db.get(ServerList, serverlist_id)


def get_serverlists_by_branch_id(
    db: Session, branch_id: int, skip: int = 0, limit: int = 100
) -> list[ServerList]:
    statement = (
        select(ServerList)
        .where(ServerList.branch_id == branch_id)
        .order_by(ServerList.id)
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
    for field, value in serverlist_items.model_dump().items():
        setattr(db_serverlist, field, value)
    commit_or_rollback(db)
    db.refresh(db_serverlist)
    return db_serverlist
