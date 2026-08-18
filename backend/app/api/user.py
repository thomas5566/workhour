from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status

from ..auth import CurrentUser, ManagerUser, login_manager
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

    access_token = login_manager.create_access_token(
        data={"sub": str(user.id)},
        expires=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    user.token = access_token
    user.expiration = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
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
