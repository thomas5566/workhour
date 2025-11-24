from pydantic import BaseModel


class FetnetListBase(BaseModel):
    id: int
    branch_id: int
    shop_id: int
    shop_name: str
    shop_tax: str
    shop_location: str
    shop_phone_number: str
    shop_phone_short_code: str
    adsl_number: str
    fetnet_phone_number: str
    adsl_bank_number: str
    fetnetlist_remark: str


class FetnetList(FetnetListBase):
    id: int

    class Config:
        orm_mode = True


class FetnetListByBranchId(BaseModel):
    id: int
    branch_id: int
    shop_id: int
    shop_name: str
    shop_tax: str
    shop_location: str
    shop_phone_number: str
    shop_phone_short_code: str
    adsl_number: str
    fetnet_phone_number: str
    adsl_bank_number: str
    fetnetlist_remark: str

    class Config:
        orm_mode = True


class FetnetListUpdate(BaseModel):
    shop_id: int
    shop_name: str
    shop_tax: str
    shop_location: str
    shop_phone_number: str
    shop_phone_short_code: str
    adsl_number: str
    fetnet_phone_number: str
    adsl_bank_number: str
    fetnetlist_remark: str
