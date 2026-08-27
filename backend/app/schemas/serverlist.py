from pydantic import Field, SecretStr, field_serializer

from ..core.credentials import mask_credential
from .base import BaseModel


class ServerList(BaseModel):
    id: int
    branch_id: int | None = None
    server_name: str | None = None
    server_ip: str | None = None
    server_location: str | None = None
    server_acc: str | None = None
    server_pass: str | None = None
    server_remark: str | None = None

    @field_serializer("server_pass")
    def serialize_password(self, value: str | None) -> str | None:
        return mask_credential(value)


class ServerListCreate(BaseModel):
    branch_id: int = Field(gt=0)
    server_name: str = Field(min_length=1, max_length=255)
    server_ip: str = Field(min_length=1, max_length=255)
    server_location: str = Field(min_length=1, max_length=255)
    server_acc: str = Field(min_length=1, max_length=255)
    server_pass: SecretStr = Field(min_length=1, max_length=255)
    server_remark: str = Field(default="", max_length=255)


class ServerListUpdate(BaseModel):
    # Match String(255) inventory columns before update data reaches SQLAlchemy.
    branch_id: int | None = Field(default=None, gt=0)
    server_name: str = Field(max_length=255)
    server_ip: str = Field(max_length=255)
    server_location: str = Field(max_length=255)
    server_acc: str = Field(max_length=255)
    # Empty/omitted password means keep the stored encrypted credential.
    server_pass: SecretStr | None = Field(default=None, min_length=1, max_length=255)
    server_remark: str = Field(max_length=255)


class ServerCredentialReveal(BaseModel):
    """Returned only from the explicit manager-only reveal endpoint."""

    password: str | None = None
