from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi_login import LoginManager
from sqlalchemy import select

from .core.config import settings
from .database import SessionLocal
from .models import User

# Keep every authentication failure standards-compliant and indistinguishable.
authentication_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
login_manager = LoginManager(
    settings.SECRET_KEY,
    "/api/user/login",
    algorithm=settings.ALGORITHM,
    not_authenticated_exception=authentication_error,
)


# fastapi-login 1.x exposes a decorator factory, so calling it is required to
# register this callback before any Bearer token can load its user.
@login_manager.user_loader()
def get_user(user_id: str) -> User | None:
    try:
        parsed_user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    with SessionLocal() as db:
        # Revoked users must stop authenticating even if their token is valid.
        return db.scalar(
            select(User).where(
                User.id == parsed_user_id,
                User.is_active.is_(True),
            )
        )


CurrentUser = Annotated[User, Depends(login_manager)]


def is_manager(user: User) -> bool:
    return bool(user.is_superuser or user.checklistAll_permission == 1)


def require_manager(user: CurrentUser) -> User:
    if is_manager(user):
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Manager permission required",
    )


ManagerUser = Annotated[User, Depends(require_manager)]


def ensure_owner_or_manager(user: User, owner_id: int) -> None:
    if user.id == owner_id or is_manager(user):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource",
    )
