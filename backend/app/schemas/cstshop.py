from pydantic import BaseModel


class CstShpoBase(BaseModel):
    id: int
    main_department_id:int    
    shop_name: str
    shop_number: str


class CstShpoCreate(CstShpoBase):
    pass


class CstShpoUpdate(CstShpoBase):
    pass


class CstShpo(CstShpoBase):
    id: int

    class Config:
        orm_mode = True

