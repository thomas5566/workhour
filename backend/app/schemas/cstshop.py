from .base import BaseModel


class CstShop(BaseModel):
    """Customer shop response matching nullable legacy database columns."""

    id: int
    main_department_id: int | None = None
    shop_name: str | None = None
    shop_number: str | None = None
