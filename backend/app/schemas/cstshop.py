from pydantic import Field

from .base import BaseModel


class CstShop(BaseModel):
    """Customer shop response matching nullable legacy database columns."""

    id: int
    main_department_id: int | None = None
    shop_name: str | None = None
    shop_number: str | None = None


class CstShopWrite(BaseModel):
    main_department_id: int = Field(gt=0)
    shop_name: str = Field(min_length=1, max_length=255)
    shop_number: str = Field(min_length=1, max_length=255)
