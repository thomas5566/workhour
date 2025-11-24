from pydantic import BaseModel


class IpCamListBase(BaseModel):
    id: int
    shop_id: int
    shop_name: str
    ipcam_brand: str
    ipcam_ip: str
    admin_acc: str
    admin_pass: str
    user_acc: str
    user_pass: str
    phone_port: str
    http_port: str
    tcp_port: str
    remark: str


class IpCamList(IpCamListBase):
    id: int

    class Config:
        orm_mode = True


class IpCamListUpdate(BaseModel):
    shop_id: int
    shop_name: str
    ipcam_brand: str
    ipcam_ip: str
    admin_acc: str
    admin_pass: str
    user_acc: str
    user_pass: str
    phone_port: str
    http_port: str
    tcp_port: str
    remark: str
    