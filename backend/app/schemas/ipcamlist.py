from pydantic import Field

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


class IpCamListUpdate(BaseModel):
    shop_id: int = Field(gt=0)
    # Keep device updates within the current String(255) database contract.
    shop_name: str = Field(max_length=255)
    ipcam_brand: str = Field(max_length=255)
    ipcam_ip: str = Field(max_length=255)
    admin_acc: str = Field(max_length=255)
    admin_pass: str = Field(max_length=255)
    user_acc: str = Field(max_length=255)
    user_pass: str = Field(max_length=255)
    phone_port: str = Field(max_length=255)
    http_port: str = Field(max_length=255)
    tcp_port: str = Field(max_length=255)
    remark: str = Field(max_length=255)
