from pydantic import Field

from .base import BaseModel


class FetnetList(BaseModel):
    id: int
    branch_id: int | None = None
    shop_id: int | None = None
    shop_name: str | None = None
    shop_tax: str | None = None
    shop_location: str | None = None
    shop_phone_number: str | None = None
    shop_phone_short_code: str | None = None
    adsl_number: str | None = None
    fetnet_phone_number: str | None = None
    adsl_bank_number: str | None = None
    fetnetlist_remark: str | None = None


class FetnetListCreate(BaseModel):
    # New entries select their location from cst_shop; branch_id is legacy.
    branch_id: int | None = Field(default=None, gt=0)
    shop_id: int = Field(gt=0)
    shop_name: str = Field(min_length=1, max_length=255)
    shop_tax: str = Field(default="", max_length=255)
    shop_location: str = Field(default="", max_length=255)
    shop_phone_number: str = Field(default="", max_length=255)
    shop_phone_short_code: str = Field(default="", max_length=255)
    adsl_number: str = Field(default="", max_length=255)
    fetnet_phone_number: str = Field(default="", max_length=255)
    adsl_bank_number: str = Field(default="", max_length=255)
    fetnetlist_remark: str = Field(default="", max_length=255)


class FetnetListUpdate(BaseModel):
    # branch_id is optional to preserve compatibility with existing clients.
    branch_id: int | None = Field(default=None, gt=0)
    shop_id: int = Field(gt=0)
    shop_name: str = Field(max_length=255)
    shop_tax: str = Field(max_length=255)
    shop_location: str = Field(max_length=255)
    shop_phone_number: str = Field(max_length=255)
    shop_phone_short_code: str = Field(max_length=255)
    adsl_number: str = Field(max_length=255)
    fetnet_phone_number: str = Field(max_length=255)
    adsl_bank_number: str = Field(max_length=255)
    fetnetlist_remark: str = Field(max_length=255)
