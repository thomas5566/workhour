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

class FetnetListUpdate(BaseModel):
    shop_id: int = Field(gt=0)
    # These limits mirror the existing String(255) database columns.
    shop_name: str = Field(max_length=255)
    shop_tax: str = Field(max_length=255)
    shop_location: str = Field(max_length=255)
    shop_phone_number: str = Field(max_length=255)
    shop_phone_short_code: str = Field(max_length=255)
    adsl_number: str = Field(max_length=255)
    fetnet_phone_number: str = Field(max_length=255)
    adsl_bank_number: str = Field(max_length=255)
    fetnetlist_remark: str = Field(max_length=255)
