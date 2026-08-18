import datetime

from pydantic import Field, SecretStr, field_validator

from ..core.hashing import BCRYPT_MAX_PASSWORD_BYTES
from .base import BaseModel
from .departments import Department


class TaskList(BaseModel):
    taskname: str | None = None


class WorkList(BaseModel):
    user_id: int | None = None
    task_id: int | None = None
    # Keep the legacy JSON key used by Vue while reading the renamed ORM field.
    date: datetime.date | None = Field(default=None, validation_alias="start_date")
    hour: float | None = None
    description: str | None = None
    overtime_hour: float | None = None
    task: TaskList | None = None


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    fullname: str | None = Field(default=None, max_length=255)
    password: SecretStr = Field(min_length=8)
    department_id: int = Field(gt=0)

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: SecretStr) -> SecretStr:
        # bcrypt limits encoded bytes, so character-count validation is insufficient.
        if len(value.get_secret_value().encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError("password must not exceed 72 UTF-8 bytes")
        return value


class User(BaseModel):
    id: int
    # Legacy rows can contain NULL values even though new writes are validated.
    username: str | None = None
    fullname: str | None = None
    is_superuser: bool = False
    checklistAll_permission: int = 0
    department_id: int | None = None
    department: Department | None = None


class UserToken(User):
    token: str
    expiration: datetime.datetime


class DataTotal(BaseModel):
    username: str | None = None
    department_id: int | None = None
    department: Department | None = None
    workhours: list[WorkList] = Field(default_factory=list)
