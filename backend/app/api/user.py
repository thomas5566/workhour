from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status

from ..auth import CurrentUser, ManagerUser, is_manager, login_manager
from ..core.config import settings
from ..core.hashing import DUMMY_PASSWORD_HASH, Hasher
from ..repository import department_crud, user_crud
from ..schemas import allfull, departments, users
from .dependencies import (
    DatabaseSession,
    LoginForm,
    PageLimit,
    PageOffset,
    PositivePathId,
)

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


def _create_user_account(
    user_item: users.UserCreate,
    db: DatabaseSession,
):
    """Create a regular account for both managed and self-registration flows."""
    db_user = user_crud.get_user_by_username(db, username=user_item.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    hashed_password = Hasher.get_password_hash(
        user_item.password.get_secret_value()
    )
    return user_crud.create_user(
        db=db,
        user_item=user_item,
        hashed_password=hashed_password,
    )


@router.get(
    "/registration-departments",
    response_model=list[departments.Department],
)
def read_registration_departments(db: DatabaseSession):
    # Expose only department identifiers/names required by self-registration.
    return department_crud.get_departments(db)


@router.post(
    "/register",
    response_model=users.User,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_item: users.UserCreate, db: DatabaseSession):
    # UserCreate has no role fields; public callers cannot grant privileges.
    return _create_user_account(user_item, db)


@router.post("/", response_model=users.User)
def create_user(
    user_item: users.UserCreate,
    db: DatabaseSession,
    manager: ManagerUser,
):
    # Bootstrap administrators are provisioned outside the public API, so
    # account creation can stay manager-only without a registration backdoor.
    return _create_user_account(user_item, db)


@router.get("/", response_model=list[users.User])
def get_users(
    db: DatabaseSession,
    manager: ManagerUser,
    skip: PageOffset = 0,
    limit: PageLimit = 100,
):
    return user_crud.get_users(db, skip=skip, limit=limit)


@router.get("/users-alldata", response_model=list[users.DataTotal])
def get_users_worklists_by_month(
    db: DatabaseSession,
    manager: ManagerUser,
):
    return user_crud.get_allusers_monthly(db)


@router.get("/get-dpuser", response_model=list[users.User])
def get_user_bydp(
    db: DatabaseSession,
    manager: ManagerUser,
):
    return user_crud.get_user_by_department(db, manager.department_id)


def _validate_user_department(db: DatabaseSession, department_id: int) -> None:
    if department_crud.get_department_by_id(db, department_id) is None:
        raise HTTPException(status_code=422, detail="Department does not exist")


@router.post(
    "/admin",
    response_model=users.User,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_user(
    user_item: users.UserAdminCreate,
    db: DatabaseSession,
    manager: ManagerUser,
):
    if user_crud.get_user_by_username(db, user_item.username):
        raise HTTPException(status_code=409, detail="Username already registered")
    _validate_user_department(db, user_item.department_id)
    password_hash = Hasher.get_password_hash(user_item.password.get_secret_value())
    return user_crud.create_admin_user(db, user_item, password_hash)


@router.put("/admin/{user_id}", response_model=users.User)
def admin_update_user(
    user_id: PositivePathId,
    user_item: users.UserAdminUpdate,
    db: DatabaseSession,
    manager: ManagerUser,
):
    db_user = user_crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    duplicate = user_crud.get_user_by_username(db, user_item.username)
    if duplicate is not None and duplicate.id != user_id:
        raise HTTPException(status_code=409, detail="Username already registered")
    _validate_user_department(db, user_item.department_id)
    password_hash = (
        Hasher.get_password_hash(user_item.password.get_secret_value())
        if user_item.password is not None
        else None
    )
    return user_crud.update_admin_user(db, db_user, user_item, password_hash)


@router.delete("/admin/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: PositivePathId,
    db: DatabaseSession,
    manager: ManagerUser,
) -> None:
    if manager.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    db_user = user_crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_crud.delete_user(db, db_user)


@router.get("/my", response_model=allfull.UserFull)
def read_user_my(
    db: DatabaseSession,
    user: CurrentUser,
):
    return user_crud.get_user(db, user_id=user.id)


@router.post("/login", response_model=users.UserToken)
def login(data: LoginForm, db: DatabaseSession, response: Response):
    user = user_crud.get_user_by_username(db, username=data.username)
    # Always verify a hash, even for an unknown account, so username probing
    # cannot rely on a noticeably faster missing-user response.
    stored_hash = user.password if user else DUMMY_PASSWORD_HASH
    password_is_valid = Hasher.verify_password(data.password, stored_hash)
    if not user or not password_is_valid or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Manager dashboards remain authenticated for four hours, while regular
    # accounts keep the shorter configured session lifetime.
    token_lifetime_minutes = (
        settings.MANAGER_ACCESS_TOKEN_EXPIRE_MINUTES
        if is_manager(user)
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = login_manager.create_access_token(
        data={"sub": str(user.id)},
        expires=timedelta(minutes=token_lifetime_minutes),
    )
    user.token = access_token
    user.expiration = datetime.now(UTC) + timedelta(
        minutes=token_lifetime_minutes
    )
    # Bearer tokens must never be retained by browser or intermediary caches.
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return user


@router.get("/{user_id}", response_model=allfull.UserFull)
def read_user(
    user_id: PositivePathId,
    db: DatabaseSession,
    manager: ManagerUser,
):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return db_user
