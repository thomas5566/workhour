from pydantic import Field

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

class ServerListUpdate(BaseModel):
    # Match String(255) inventory columns before update data reaches SQLAlchemy.
    server_name: str = Field(max_length=255)
    server_ip: str = Field(max_length=255)
    server_location: str = Field(max_length=255)
    server_acc: str = Field(max_length=255)
    server_pass: str = Field(max_length=255)
    server_remark: str = Field(max_length=255)
