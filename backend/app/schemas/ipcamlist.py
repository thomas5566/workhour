from pydantic import Field, SecretStr, field_serializer

from ..core.credentials import mask_credential
from .base import BaseModel


class IpCamList(BaseModel):
    id: int
    shop_id: int | None = None
    shop_name: str | None = None
    ipcam_brand: str | None = None
    ipcam_ip: str | None = None
    admin_acc: str | None = None
    admin_pass: str | None = None
    user_acc: str | None = None
    user_pass: str | None = None
    phone_port: str | None = None
    http_port: str | None = None
    tcp_port: str | None = None
    remark: str | None = None

    @field_serializer("admin_pass", "user_pass")
    def serialize_password(self, value: str | None) -> str | None:
        return mask_credential(value)


class IpCamListCreate(BaseModel):
    shop_id: int = Field(gt=0)
    shop_name: str = Field(min_length=1, max_length=255)
    ipcam_brand: str = Field(default="", max_length=255)
    ipcam_ip: str = Field(default="", max_length=255)
    admin_acc: str = Field(default="", max_length=255)
    admin_pass: SecretStr | None = Field(default=None, max_length=255)
    user_acc: str = Field(default="", max_length=255)
    user_pass: SecretStr | None = Field(default=None, max_length=255)
    phone_port: str = Field(default="", max_length=255)
    http_port: str = Field(default="", max_length=255)
    tcp_port: str = Field(default="", max_length=255)
    remark: str = Field(default="", max_length=255)


class IpCamListUpdate(IpCamListCreate):
    # Omitted credentials preserve the encrypted values already in the database.
    admin_pass: SecretStr | None = Field(default=None, max_length=255)
    user_pass: SecretStr | None = Field(default=None, max_length=255)


class IpCamCredentialReveal(BaseModel):
    """Returned only from the explicit IT-authorized reveal endpoint."""

    admin_password: str | None = None
    user_password: str | None = None
