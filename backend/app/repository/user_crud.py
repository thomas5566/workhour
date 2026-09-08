from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Task, User, Workhour
from ..schemas import users
from .transaction import commit_or_rollback


def get_user(db: Session, user_id: int) -> User | None:
    statement = (
        select(User)
        .options(
            selectinload(User.department),
            selectinload(User.workhours)
            .selectinload(Workhour.task)
            .selectinload(Task.cstshops),
            selectinload(User.workhours)
            .selectinload(Workhour.user)
            .selectinload(User.department),
            selectinload(User.workhours).selectinload(Workhour.shop),
        )
        .where(User.id == user_id)
    )
    return db.scalar(statement)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_user_by_department(db: Session, department_id: int) -> list[User]:
    statement = (
        select(User)
        .options(selectinload(User.department))
        .where(User.department_id == department_id)
        .order_by(User.id)
    )
    return list(db.scalars(statement).all())


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[User]:
    statement = (
        select(User)
        .options(selectinload(User.department))
        .order_by(User.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_allusers_monthly(db: Session) -> list[User]:
    # The frontend expands each user and reads nested workhours/tasks. Loading
    # both relationships here avoids an N+1 query for every expanded row.
    statement = (
        select(User)
        .options(
            selectinload(User.department),
            selectinload(User.workhours).selectinload(Workhour.task),
        )
        .order_by(User.username, User.id)
    )
    return list(db.scalars(statement).all())


def create_user(
    db: Session,
    user_item: users.UserCreate,
    hashed_password: str,
    is_active: bool = True,
) -> User:
    db_user = User(
        username=user_item.username,
        fullname=user_item.fullname or "",
        password=hashed_password,
        department_id=user_item.department_id,
        is_active=is_active,
    )
    db.add(db_user)
    commit_or_rollback(db)
    db.refresh(db_user)
    return db_user


def create_admin_user(
    db: Session,
    user_item: users.UserAdminCreate,
    hashed_password: str,
) -> User:
    db_user = User(
        username=user_item.username,
        fullname=user_item.fullname or "",
        password=hashed_password,
        department_id=user_item.department_id,
        is_active=user_item.is_active,
        is_superuser=user_item.is_superuser,
        checklistAll_permission=user_item.checklistAll_permission,
    )
    db.add(db_user)
    commit_or_rollback(db)
    db.refresh(db_user)
    return db_user


def update_admin_user(
    db: Session,
    db_user: User,
    user_item: users.UserAdminUpdate,
    hashed_password: str | None,
) -> User:
    db_user.username = user_item.username
    db_user.fullname = user_item.fullname
    db_user.department_id = user_item.department_id
    db_user.is_active = user_item.is_active
    db_user.is_superuser = user_item.is_superuser
    db_user.checklistAll_permission = user_item.checklistAll_permission
    if hashed_password is not None:
        db_user.password = hashed_password
        db_user.auth_version = (db_user.auth_version or 0) + 1
    commit_or_rollback(db)
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: User) -> None:
    db.delete(db_user)
    commit_or_rollback(db)
