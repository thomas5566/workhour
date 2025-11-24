from pydantic import BaseModel
import datetime

class TransactionsListBase(BaseModel):    
    id: int
    shop_id: int
    amount: str
    sale_id: str
    sale_amount: str
    pos_id: str
    canceled: str
    transaction_id : str
    service_amount: str
    discount_amount: str
    sale_deleted: str
    employee_username: str
    shipping_fee: str
    create_time: datetime.date
    update_time: datetime.date


class TransactionsList(TransactionsListBase):
    id: int

    class Config:
        orm_mode = True


class TransactionsListByShopId(BaseModel):
    id: int
    shop_id: int
    amount: str
    sale_id: str
    sale_amount: str
    pos_id: str
    canceled: str
    transaction_id : str
    service_amount: str
    discount_amount: str
    sale_deleted: str
    employee_username: str
    shipping_fee: str
    create_time: datetime.date
    update_time: datetime.date
    

    class Config:
        orm_mode = True


# class ServerListUpdate(BaseModel):
#     server_name: str
#     server_ip: str
#     server_location: str
#     server_acc: str
#     server_pass: str
#     server_remark: str
